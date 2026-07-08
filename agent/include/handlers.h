// handlers.h

#ifndef HANDLERS_H
#define HANDLERS_H

#include "command.h"

int handle_system_info(const cmd_t *cmd, int sock);
int handle_system_done(const cmd_t *cmd, int sock);

#endif