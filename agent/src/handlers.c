#include <stdio.h>
#include <string.h>
#include <sys/utsname.h>
#include <stdlib.h>

#include "handlers.h"
#include "protocol.h"

int handle_system_info(const cmd_t *cmd, int sock)
{
    struct utsname sys;

    printf("[agent] SYSTEM_INFO received\n");
    if (uname(&sys) != 0) {
        perror("uname");
        return -1 ;
    }
    // payload object
    cJSON *payload = cJSON_CreateObject();
    cJSON *result = cJSON_CreateObject();
    // cmd inside payload
    cJSON_AddStringToObject(payload, "cmd", "SYSTEM_INFO");
    // result inside payload
    cJSON_AddItemToObject(payload, "result", result);
    cJSON_AddStringToObject(result, "name", sys.sysname);
    cJSON_AddStringToObject(result, "release", sys.release);
    cJSON_AddStringToObject(result, "version", sys.version);
    cJSON_AddStringToObject(result, "machine", sys.machine);
    // full message envelope
    cJSON *root = cJSON_CreateObject();
    cJSON_AddNumberToObject(root, "type", 0);
    cJSON_AddItemToObject(root, "payload", payload);
    char *json = cJSON_PrintUnformatted(root);
    if (!json) {    
        cJSON_Delete(root);
        return -1;
    }
    send_frame(sock, json, strlen(json));
    free(json);
    cJSON_Delete(root);
}

int handle_system_done(const cmd_t *cmd, int sock)
{
    struct utsname sys;

    printf("[agent] DONE received\n");
    if (uname(&sys) != 0) {
        perror("uname");
        return -1;
    }
    // payload object
    cJSON *payload = cJSON_CreateObject();
    cJSON *result = cJSON_CreateObject();
    // cmd inside payload
    cJSON_AddStringToObject(payload, "cmd", "DONE");
    // result inside payload
    cJSON_AddItemToObject(payload, "result", result);
    // full message envelope
    cJSON *root = cJSON_CreateObject();
    cJSON_AddNumberToObject(root, "type", 0);
    cJSON_AddItemToObject(root, "payload", payload);
    char *json = cJSON_PrintUnformatted(root);
    if (!json) {
        cJSON_Delete(root);
        return -1;
    }
    send_frame(sock, json, strlen(json));
    free(json);
    cJSON_Delete(root);
    return 1;
}