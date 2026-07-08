#include <unistd.h>
#include <sys/socket.h>

#include "net.h"

int send_exact(int sock, const void *buf, size_t len) {
    size_t total = 0;

    while (total < len) {
        ssize_t n = send(sock, (const char*)buf + total, len - total, 0);
        if (n <= 0) return -1;
        total += n;
    }
    return 0;
}

int recv_exact(int sock, void *buf, size_t len) {
    size_t total = 0;

    while (total < len) {
        ssize_t n = recv(sock, (char*)buf + total, len - total, 0);
        if (n <= 0) 
            return -1;
        total += n;
    }
    return 0;
}