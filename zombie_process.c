#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

int main() {
    pid_t child_pid;
    
    // Create a child process
    child_pid = fork();
    
    if (child_pid == 0) {
        // Child process
        printf("Child process (PID: %d) is running\n", getpid());
        printf("Child process is about to exit\n");
        exit(0);  // Child exits immediately
    } 
    else if (child_pid > 0) {
        // Parent process
        printf("Parent process (PID: %d) created child (PID: %d)\n", 
               getpid(), child_pid);
        printf("Parent is sleeping for 30 seconds...\n");
        printf("During this time, child will become a zombie\n");
        printf("Check with: ps aux | grep %d\n", child_pid);
        
        // Parent sleeps without calling wait()
        // This creates the zombie state
        sleep(30);
        
        printf("Parent is now awake. Zombie should still exist.\n");
        printf("Parent will sleep for another 30 seconds without cleaning up...\n");
        sleep(30);
        
        // If we wanted to clean up the zombie, we would call:
        // wait(NULL);
        
        printf("Parent process exiting\n");
    } 
    else {
        // Fork failed
        perror("fork failed");
        return 1;
    }
    
    return 0;
}
