#include <stdio.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>

#define SYSCALL_OPCODE "\x0f\x05"

int main() {
    unsigned char* region = (unsigned char *)mmap(NULL, 0x1000, PROT_WRITE | PROT_READ | PROT_EXEC, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if(region == MAP_FAILED) {
        perror("mmap");
        return 1;
    }
    write(1, "input shellcode > ", 18);
    read(0, region, 0x100);
    for(int i = 0; i < 0x100; i++) {
        if(region[i] == 0x0f && region[i + 1] == 0x05)
            return 0;
    }
    ((void(*)())region)();
    munmap(region, 0x1000);
}