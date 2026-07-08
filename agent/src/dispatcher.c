#include "dispatcher.h"
#include "handlers.h"
#include "command.h"

static command_handler_t handlers[] = {
    [SYSTEM_INFO] = handle_system_info,
    [DONE] = handle_system_done
};

int dispatch_command(const cmd_t *cmd, int sock)
{
    command_handler_t handler;

    if (!cmd)
        return -1;
    if (cmd->cmd >= sizeof(handlers) / sizeof(handlers[0]))
        return -1;
    handler = handlers[cmd->cmd];
    if (!handler)
        return -1;
    return handler(cmd, sock);
}