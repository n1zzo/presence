# presence
Semi-automatic presence verification tool

# Protocol Description

| **Title**      | Students List                         |
| **URL**        | `/list`                               |
| **Method**     | `GET`                                 |
| **URL Params** | **Required:** `section=STRING`        |
| **Response**   | `{"list": [{"codice_persona": STRING,
                               "matricola": STRING,
                               "nome": STRING,
                               "email": STRING,
                               "sessions": [SESSION, ...]}, ...],
                     "timestamp": INTEGER}`              |

