#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

uint32_t stage1(uint32_t x) {
    x = ((x & 0xFF00FF00) >> 8) | ((x & 0x00FF00FF) << 8);
    x ^= 0xDEADBEEF;
    x = (x << 13) | (x >> 19);
    return x;
}

uint32_t stage2(uint32_t x) {
    x += 0x13371337;
    x = ((x & 0xF0F0F0F0) >> 4) | ((x & 0x0F0F0F0F) << 4);
    x ^= 0xCAFEBABE;
    return x;
}

uint32_t stage3(uint32_t x) {
    x = (x >> 7) | (x << 25);
    x *= 0x41414141;
    x ^= 0x5A5A5A5A;
    return x;
}

uint32_t generate_key() {
    uint32_t k1 = 0x41584557;
    uint32_t k2 = 0x48454746;
    uint32_t k3 = 0x41534458;
    uint32_t k4 = 0x48424A41;
    
    k1 = stage1(k1);
    k2 = stage2(k2);
    k3 = stage3(k3);
    k4 = k1 ^ k2 ^ k3;
    
    return k4;
}

void generate_verification_constants(uint32_t *c1, uint32_t *c2) {
    uint32_t seed = 0x12345678;
    
    seed = stage1(seed);
    seed = stage2(seed);
    *c1 = seed;
    
    seed = stage3(seed);
    seed ^= generate_key();
    *c2 = seed;
}

int verify_input(uint32_t input) {
    uint32_t c1, c2;
    generate_verification_constants(&c1, &c2);
    
    uint32_t transformed = input;
    transformed = stage1(transformed);
    transformed = stage2(transformed);
    transformed = stage3(transformed);
    
    uint32_t key = generate_key();
    uint32_t left = transformed ^ key;
    uint32_t right = c1 ^ c2;
    
    return left == right;
}

uint32_t rotl(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

uint32_t Ch(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (~x & z);
}

uint32_t Maj(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (x & z) ^ (y & z);
}

uint32_t Sigma0(uint32_t x) {
    return rotl(x, 30) ^ rotl(x, 19) ^ rotl(x, 10);
}

uint32_t Sigma1(uint32_t x) {
    return rotl(x, 26) ^ rotl(x, 21) ^ rotl(x, 7);
}

uint32_t sigma0(uint32_t x) {
    return rotl(x, 25) ^ rotl(x, 14) ^ (x >> 3);
}

uint32_t sigma1(uint32_t x) {
    return rotl(x, 15) ^ rotl(x, 13) ^ (x >> 10);
}

void sha256(const char *data, char *hash) {
    uint32_t K[64] = {
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    };
    
    uint32_t H[8] = {
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    };
    
    int len = strlen(data);
    int blocks = (len + 9 + 63) / 64;
    uint8_t *msg = calloc(blocks * 64, 1);
    memcpy(msg, data, len);
    msg[len] = 0x80;
    
    uint64_t bits = len * 8;
    for (int i = 0; i < 8; i++) {
        msg[blocks * 64 - 8 + i] = (bits >> (56 - i * 8)) & 0xFF;
    }
    
    for (int b = 0; b < blocks; b++) {
        uint32_t W[64];
        for (int i = 0; i < 16; i++) {
            W[i] = (msg[b * 64 + i * 4] << 24) | (msg[b * 64 + i * 4 + 1] << 16) |
                   (msg[b * 64 + i * 4 + 2] << 8) | msg[b * 64 + i * 4 + 3];
        }
        
        for (int i = 16; i < 64; i++) {
            W[i] = sigma1(W[i-2]) + W[i-7] + sigma0(W[i-15]) + W[i-16];
        }
        
        uint32_t a = H[0], b = H[1], c = H[2], d = H[3];
        uint32_t e = H[4], f = H[5], g = H[6], h = H[7];
        
        for (int i = 0; i < 64; i++) {
            uint32_t T1 = h + Sigma1(e) + Ch(e, f, g) + K[i] + W[i];
            uint32_t T2 = Sigma0(a) + Maj(a, b, c);
            h = g;
            g = f;
            f = e;
            e = d + T1;
            d = c;
            c = b;
            b = a;
            a = T1 + T2;
        }
        
        H[0] += a; H[1] += b; H[2] += c; H[3] += d;
        H[4] += e; H[5] += f; H[6] += g; H[7] += h;
    }
    
    for (int i = 0; i < 8; i++) {
        sprintf(hash + i * 8, "%08x", H[i]);
    }
    
    free(msg);
}

void print_flag(uint32_t correct_input) {
    char input_str[16];
    char hash[65] = {0};
    
    snprintf(input_str, sizeof(input_str), "%u", correct_input);
    sha256(input_str, hash);
    
    printf("Congratulations! Flag: kctf-jr{%s}\n", hash);
}

int main() {
    printf("Enter the magic number: ");
    
    uint32_t input;
    if (scanf("%u", &input) != 1) {
        printf("Invalid input!\n");
        return 1;
    }
    
    if (verify_input(input)) {
        printf("Correct! Generating flag...\n");
        print_flag(input);
    } else {
        printf("Wrong! Try again.\n");
    }
    
    return 0;
}