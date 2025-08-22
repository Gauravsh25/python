# Install development tools group (includes gcc, make, etc.)
yum groupinstall "Development Tools"
# OR just install gcc
yum install gcc

# For newer versions, use dnf instead of yum
dnf groupinstall "Development Tools"
# OR
dnf install gcc

apt update
apt install build-essential
# OR just gcc
apt install gcc


How to compile and run:

Save the code as zombie_process.c
Compile: gcc -o zombie_process zombie_process.c
Run: ./zombie_process
