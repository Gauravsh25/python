#!/usr/bin/env python3
"""
IP Address Locator Script
This script provides multiple methods to locate IP addresses using various geolocation services.
"""

import requests
import json
import socket
from typing import Dict, Optional
import argparse
import sys

class IPLocator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_public_ip(self) -> Optional[str]:
        """Get the public IP address of the current machine."""
        try:
            response = self.session.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except Exception as e:
            print(f"Error getting public IP: {e}")
            return None
    
    def validate_ip(self, ip: str) -> bool:
        """Validate if the given string is a valid IP address."""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    def locate_with_ipapi(self, ip: str) -> Optional[Dict]:
        """Locate IP using ip-api.com (free, no API key required)."""
        try:
            url = f"http://ip-api.com/json/{ip}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if data['status'] == 'success':
                return {
                    'ip': ip,
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': data.get('lat', 'Unknown'),
                    'longitude': data.get('lon', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'organization': data.get('org', 'Unknown'),
                    'service': 'ip-api.com'
                }
            else:
                print(f"Error from ip-api: {data.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Error with ip-api service: {e}")
            return None
    
    def locate_with_ipinfo(self, ip: str) -> Optional[Dict]:
        """Locate IP using ipinfo.io (free tier available)."""
        try:
            url = f"https://ipinfo.io/{ip}/json"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if 'error' not in data:
                location = data.get('loc', ',').split(',')
                return {
                    'ip': ip,
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': location[0] if len(location) > 0 else 'Unknown',
                    'longitude': location[1] if len(location) > 1 else 'Unknown',
                    'timezone': data.get('timezone', 'Unknown'),
                    'isp': data.get('org', 'Unknown'),
                    'postal': data.get('postal', 'Unknown'),
                    'service': 'ipinfo.io'
                }
            else:
                print(f"Error from ipinfo: {data.get('error', {}).get('message', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Error with ipinfo service: {e}")
            return None
    
    def locate_with_freeipapi(self, ip: str) -> Optional[Dict]:
        """Locate IP using freeipapi.com."""
        try:
            url = f"https://freeipapi.com/api/json/{ip}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            return {
                'ip': ip,
                'country': data.get('countryName', 'Unknown'),
                'country_code': data.get('countryCode', 'Unknown'),
                'region': data.get('regionName', 'Unknown'),
                'city': data.get('cityName', 'Unknown'),
                'latitude': data.get('latitude', 'Unknown'),
                'longitude': data.get('longitude', 'Unknown'),
                'timezone': data.get('timeZone', 'Unknown'),
                'isp': data.get('isp', 'Unknown'),
                'service': 'freeipapi.com'
            }
        except Exception as e:
            print(f"Error with freeipapi service: {e}")
            return None
    
    def locate_ip(self, ip: str, service: str = 'all') -> Optional[Dict]:
        """
        Locate an IP address using the specified service.
        
        Args:
            ip: IP address to locate
            service: Service to use ('ipapi', 'ipinfo', 'freeipapi', or 'all')
        """
        if not self.validate_ip(ip):
            print(f"Invalid IP address: {ip}")
            return None
        
        services = {
            'ipapi': self.locate_with_ipapi,
            'ipinfo': self.locate_with_ipinfo,
            'freeipapi': self.locate_with_freeipapi
        }
        
        if service == 'all':
            # Try all services until one works
            for service_name, service_func in services.items():
                print(f"Trying {service_name}...")
                result = service_func(ip)
                if result:
                    return result
            print("All services failed")
            return None
        elif service in services:
            return services[service](ip)
        else:
            print(f"Unknown service: {service}")
            return None
    
    def print_location_info(self, info: Dict):
        """Print location information in a formatted way."""
        if not info:
            print("No location information available")
            return
        
        print(f"\n{'='*50}")
        print(f"IP Address Location Information")
        print(f"{'='*50}")
        print(f"IP Address:    {info.get('ip', 'Unknown')}")
        print(f"Country:       {info.get('country', 'Unknown')}")
        print(f"Country Code:  {info.get('country_code', 'Unknown')}")
        print(f"Region:        {info.get('region', 'Unknown')}")
        print(f"City:          {info.get('city', 'Unknown')}")
        print(f"Latitude:      {info.get('latitude', 'Unknown')}")
        print(f"Longitude:     {info.get('longitude', 'Unknown')}")
        print(f"Timezone:      {info.get('timezone', 'Unknown')}")
        print(f"ISP:           {info.get('isp', 'Unknown')}")
        if 'organization' in info:
            print(f"Organization:  {info.get('organization', 'Unknown')}")
        if 'postal' in info:
            print(f"Postal Code:   {info.get('postal', 'Unknown')}")
        print(f"Service Used:  {info.get('service', 'Unknown')}")
        print(f"{'='*50}")

def main():
    parser = argparse.ArgumentParser(description='Locate IP addresses using geolocation services')
    parser.add_argument('ip', nargs='?', help='IP address to locate (optional)')
    parser.add_argument('-s', '--service', choices=['ipapi', 'ipinfo', 'freeipapi', 'all'], 
                       default='all', help='Geolocation service to use')
    parser.add_argument('-m', '--my-ip', action='store_true', 
                       help='Locate your own public IP address')
    parser.add_argument('-j', '--json', action='store_true', 
                       help='Output in JSON format')
    
    args = parser.parse_args()
    
    locator = IPLocator()
    
    # Determine which IP to locate
    target_ip = None
    if args.my_ip:
        target_ip = locator.get_public_ip()
        if not target_ip:
            print("Failed to get public IP address")
            sys.exit(1)
        print(f"Your public IP address: {target_ip}")
    elif args.ip:
        target_ip = args.ip
    else:
        # Interactive mode
        print("IP Address Locator")
        print("1. Enter an IP address")
        print("2. Locate your public IP")
        choice = input("Choose an option (1 or 2): ").strip()
        
        if choice == '1':
            target_ip = input("Enter IP address: ").strip()
        elif choice == '2':
            target_ip = locator.get_public_ip()
            if not target_ip:
                print("Failed to get public IP address")
                sys.exit(1)
            print(f"Your public IP address: {target_ip}")
        else:
            print("Invalid choice")
            sys.exit(1)
    
    # Locate the IP
    if target_ip:
        info = locator.locate_ip(target_ip, args.service)
        
        if info:
            if args.json:
                print(json.dumps(info, indent=2))
            else:
                locator.print_location_info(info)
        else:
            print("Failed to locate IP address")
            sys.exit(1)
    else:
        print("No IP address provided")
        sys.exit(1)

if __name__ == "__main__":
    main()
