# presence
## Semi-automatic presence verification tool

# Protocol Description

## Students List

| API            | Description                    |
|----------------|--------------------------------|
| **URL**        | `/list`                        |
| **Method**     | `GET`                          |
| **URL Params** | **Required:** `section=STRING` |

### Response Example

```
{"list": [{"codice_persona": STRING,
           "matricola": STRING,
           "nome": STRING,
           "email": STRING,
           "sessions": []}, ...],
 "timestamp": INTEGER }
```

## Registered Students

| API            | Description                                   |
|----------------|-----------------------------------------------|
| **URL**        | `/registered`                                 |
| **Method**     | `GET`                                         |
| **URL Params** | **Required:** `section=STRING, labid=INTEGER` |

### Response Example

```
{"list": [{"codice_persona": STRING,
           "matricola": STRING,
           "nome": STRING,
           "email": STRING,
           "sessions": [SESSION, ...]}, ...],
 "timestamp": INTEGER }
```

## Not Registered Students

| API            | Description                                   |
|----------------|-----------------------------------------------|
| **URL**        | `/notyet`                                     |
| **Method**     | `GET`                                         |
| **URL Params** | **Required:** `section=STRING, labid=INTEGER` |

### Response Example

```
{"list": [{"codice_persona": STRING,
           "matricola": STRING,
           "nome": STRING,
           "email": STRING,
           "sessions": [SESSION, ...]}, ...],
 "timestamp": INTEGER }
```

## Register Student

| API             | Description                                              |
|-----------------|----------------------------------------------------------|
| **URL**         | `/register`                                              |
| **Method**      | `POST`                                                   |
| **Body Params** | **Required:** `section=STRING, id=STRING, labid=INTEGER` |

### Response Example

```
{"registered": [{"codice_persona": STRING,
                 "matricola": STRING,
                 "nome": STRING,
                 "email": STRING,
                 "sessions": [SESSION, ...]}, ...],
 "timestamp": INTEGER }
```

## Control Timer

| API             | Description                                                                            |
|-----------------|----------------------------------------------------------------------------------------|
| **URL**         | `/timer`                                                                               |
| **Method**      | `POST`                                                                                 |
| **Body Params** | **Required:** `section=STRING, id=STRING, labid=INTEGER, action=["start"&#124;"stop"]` |

### Response Example

```
{"registered": [{"codice_persona": STRING,
                 "matricola": STRING,
                 "nome": STRING,
                 "email": STRING,
                 "sessions": [SESSION, ...]}, ...],
 "timestamp": INTEGER }
```

## Groups Composition

| API            | Description                    |
|----------------|--------------------------------|
| **URL**        | `/groups`                      |
| **Method**     | `GET`                          |
| **URL Params** | **Required:** `section=STRING` |

### Response Example

```
{"list": [{"id": INTEGER,
           "members": [{"codice_persona": STRING,
                        "matricola": STRING,
                        "nome": STRING,
                        "email": STRING}, ...]}, ...],
 "timestamp": INTEGER }
```

## Groups Info

| API            | Description                                     |
|----------------|-------------------------------------------------|
| **URL**        | `/groupinfo`                                    |
| **Method**     | `GET`                                           |
| **URL Params** | **Required:** `section=STRING, groupid=INTEGER` |

### Response Example

```
{"id": INTEGER,
 "score": INTEGER,
 "repo": STRING,
 "compiles": BOOLEAN,
 "passed_tests": INTEGER,
 "sessions": [SESSION, ...],
 "timestamp": INTEGER }
```

## Curl Examples

### Get students list

```
curl $BASE_URL'/list?section=test'
```

### Register a new student

```
curl -X POST -d '{ "id": $MATRICOLA, "labid": 1 , "section": "test"}' $BASE_URL'/register'
```

