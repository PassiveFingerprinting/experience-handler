#include <stdlib.h>
#include <string.h>

#include "command.h"

command_type_t command_from_string(const char *cmd)
{
    if (strcmp(cmd, "SYSTEM_INFO") == 0)
        return SYSTEM_INFO;
    if (strcmp(cmd, "DONE") == 0)
        return DONE;
    return UNKOWN;    
}

cmd_t *cmd_from_json(const char *json_str)
{
    cJSON *root = cJSON_Parse(json_str);
    if (!root) 
        return NULL;

    cJSON *type = cJSON_GetObjectItem(root, "type");
    cJSON *payload = cJSON_GetObjectItem(root, "payload");

    if (!cJSON_IsNumber(type) || !cJSON_IsObject(payload)) {
        cJSON_Delete(root);
        return NULL;
    }

    cJSON *cmd = cJSON_GetObjectItem(payload, "cmd");
    cJSON *data = cJSON_GetObjectItem(payload, "data");

    if (!cJSON_IsString(cmd) || !cJSON_IsObject(data)) {
        cJSON_Delete(root);
        return NULL;
    }

    cmd_t *out = malloc(sizeof(cmd_t));
    if (!out) {
        cJSON_Delete(root);
        return NULL;
    }

    out->type = type->valueint;   // "0" → 0
    out->cmd = command_from_string(cmd->valuestring);
    out->data = cJSON_Duplicate(data, 1);

    cJSON_Delete(root);
    return out;
}

void cmd_free(cmd_t *cmd)
{
    if (!cmd)
        return;
    cJSON_Delete(cmd->data);
    free(cmd);
}