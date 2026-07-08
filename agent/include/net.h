#ifndef NET_H
#define NET_H

#include <stddef.h>

int send_exact(int sock, const void *buf, size_t len);
int recv_exact(int sock, void *buf, size_t len);

#endif