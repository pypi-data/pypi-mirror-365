import sys
import os
import asyncio
import json
import base64
import re
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from math import radians, sin, cos, asin, sqrt
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import aiohttp
import aiofiles

from .ui import ConsoleManager

NORD_API_BASE_URL = "https://api.nordvpn.com/v1"
LOCATION_API_URL = "https://ipinfo.io/json"
CONCURRENT_LIMIT = 200

@dataclass
class Server:
    name: str
    hostname: str
    station: str
    load: int
    country: str
    city: str
    latitude: float
    longitude: float
    public_key: str
    distance: float = 0.0

@dataclass
class UserPreferences:
    dns: str = "103.86.96.100"
    use_ip_for_endpoint: bool = False
    persistent_keepalive: int = 25

    def update_from_input(self, user_input: dict):
        dns_input = user_input.get("dns")
        if dns_input and re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', dns_input):
            self.dns = dns_input

        self.use_ip_for_endpoint = user_input.get("endpoint_type", "").lower() == 'y'

        keepalive_input = user_input.get("keepalive")
        if keepalive_input and keepalive_input.isdigit() and 15 <= int(keepalive_input) <= 120:
            self.persistent_keepalive = int(keepalive_input)

class NordVpnApiClient:
    def __init__(self, console_manager: ConsoleManager):
        self._session = aiohttp.ClientSession()
        self._console = console_manager

    async def _get(self, url: str, **kwargs) -> Optional[Any]:
        try:
            async with self._session.get(url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            self._console.print_message("error", f"API request failed for {url}: {e}")
            return None

    async def get_private_key(self, token: str) -> Optional[str]:
        auth_header = base64.b64encode(f'token:{token}'.encode()).decode()
        url = f"{NORD_API_BASE_URL}/users/services/credentials"
        data = await self._get(url, headers={'Authorization': f'Basic {auth_header}'})
        if isinstance(data, dict):
            return data.get('nordlynx_private_key')
        return None

    async def get_all_servers(self) -> List[Dict[str, Any]]:
        url = f"{NORD_API_BASE_URL}/servers"
        params = {'limit': 9000, 'filters[servers_technologies][identifier]': 'wireguard_udp'}
        data = await self._get(url, params=params)
        if isinstance(data, list):
            return data
        return []

    async def get_user_geolocation(self) -> Optional[Tuple[float, float]]:
        data = await self._get(LOCATION_API_URL)
        if not isinstance(data, dict):
            return None
        try:
            lat, lon = data.get('loc', '').split(',')
            return float(lat), float(lon)
        except (ValueError, IndexError):
            self._console.print_message("error", "Could not parse location data.")
            return None

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

class ConfigurationOrchestrator:
    def __init__(self, private_key: str, preferences: UserPreferences, console_manager: ConsoleManager, api_client: NordVpnApiClient):
        self._api_client = api_client
        self._private_key = private_key
        self._preferences = preferences
        self._console = console_manager
        self._output_dir = Path(f'nordvpn_configs_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        self._semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
        self._thread_pool = ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) + 4))
        self.generation_succeeded = False
        self.stats = {"total": 0, "best": 0}

    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        lon1_rad, lat1_rad, lon2_rad, lat2_rad = map(radians, [lon1, lat1, lon2, lat2])
        a = sin((lat2_rad - lat1_rad) / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin((lon2_rad - lon1_rad) / 2)**2
        return 2 * asin(sqrt(a)) * 6371

    def _parse_server_data(self, server_data: Dict[str, Any], user_location: Tuple[float, float]) -> Optional[Server]:
        try:
            location = server_data['locations'][0]
            public_key = next(
                tech_meta['value']
                for tech in server_data['technologies'] if tech['identifier'] == 'wireguard_udp'
                for tech_meta in tech['metadata'] if tech_meta['name'] == 'public_key'
            )
            return Server(
                name=server_data['name'], hostname=server_data['hostname'], station=server_data['station'],
                load=int(server_data.get('load', 0)), country=location['country']['name'],
                city=location['country'].get('city', {}).get('name', 'Unknown'), latitude=location['latitude'],
                longitude=location['longitude'], public_key=public_key,
                distance=self._calculate_distance(user_location[0], user_location[1], location['latitude'], location['longitude'])
            )
        except (KeyError, IndexError, StopIteration):
            return None

    def _generate_wireguard_config_string(self, server: Server) -> str:
        endpoint = server.station if self._preferences.use_ip_for_endpoint else server.hostname
        return f"[Interface]\nPrivateKey = {self._private_key}\nAddress = 10.5.0.2/16\nDNS = {self._preferences.dns}\n\n[Peer]\nPublicKey = {server.public_key}\nAllowedIPs = 0.0.0.0/0, ::/0\nEndpoint = {endpoint}:51820\nPersistentKeepalive = {self._preferences.persistent_keepalive}"

    @staticmethod
    def _sanitize_path_part(part: str) -> str:
        return re.sub(r'[<>:"/\\|?*\0]', '', part.lower().replace(' ', '_')).replace('#', '')

    async def _save_config_file(self, config_string: str, path: Path, filename: str, progress, task):
        path.mkdir(parents=True, exist_ok=True)
        async with self._semaphore:
            async with aiofiles.open(path / filename, 'w') as f:
                await f.write(config_string)
        progress.update(task, advance=1)

    async def generate(self) -> Optional[Path]:
        progress = self._console.create_progress_bar()
        with progress:
            task_data = progress.add_task("Fetching remote data...", total=2)
            
            progress.update(task_data, description="Fetching user location...")
            user_location, all_servers_data = await asyncio.gather(
                self._api_client.get_user_geolocation(),
                self._api_client.get_all_servers()
            )
            
            if not user_location or not all_servers_data:
                return None
            
            progress.update(task_data, advance=2, description="Processing servers...")

            loop = asyncio.get_running_loop()
            parse_func = partial(self._parse_server_data, user_location=user_location)
            parse_tasks = [loop.run_in_executor(self._thread_pool, parse_func, s) for s in all_servers_data]
            
            processed_servers = [server for server in await asyncio.gather(*parse_tasks) if server]
            self._thread_pool.shutdown(wait=False, cancel_futures=True)

        sorted_servers = sorted(processed_servers, key=lambda s: (s.load, s.distance))
        
        self._output_dir.mkdir(exist_ok=True)
        servers_info, best_servers_by_location = {}, {}
        
        config_progress = self._console.create_progress_bar(transient=False)
        with config_progress:
            total_configs = len(sorted_servers)
            best_configs = 0
            
            save_tasks = []
            task_save_all = config_progress.add_task("Generating configs...", total=total_configs)
            for server in sorted_servers:
                country_sanitized = self._sanitize_path_part(server.country)
                city_sanitized = self._sanitize_path_part(server.city)
                config_str = self._generate_wireguard_config_string(server)
                path = self._output_dir / 'configs' / country_sanitized / city_sanitized
                filename = f"{self._sanitize_path_part(server.name)}.conf"
                save_tasks.append(self._save_config_file(config_str, path, filename, config_progress, task_save_all))
                
                location_key = (server.country, server.city)
                if location_key not in best_servers_by_location or server.load < best_servers_by_location[location_key].load:
                    best_servers_by_location[location_key] = server
                
                country_info = servers_info.setdefault(server.country, {})
                city_info = country_info.setdefault(server.city, {"distance": int(server.distance), "servers": []})
                city_info["servers"].append((server.name, server.load))

            self.stats["total"] = total_configs
            await asyncio.gather(*save_tasks)

            best_save_tasks = []
            best_configs = len(best_servers_by_location)
            task_save_best = config_progress.add_task("Generating optimized configs...", total=best_configs)
            for server in best_servers_by_location.values():
                country_sanitized = self._sanitize_path_part(server.country)
                city_sanitized = self._sanitize_path_part(server.city)
                config_str = self._generate_wireguard_config_string(server)
                path = self._output_dir / 'best_configs' / country_sanitized / city_sanitized
                filename = f"{self._sanitize_path_part(server.name)}.conf"
                best_save_tasks.append(self._save_config_file(config_str, path, filename, config_progress, task_save_best))
            
            self.stats["best"] = best_configs
            await asyncio.gather(*best_save_tasks)
            
            async with aiofiles.open(self._output_dir / 'servers.json', 'w') as f:
                await f.write(json.dumps(servers_info, indent=2, separators=(',', ':'), ensure_ascii=False))
        
        self.generation_succeeded = True
        return self._output_dir

def is_valid_token_format(token: str) -> bool:
    return bool(re.match(r'^[a-fA-F0-9]{64}$', token))

async def main_async():
    console = ConsoleManager()
    api_client = NordVpnApiClient(console)

    try:
        console.clear()
        console.print_title()

        token = console.get_user_input("Please enter your NordVPN access token: ", is_secret=True)
        if not is_valid_token_format(token):
            console.print_message("error", "Invalid token format.")
            return

        private_key = None
        with console.create_progress_bar() as progress:
            task = progress.add_task("Validating token...", total=1)
            private_key = await api_client.get_private_key(token)
            progress.update(task, advance=1)
        
        if not private_key:
            console.print_message("error", "Token is invalid or could not be verified. Please check the token and try again.")
            return

        console.print_message("success", "Token validated successfully.")
        
        preferences = UserPreferences()
        user_input = console.get_preferences(preferences)
        preferences.update_from_input(user_input)
        
        console.clear()
        
        start_time = time.time()
        orchestrator = ConfigurationOrchestrator(private_key, preferences, console, api_client)
        
        output_directory = await orchestrator.generate()
        elapsed_time = time.time() - start_time
        
        if orchestrator.generation_succeeded and output_directory:
            console.print_summary(output_directory, orchestrator.stats["total"], orchestrator.stats["best"], elapsed_time)
        else:
            console.print_message("error", "Process failed. Check the logs for details.")
            
    except Exception as e:
        console.print_message("error", f"An unrecoverable error occurred: {e}")
    finally:
        await api_client.close()

def cli_entry_point():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")

if __name__ == "__main__":
    cli_entry_point()
