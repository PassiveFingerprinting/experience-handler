#include <stdio.h>
#include <string.h>
#include <sys/utsname.h>
#include <stdlib.h>

#include "handlers.h"
#include "protocol.h"

/**
 * @brief Handle the SYSTEM_INFO command.
 *
 * Collects basic system information using uname(), builds a JSON
 * response, and sends it back to the server.
 *
 * Response format:
 * {
 *     "type": 0,
 *     "payload": {
 *         "cmd": "SYSTEM_INFO",
 *         "result": {
 *             "name": "...",
 *             "release": "...",
 *             "version": "...",
 *             "machine": "..."
 *         }
 *     }
 * }
 *
 * @param cmd Received command structure.
 * @param sock Connected socket.
 * @return 0 on success, -1 on error.
 */
int handle_system_info(const cmd_t *cmd, int sock)
{
    struct utsname sys;
    /* Suppress unused parameter warning. */
    (void)cmd;
    cJSON *payload = NULL;
    cJSON *result = NULL;
    cJSON *root = NULL;
    char *json = NULL;

    printf("[agent] SYSTEM_INFO received\n");
    /* Retrieve system information. */
    if (uname(&sys) != 0) {
        perror("uname");
        return -1;
    }
    /* Create the payload section. */
    payload = cJSON_CreateObject();
    result = cJSON_CreateObject();
    /* Add the command name. */
    cJSON_AddStringToObject(payload, "cmd", "SYSTEM_INFO");
    /* Add the result object containing system information. */
    cJSON_AddItemToObject(payload, "result", result);
    cJSON_AddStringToObject(result, "name", sys.sysname);
    cJSON_AddStringToObject(result, "release", sys.release);
    cJSON_AddStringToObject(result, "version", sys.version);
    cJSON_AddStringToObject(result, "machine", sys.machine);
    /* Create the top-level message. */
    root = cJSON_CreateObject();
    cJSON_AddNumberToObject(root, "type", 0);
    cJSON_AddItemToObject(root, "payload", payload);
    /* Serialize the JSON document. */
    json = cJSON_PrintUnformatted(root);
    if (!json) {
        cJSON_Delete(root);
        return -1;
    }
    /* Send the serialized message. */
    send_frame(sock, json, strlen(json));
    free(json);
    cJSON_Delete(root);
    return 0;
}

/**
 * @brief Handle the DONE command.
 *
 * Sends an acknowledgment indicating that all requested commands
 * have been processed.
 *
 * Response format:
 * {
 *     "type": 0,
 *     "payload": {
 *         "cmd": "DONE",
 *         "result": {}
 *     }
 * }
 *
 * @param cmd Received command structure.
 * @param sock Connected socket.
 * @return 1 to indicate completion, or -1 on error.
 */
int handle_system_done(const cmd_t *cmd, int sock)
{
    /* Suppress unused parameter warning. */
    (void)cmd;

    printf("[agent] DONE received\n");

    /* Create the payload section. */
    cJSON *payload = cJSON_CreateObject();
    cJSON *result = cJSON_CreateObject();

    /* Add the command name. */
    cJSON_AddStringToObject(payload, "cmd", "DONE");

    /* Add an empty result object. */
    cJSON_AddItemToObject(payload, "result", result);

    /* Create the top-level message. */
    cJSON *root = cJSON_CreateObject();
    cJSON_AddNumberToObject(root, "type", 0);
    cJSON_AddItemToObject(root, "payload", payload);

    /* Serialize the JSON document. */
    char *json = cJSON_PrintUnformatted(root);
    if (!json) {
        cJSON_Delete(root);
        return -1;
    }

    /* Send the serialized message. */
    send_frame(sock, json, strlen(json));

    free(json);
    cJSON_Delete(root);

    return 1;
}