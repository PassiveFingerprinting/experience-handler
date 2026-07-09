#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>

#include "protocol.h"
#include "net.h"

/**
 * @brief Send a length-prefixed message over a socket.
 *
 * The message format is:
 *
 * +------------+-------------------+
 * | 4 bytes    | Payload           |
 * | length     | data              |
 * +------------+-------------------+
 *
 * The length field is converted to network byte order before being
 * transmitted to ensure compatibility between systems with different
 * endianness.
 *
 * @param sock Socket file descriptor.
 * @param data Buffer containing the message payload.
 * @param len Length of the payload in bytes.
 *
 * @return 0 on success, -1 if sending fails.
 */
int send_frame(int sock, const char *data, uint32_t len)
{
    /* Convert length to network byte order. */
    uint32_t net_len = htonl(len);

    /* Send the message length header. */
    if (send_exact(sock, &net_len, 4) < 0)
        return -1;

    /* Send the actual payload. */
    if (send_exact(sock, data, len) < 0)
        return -1;

    return 0;
}

/**
 * @brief Receive a length-prefixed message from a socket.
 *
 * Reads the 4-byte length header first, allocates enough memory for
 * the payload, then receives the complete message.
 *
 * The returned buffer is null-terminated and must be freed by the
 * caller using free().
 *
 * @param sock Socket file descriptor.
 * @param out_len Pointer where the received payload length will be
 *                stored.
 *
 * @return Allocated message buffer on success, NULL on error.
 */
char *recv_frame(int sock, uint32_t *out_len)
{
    uint32_t net_len = 0;
    uint32_t len = 0;
    char *buf = NULL;

    /* Receive the message length header. */
    if (recv_exact(sock, &net_len, 4) < 0)
        return NULL;
    /* Convert length from network byte order. */
    len = ntohl(net_len);
    /* Allocate buffer for payload plus null terminator. */
    buf = malloc(sizeof(char) * (len + 1));
    if (!buf)
        return NULL;
    /* Receive the complete payload. */
    if (recv_exact(sock, buf, len) < 0) {
        free(buf);
        return NULL;
    }
    /* Make the received data usable as a C string. */
    buf[len] = '\0';
    *out_len = len;
    return buf;
}