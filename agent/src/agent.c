#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>

#include "command.h"
#include "protocol.h"
#include "dispatcher.h"

/**
 * @brief Main command processing loop.
 *
 * Continuously receives framed messages from the server, parses them
 * into command structures, dispatches them to the appropriate handler,
 * and stops when a DONE command or an unrecoverable error is received.
 *
 * @param sock Connected socket.
 * @return 0 when the loop terminates.
 */
int loop(int sock)
{
    uint32_t len = 0;
    int status = 0;
    char *msg = NULL;
    cmd_t *cmd = NULL;

    while (1) {
        /* Receive the next framed message. */
        msg = recv_frame(sock, &len);
        if (!msg)
            break;
        /* Parse the received JSON into a command structure. */
        cmd = cmd_from_json(msg);
        free(msg);
        if (!cmd) {
            fprintf(stderr, "Invalid message\n");
            continue;
        }
        /* Dispatch the command to its registered handler. */
        status = dispatch_command(cmd, sock);
        /* A DONE command terminates the agent loop. */
        if (status == 1) {
            printf("[Agent]: received DONE command\n");
            break;
        }
        /* Stop on dispatcher errors. */
        if (status == -1) {
            printf("[Agent]: error with dispatcher\n");
            break;
        }
        /* Release the processed command. */
        cmd_free(cmd);
        cmd = NULL;
    }
    /* Free any remaining command before exiting. */
    if (cmd)
        cmd_free(cmd);
    return 0;
}

/**
 * @brief Connect to the server and start the agent.
 *
 * Creates a TCP socket, connects to the specified server, enters the
 * command processing loop, and closes the connection before exiting.
 *
 * @param host IPv4 address of the server.
 * @param port TCP port of the server.
 * @return 0 on success, 1 if an error occurs while creating or
 *         connecting the socket.
 */
int agent(const char *host, int port)
{
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in server;

    /* Create the TCP socket. */
    if (sock < 0) {
        perror("socket");
        return 1;
    }
    /* Initialize the server address structure. */
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    /* Convert the textual IPv4 address into binary form. */
    if (inet_pton(AF_INET, host, &server.sin_addr) <= 0) {
        perror("inet_pton");
        close(sock);
        return 1;
    }
    /* Connect to the remote server. */
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("connect");
        close(sock);
        return 1;
    }
    /* Start processing incoming commands. */
    loop(sock);
    /* Clean up the connection. */
    close(sock);
    printf("[agent] exit\n");
    return 0;
}