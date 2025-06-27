#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

void init() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

void print_menu() {
    printf("1. Input payload\n");
    printf("2. Show payload\n");
    printf("3. Delete payload\n");
}

int main() {
    init();
    char payload[0x1000] = {0};
    int sel;
    while(1) {
        print_menu();
        printf("> " );
        scanf("%d", &sel);
        switch(sel) {
            case 1:
                read(0, payload, 0x1000);
                break;
            case 2:
                warnx(payload);
                break;
            case 3:
                memset(payload, 0, sizeof(payload));
                break;
            case 4:
                return 0;
        }
    }
}
