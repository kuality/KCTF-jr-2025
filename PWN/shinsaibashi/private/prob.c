#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>

#define BUF_SIZE 0x100

uint32_t urandom_seed;
uint8_t key[8];

void init() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        perror("Failed to open /dev/urandom");
        exit(EXIT_FAILURE);
    }
    if (read(fd, &urandom_seed, sizeof(urandom_seed)) != sizeof(urandom_seed)) {
        perror("Failed to read random bytes");
        close(fd);
        exit(EXIT_FAILURE);
    }
    srand(urandom_seed);
    close(fd);
}

void generate_key() {
    for(int i = 0; i < 8; i++)
        key[i] = rand() % 256;
}

void read_input(char *buf) {
    for(size_t i = 0;; i++) {
        int c = getchar();
        if (c == EOF || c == '\n')
            return;
        buf[i] = (char)c;
    }
}

int main() {
    init();
    generate_key();
    char buf[BUF_SIZE];   
    while(1) {
        printf("> ");
        read_input(buf);
        if(!strcmp(buf, "exit"))
            break;
        size_t len = strlen(buf);
        for(size_t i = 0; i < len; i++)
            buf[i] ^= key[i % 8];
        for(size_t i = 0; i < len; i++)
            printf("%02x ", (unsigned char)buf[i]);
        printf("\n");
    }
    return 0;
}