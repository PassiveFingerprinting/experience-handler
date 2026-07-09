#include <unistd.h>
#include <sys/socket.h>

#include "net.h"

/**
 * @brief Send exactly a specified number of bytes over a socket.
 *
 * The send() system call is not guaranteed to transmit the entire
 * buffer in one call. This function repeatedly calls send() until
 * all requested bytes have been sent or an error occurs.
 *
 * @param sock Socket file descriptor.
 * @param buf Buffer containing data to send.
 * @param len Number of bytes to send.
 *
 * @return 0 on success, -1 if a send error occurs or the connection
 *         is closed.
 */
int send_exact(int sock, const void *buf, size_t len)
{
    size_t total = 0;

    /* Keep sending until the complete buffer has been transmitted. */
    while (total < len) {
        ssize_t n = send(sock, (const char *)buf + total, len - total, 0);
        /* send() failed or connection was closed. */
        if (n <= 0)
            return -1;
        total += n;
    }
    return 0;
}

/**
 * @brief Receive exactly a specified number of bytes from a socket.
 *
 * The recv() system call may return fewer bytes than requested.
 * This function ensures that the requested amount of data is received
 * before returning.
 *
 * @param sock Socket file descriptor.
 * @param buf Buffer where received data will be stored.
 * @param len Number of bytes to receive.
 *
 * @return 0 on success, -1 if a receive error occurs or the connection
 *         is closed.
 */
int recv_exact(int sock, void *buf, size_t len)
{
    size_t total = 0;

    /* Keep receiving until the complete buffer has been filled. */
    while (total < len) {
        ssize_t n = recv(sock, (char *)buf + total, len - total, 0);
        /* recv() failed or connection was closed. */
        if (n <= 0)
            return -1;
        total += n;
    }
    return 0;
}