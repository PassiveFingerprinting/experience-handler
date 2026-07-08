#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>

#include "command.h"
#include "protocol.h"
#include "dispatcher.h"

int loop(int sock) {
    uint32_t len = 0;
    int status = 0;
    char *msg = NULL;
    cmd_t *cmd = NULL;

    while (1) {
        msg = recv_frame(sock, &len);
        if (!msg) 
            break;
        cmd = cmd_from_json(msg);
        free(msg);
        if (!cmd) {
            fprintf(stderr, "Invalid message\n");
            continue;
        }
        status = dispatch_command(cmd, sock);
        if (status == 1) {
            printf("[Agent]: received DONE command\n");
            break;
        }
        if (status == -1) {
            printf("[Agent]: error with dispatcher\n");
            break;
        }
        cmd_free(cmd);
    }
    if (cmd)
        cmd_free(cmd);
    return 0;
}

int agent(const char *host, int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in server;

    if (sock < 0) {
        perror("socket");
        return 1;
    }
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    if (inet_pton(AF_INET, host, &server.sin_addr) <= 0) {
        perror("inet_pton");
        close(sock);
        return 1;
    }
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("connect");
        close(sock);
        return 1;
    }
    loop(sock);
    close(sock);
    printf("[agent] exit\n");
    return 0;
}