#!/bin/bash
# topusage.sh - Show top processes by Memory & CPU with system usage

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
echo -e "   System Memory Usage"
echo -e "============================================="
used=$(free -g | awk '/Mem:/ {print $3}')
total=$(free -g | awk '/Mem:/ {print $2}')
echo -e "Total Used (GB): $used / $total GB"

