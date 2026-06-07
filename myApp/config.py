ENV="development"
DEBUG=True
SEND_FILE_MAX_AGE_DEFAULT = 0
SECRET_KEY ="pouletteetpoulet"

WEB_SERVER={
    "host": "localhost",
    "port":8080,
}

DB_SERVER={
    "user":"root",
    "password":"",
    "host":"localhost",
    "port": 3306,
    "database": "ienac25_flashcards_groupea",
    "raise_on_warnings": True
}

COLOR={'header': '\033[95m',
       'blue': '\033[94m',
       'green': '\033[92m',
       'orange': '\033[93m',
       'red': '\033[31m',
       'end': '\033[0m',}
