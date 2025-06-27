// gcc -o prob prob.c -no-pie

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void shell() {
    execve("/bin/sh", NULL, NULL);
}

void init() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

int main() {
    init();
    unsigned long long addr, val;
    while(1) {
        printf("addr > ");
        scanf("%llu", &addr);
        printf("val > ");
        scanf("%llu", &val);
        if(addr == 0 || val == 0) 
            break;
        *(unsigned long long *)addr = val;
    }
}
