#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <ctype.h>

#include "agent.h"

/**
 * @brief Validate a TCP port number.
 *
 * Checks that the provided string contains only numerical characters
 * and that the resulting port number is within the valid TCP/UDP port
 * range (1-65535).
 *
 * @param port_str Port number as a string.
 * @param port_out Pointer where the validated integer port will be stored.
 *
 * @return 1 if the port is valid, 0 otherwise.
 */
int is_valid_port(const char *port_str, int *port_out)
{
    /* Ensure that every character is a digit. */
    for (size_t i = 0; i < strlen(port_str); i++) {
        if (!isdigit(port_str[i]))
            return 0;
    }
    /* Convert string to integer. */
    long port = strtol(port_str, NULL, 10);
    /* Check the valid TCP/UDP port range. */
    if (port < 1 || port > 65535)
        return 0;
    *port_out = (int)port;
    return 1;
}

/**
 * @brief Validate an IPv4 address.
 *
 * Uses inet_pton() to check whether the provided string is a valid
 * IPv4 address.
 *
 * @param ip IPv4 address string.
 *
 * @return 1 if the address is valid, 0 otherwise.
 */
int is_valid_ipv4(const char *ip)
{
    struct sockaddr_in sa;

    return inet_pton(AF_INET, ip, &(sa.sin_addr)) == 1;
}

/**
 * @brief Display command-line usage information.
 *
 * Prints the expected arguments and available options for starting
 * the agent.
 */
void helper()
{
    printf("usage: main.py [-h] host port\n\n");
    printf("A python agent to connect to experience server\n\n");
    printf("positional arguments:\n");
    printf("  host\t\tExperience server address\n");
    printf("  port\t\tExperience server port\n\n");
    printf("options:\n");
    printf(" -h, --help  show this help message and exit\n");
}

/**
 * @brief Agent entry point.
 *
 * Parses command-line arguments, validates the server address and port,
 * then starts the agent connection.
 *
 * Expected usage:
 *
 *     ./agent <host> <port>
 *
 * Example:
 *
 *     ./agent 192.168.1.10 5573
 *
 * If no arguments are provided, default values are displayed:
 *
 *     host = 127.0.0.1
 *     port = 5573
 *
 * @param argc Number of command-line arguments.
 * @param argv Command-line argument array.
 *
 * @return 0 on success, 1 on invalid input or connection error.
 */
int main(int argc, char *argv[])
{
    const char *host = "127.0.0.1";
    int port = 5573;

    /*
     * The agent expects exactly two arguments:
     * - server IPv4 address
     * - server port
     */
    if (argc != 3) {
        helper();
    } else {
        host = argv[1];
        /* Validate the server IPv4 address. */
        if (!is_valid_ipv4(host)) {
            fprintf(stderr, "[agent] invalid IPv4 address: %s\n", host);
            return 1;
        }
        /* Validate and parse the server port. */
        if (!is_valid_port(argv[2], &port)) {
            fprintf(stderr, "[agent] invalid port: %s\n", argv[2]);
            return 1;
        }
        /* Start the agent. */
        return agent(host, port);
    }
    return 0;
}