#!/usr/bin/env python3
# Usage: ./gen_cnames.py <dhcp-file> <arp-file> <zone-file> <target-zone>

import re
import sys
from datetime import date

dhcp_file, arp_file, zone_file, target_zone = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

# Build IP → MAC from DHCP
ip_to_mac = {}
with open(dhcp_file) as f:
    for line in f:
        m = re.search(r'hardware ethernet ([\da-f:]+).*fixed-address ([\d.]+)', line)
        if m:
            ip_to_mac[m.group(2)] = m.group(1)

# Build set of live IPs from ARP table
arp_ips = set()
with open(arp_file) as f:
    for line in f:
        m = re.match(r'[\da-f:]{17}\s+([\d.]+)', line)
        if m:
            arp_ips.add(m.group(1))

# Build ordered list of (ip, hostname) from zone A records
ip_to_host = {}
host_order = []
with open(zone_file) as f:
    for line in f:
        m = re.match(r'^(\S+)\s+A\s+([\d.]+)', line)
        if m:
            host, ip = m.group(1), m.group(2)
            ip_to_host[ip] = host
            host_order.append(ip)

# Emit CNAMEs
print(f"; CNAME → DDNS migration")
print(f"; Generated: {date.today()}")
print(f"; MAC suffix = last 2 octets, colons stripped, lowercase")
print()

for ip in host_order:
    host = ip_to_host[ip]
    if ip not in ip_to_mac:
        print(f"; ⚠ {host} ({ip}) — no MAC found in DHCP, skipping")
        continue
    mac = ip_to_mac[ip]
    suffix = ''.join(mac.split(':')[-2:])
    flag = "  ; ⚠ not in ARP table" if ip not in arp_ips else ""
    print(f";{host:<24} CNAME   {suffix}.{target_zone}{flag}")
