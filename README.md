# bazunie


https://www.youtube.com/watch?v=sdZMlv1ZSK8 - filmik z łączeniem się do bazy na localhost (działa)

Żeby program działał trzeba stworzyć plik config.py z taką zawartością:
```
# Configuration for the MySQL connection
db_config = {
    'user':'<uzytkownik bazy>',
    'host':'<ip>',
    'database':'<nazwa bazy>',
    'passwd':'<haslo>',
    'port': <port na ktorym uruchomoiona jest baza>
}
```