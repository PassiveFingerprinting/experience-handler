// dispatcher.h

#ifndef DISPATCHER_H
#define DISPATCHER_H

#include "command.h"

typedef int (*command_handler_t)(const cmd_t *cmd, int sock);

int dispatch_command(const cmd_t *cmd, int sock);

#endif