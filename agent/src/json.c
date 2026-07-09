#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "json.h"
#include "cJSON.h"

/**
 * @brief Create a simple JSON message.
 *
 * Builds a JSON object containing a mandatory "type" field and an
 * optional "data" field.
 *
 * Example output:
 * {
 *     "type": "INFO",
 *     "data": "Hello"
 * }
 *
 * If @p data is NULL, the resulting object contains only the "type"
 * field.
 *
 * @param type Message type.
 * @param data Optional message payload.
 * @return Newly allocated JSON string, or NULL if serialization
 *         fails. The caller is responsible for freeing the returned
 *         string with free().
 */
char *json_create_message(const char *type, const char *data)
{
    cJSON *root = cJSON_CreateObject();
    char *out = NULL;

    /* Add the mandatory message type. */
    cJSON_AddStringToObject(root, "type", type);
    /* Add the optional data field if provided. */
    if (data)
        cJSON_AddStringToObject(root, "data", data);
    /* Serialize the JSON object into a compact string. */
    out = cJSON_PrintUnformatted(root);
    /* The serialized string is independent from the JSON object. */
    cJSON_Delete(root);
    return out;
}