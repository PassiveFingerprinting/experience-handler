#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "json.h"
#include "cJSON.h"

char *json_create_message(const char *type, const char *data) {
    cJSON *root = cJSON_CreateObject();
    char *out = NULL;

    cJSON_AddStringToObject(root, "type", type);
    if (data)
        cJSON_AddStringToObject(root, "data", data);
    out = cJSON_PrintUnformatted(root);
    cJSON_Delete(root);
    return out;
}
