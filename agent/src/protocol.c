#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>

#include "protocol.h"
#include "net.h"

int send_frame(int sock, const char *data, uint32_t len) {
    uint32_t net_len = htonl(len);

    if (send_exact(sock, &net_len, 4) < 0) 
        return -1;
    if (send_exact(sock, data, len) < 0) 
        return -1;
    return 0;
}

char *recv_frame(int sock, uint32_t *out_len) {
    uint32_t net_len = 0;
    uint32_t len = 0;
    char *buf = NULL;

    if (recv_exact(sock, &net_len, 4) < 0) 
        return NULL;
    len = ntohl(net_len);
    buf = malloc(sizeof(char) * (len + 1));
    if (!buf) 
        return NULL;
    if (recv_exact(sock, buf, len) < 0) {
        free(buf);
        return NULL;
    }
    buf[len] = '\0';
    *out_len = len;
    return buf;
}