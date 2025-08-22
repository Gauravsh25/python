#!/usr/bin/env python3
import os
import time
import sys

def create_zombie():
    # Create child process
    pid = os.fork()
    
    if pid == 0:
        # Child process
        print(f"Child process (PID: {os.getpid()}) is running")
        print("Child process is about to exit")
        sys.exit(0)  # Child exits immediately
    else:
        # Parent process
        print(f"Parent process (PID: {os.getpid()}) created child (PID: {pid})")
        print("Parent is sleeping for 30 seconds...")
        print("During this time, child will become a zombie")
        print(f"Check with: ps aux | grep {pid}")
        
        # Parent sleeps without calling os.wait()
        time.sleep(30)
        
        print("Parent is now awake. Zombie should still exist.")
        print("Parent will sleep for another 30 seconds...")
        time.sleep(30)
        
        # To clean up the zombie, uncomment the next line:
        # os.wait()
        
        print("Parent process exiting")

if __name__ == "__main__":
    create_zombie()
