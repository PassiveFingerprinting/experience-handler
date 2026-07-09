#include <stdlib.h>
#include <string.h>

#include "command.h"

/**
 * @brief Convert a command string into its corresponding enum value.
 *
 * Maps the command name received in a JSON packet to the internal
 * command_type_t enumeration.
 *
 * @param cmd Command string.
 * @return Corresponding command_type_t value, or UNKOWN if the
 *         command is not recognized.
 */
command_type_t command_from_string(const char *cmd)
{
    if (strcmp(cmd, "SYSTEM_INFO") == 0)
        return SYSTEM_INFO;
    if (strcmp(cmd, "DONE") == 0)
        return DONE;
    return UNKOWN;
}

/**
 * @brief Parse a JSON packet into a cmd_t structure.
 *
 * Expected JSON format:
 *
 * {
 *     "type": 0,
 *     "payload": {
 *         "cmd": "SYSTEM_INFO",
 *         "data": { ... }
 *     }
 * }
 *
 * The "data" object is duplicated and must later be freed by
 * cmd_free().
 *
 * @param json_str JSON string to parse.
 * @return Pointer to a newly allocated cmd_t structure, or NULL
 *         if parsing or allocation fails.
 */
cmd_t *cmd_from_json(const char *json_str)
{
    cJSON *root = cJSON_Parse(json_str);
    cJSON *type = NULL;
    cJSON *payload = NULL;
    cJSON *cmd = NULL;
    cJSON *data = NULL;
    cmd_t *out = NULL;

    /* Failed to parse the JSON document. */
    if (!root)
        return NULL;
    /* Retrieve the required top-level fields. */
    type = cJSON_GetObjectItem(root, "type");
    payload = cJSON_GetObjectItem(root, "payload");
    /* Validate their types. */
    if (!cJSON_IsNumber(type) || !cJSON_IsObject(payload)) {
        cJSON_Delete(root);
        return NULL;
    }
    /* Retrieve the payload fields. */
    cmd = cJSON_GetObjectItem(payload, "cmd");
    data = cJSON_GetObjectItem(payload, "data");
    /* Ensure the payload has the expected format. */
    if (!cJSON_IsString(cmd) || !cJSON_IsObject(data)) {
        cJSON_Delete(root);
        return NULL;
    }
    /* Allocate the output structure. */
    out = malloc(sizeof(cmd_t));
    if (!out) {
        cJSON_Delete(root);
        return NULL;
    }
    /* Fill the structure from the parsed JSON. */
    out->type = type->valueint;
    out->cmd = command_from_string(cmd->valuestring);
    /* Duplicate the data object so it remains valid after deleting
     * the parsed JSON tree.
     */
    out->data = cJSON_Duplicate(data, 1);
    /* The duplicated data is now owned by the cmd_t structure. */
    cJSON_Delete(root);
    return out;
}

/**
 * @brief Free a command structure.
 *
 * Releases both the duplicated JSON payload and the cmd_t structure.
 *
 * @param cmd Command structure to free. NULL is accepted.
 */
void cmd_free(cmd_t *cmd)
{
    if (!cmd)
        return;
    cJSON_Delete(cmd->data);
    free(cmd);
}