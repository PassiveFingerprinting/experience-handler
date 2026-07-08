#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <ctype.h>

#include "agent.h"

int is_valid_port(const char *port_str, int *port_out) {
    for (size_t i = 0; i < strlen(port_str); i++) {
        if (!isdigit(port_str[i])) return 0;
    }

    long port = strtol(port_str, NULL, 10);

    if (port < 1 || port > 65535) return 0;

    *port_out = (int)port;
    return 1;
}

int is_valid_ipv4(const char *ip) {
    struct sockaddr_in sa;
    return inet_pton(AF_INET, ip, &(sa.sin_addr)) == 1;
}

void helper() {
    printf("usage: main.py [-h] host port\n\n");
    printf("A python agent to connect to experience server\n\n");
    printf("positional arguments:\n");
    printf("  host\t\tExperience server address\n");
    printf("  port\t\tExperience server port\n\n");
    printf("options:\n -h, --help  show this help message and exit");
}

int main(int argc, char *argv[]) {
    const char *host = "127.0.0.1";
    int port = 5573;

    if (argc != 3) {
        helper();
    } else {
        host = argv[1];
        if (!is_valid_ipv4(host)) {
            fprintf(stderr, "[agent] invalid IPv4 address: %s\n", host);
            return 1;
        }

        if (!is_valid_port(argv[2], &port)) {
            fprintf(stderr, "[agent] invalid port: %s\n", argv[2]);
            return 1;
        }
        return agent(host, port);
    }
    return 0;
}