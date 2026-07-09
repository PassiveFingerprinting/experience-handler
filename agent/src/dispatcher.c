#include "dispatcher.h"
#include "handlers.h"
#include "command.h"

/**
 * @brief Table mapping command types to their corresponding handlers.
 *
 * Each entry associates a command_type_t value with the function
 * responsible for processing that command.
 */
static command_handler_t handlers[] = {
    [SYSTEM_INFO] = handle_system_info,
    [DONE] = handle_system_done
};

/**
 * @brief Dispatch a command to its registered handler.
 *
 * This function validates the command, looks up the corresponding
 * handler in the dispatch table, and invokes it.
 *
 * @param cmd Parsed command structure.
 * @param sock Connected socket associated with the client.
 * @return The return value of the handler on success, or -1 if the
 *         command is invalid or no handler is registered.
 */
int dispatch_command(const cmd_t *cmd, int sock)
{
    command_handler_t handler;

    /* Ensure a valid command was provided. */
    if (!cmd)
        return -1;
    /* Verify that the command value is within the dispatch table. */
    if (cmd->cmd >= sizeof(handlers) / sizeof(handlers[0]))
        return -1;
    /* Retrieve the handler associated with the command. */
    handler = handlers[cmd->cmd];
    /* Reject commands that have no registered handler. */
    if (!handler)
        return -1;
    /* Execute the command handler. */
    return handler(cmd, sock);
}