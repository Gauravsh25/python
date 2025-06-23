#!/usr/bin/env python3
"""
IP Address Locator Script
Provides geolocation information for IP addresses using multiple APIs
"""

import requests
import json
import sys
import argparse
from typing import Dict, Optional
import time

class IPLocator:
    def __init__(self):
        self.apis = {
            'ipapi': 'http://ip-api.com/json/',
            'ipinfo': 'https://ipinfo.io/',
            'freegeoip': 'https://freegeoip.app/json/'
        }
    
    def get_location_ipapi(self, ip: str) -> Optional[Dict]:
        """Get location using ip-api.com (free, no key required)"""
        try:
            url = f"{self.apis['ipapi']}{ip}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'ip': data.get('query'),
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'zip_code': data.get('zip'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'organization': data.get('org'),
                    'source': 'ip-api.com'
                }
        except Exception as e:
            print(f"Error with ip-api: {e}")
        return None
    
    def get_location_ipinfo(self, ip: str, token: str = None) -> Optional[Dict]:
        """Get location using ipinfo.io (limited free tier)"""
        try:
            url = f"{self.apis['ipinfo']}{ip}"
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'loc' in data:
                lat, lon = data['loc'].split(',')
                return {
                    'ip': data.get('ip'),
                    'country': data.get('country'),
                    'region': data.get('region'),
                    'city': data.get('city'),
                    'zip_code': data.get('postal'),
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'timezone': data.get('timezone'),
                    'isp': data.get('org'),
                    'source': 'ipinfo.io'
                }
        except Exception as e:
            print(f"Error with ipinfo: {e}")
        return None
    
    def get_location_freegeoip(self, ip: str) -> Optional[Dict]:
        """Get location using freegeoip.app"""
        try:
            url = f"{self.apis['freegeoip']}{ip}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'ip': data.get('ip'),
                'country': data.get('country_name'),
                'country_code': data.get('country_code'),
                'region': data.get('region_name'),
                'city': data.get('city'),
                'zip_code': data.get('zip_code'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('time_zone'),
                'source': 'freegeoip.app'
            }
        except Exception as e:
            print(f"Error with freegeoip: {e}")
        return None
    
    def get_my_ip(self) -> str:
        """Get current public IP address"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except:
            try:
                response = requests.get('https://httpbin.org/ip', timeout=5)
                return response.json()['origin']
            except:
                return None
    
    def locate_ip(self, ip: str = None, api: str = 'ipapi', token: str = None) -> Optional[Dict]:
        """Main function to locate an IP address"""
        if not ip:
            ip = self.get_my_ip()
            if not ip:
                print("Could not determine IP address")
                return None
            print(f"Using current public IP: {ip}")
        
        if api == 'ipapi':
            return self.get_location_ipapi(ip)
        elif api == 'ipinfo':
            return self.get_location_ipinfo(ip, token)
        elif api == 'freegeoip':
            return self.get_location_freegeoip(ip)
        else:
            print(f"Unknown API: {api}")
            return None
    
    def locate_multiple_apis(self, ip: str = None) -> Dict:
        """Try multiple APIs and return all results"""
        if not ip:
            ip = self.get_my_ip()
        
        results = {}
        for api_name in ['ipapi', 'freegeoip', 'ipinfo']:
            print(f"Trying {api_name}...")
            result = self.locate_ip(ip, api_name)
            if result:
                results[api_name] = result
            time.sleep(1)  # Rate limiting
        
        return results
    
    def format_output(self, data: Dict) -> str:
        """Format the location data for display"""
        if not data:
            return "No location data available"
        
        output = []
        output.append(f"IP Address: {data.get('ip', 'N/A')}")
        output.append(f"Country: {data.get('country', 'N/A')} ({data.get('country_code', 'N/A')})")
        output.append(f"Region: {data.get('region', 'N/A')}")
        output.append(f"City: {data.get('city', 'N/A')}")
        output.append(f"ZIP Code: {data.get('zip_code', 'N/A')}")
        output.append(f"Coordinates: {data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}")
        output.append(f"Timezone: {data.get('timezone', 'N/A')}")
        output.append(f"ISP: {data.get('isp', 'N/A')}")
        if data.get('organization'):
            output.append(f"Organization: {data.get('organization', 'N/A')}")
        output.append(f"Source: {data.get('source', 'N/A')}")
        
        return '\n'.join(output)

def main():
    parser = argparse.ArgumentParser(description='Locate IP addresses geographically')
    parser.add_argument('ip', nargs='?', help='IP address to locate (optional)')
    parser.add_argument('--api', choices=['ipapi', 'ipinfo', 'freegeoip'], 
                       default='ipapi', help='API to use')
    parser.add_argument('--token', help='API token (for ipinfo.io)')
    parser.add_argument('--all', action='store_true', 
                       help='Try all available APIs')
    parser.add_argument('--json', action='store_true', 
                       help='Output in JSON format')
    
    args = parser.parse_args()
    
    locator = IPLocator()
    
    if args.all:
        results = locator.locate_multiple_apis(args.ip)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for api_name, data in results.items():
                print(f"\n=== {api_name.upper()} ===")
                print(locator.format_output(data))
    else:
        result = locator.locate_ip(args.ip, args.api, args.token)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(locator.format_output(result))

if __name__ == "__main__":
    main()
