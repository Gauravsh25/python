#!/bin/bash

echo "======================================"
echo "        System Health Report"
echo "======================================"

# Hostname
echo "Hostname        : $(hostname)"

# OS and Kernel info
echo "OS              : $(grep PRETTY_NAME /etc/os-release | cut -d= -f2- | tr -d '\"')"
echo "Kernel Version  : $(uname -r)"

# Uptime
echo "Uptime          : $(uptime -p)"

# Current date/time
echo "Date & Time     : $(date)"

# IP address
echo "IP Address      : $(hostname -I | awk '{print $1}')"

# Logged in users
echo "Logged-in Users : $(who | wc -l)"

# CPU Usage
echo "CPU Usage       : $(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8"%"}')"

# Memory Usage
echo "Memory Usage    : $(free -h | awk '/Mem:/ {print $3 " / " $2}')"

# Disk Usage
echo "Disk Usage      :"
df -h --total | grep 'total'

echo "======================================"

