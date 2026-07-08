#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>

int send_frame(int sock, const char *data, uint32_t len);
char *recv_frame(int sock, uint32_t *out_len);

#endif