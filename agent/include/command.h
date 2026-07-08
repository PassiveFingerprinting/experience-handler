// command.h

#ifndef COMMAND_H
#define COMMAND_H

#include "cJSON.h"

typedef enum {
    SYSTEM_INFO,
    DONE,
    UNKOWN
} command_type_t;

typedef struct cmd {
    int type;
    command_type_t cmd;
    cJSON *data;
} cmd_t;

cmd_t *cmd_from_json(const char *json);
command_type_t command_from_string(const char *cmd);
void cmd_free(cmd_t *cmd);

#endif