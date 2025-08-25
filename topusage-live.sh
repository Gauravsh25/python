#!/bin/bash
# topusage-live.sh - Live monitor for Memory & CPU usage with system stats

while true; do
  clear
  echo -e "============================================="
  echo -e "   Top 5 Memory Consuming Processes (GB)"
  echo -e "============================================="
  echo -e "PID\tCOMMAND\t%MEM\tMEM(GB)"

  ps -eo pid,comm,%mem,rss --sort=-rss | head -n 6 | \
  awk '{if(NR>1){printf "%s\t%s\t%s\t%.2f\n",$1,$2,$3,$4/1024/1024}}'

  echo -e "\n============================================="
  echo -e "   Top 5 CPU Consuming Processes"
  echo -e "============================================="
  echo -e "PID\tCOMMAND\t%CPU"

  ps -eo pid,comm,%cpu --sort=-%cpu | head -n 6 | \
  awk '{if(NR>1){printf "%s\t%s\t%s\n",$1,$2,$3}}'

  echo -e "\n============================================="
  echo -e "   System Usage Overview"
  echo -e "============================================="

  # Memory usage in GB
  used=$(free -g | awk '/Mem:/ {print $3}')
  total=$(free -g | awk '/Mem:/ {print $2}')
  mem_percent=$(free | awk '/Mem:/ {printf "%.1f", $3/$2*100}')

  # CPU usage %
  cpu_idle=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | cut -d. -f1)
  cpu_used=$((100 - cpu_idle))

  echo -e "Memory Used : $used / $total GB ($mem_percent%)"
  echo -e "CPU Usage   : $cpu_used%"
  
  sleep 5   # refresh every 5 seconds
done

