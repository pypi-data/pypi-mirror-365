# POOPSQL

drop in replacement for sqlite for multi writing using tcp with serialized writes

not really a replacement more like a wrapper

## install

```bash
pip install sqlpoop
```

## example

```python
from sqlpoop import Sqlpoop

db = Sqlpoop(passcode="poopypassword")

db.execute("create table if not exists users (id integer primary key, name text)")
db.execute("insert into users (name) values (?)", ("bob",))
result = db.execute("select * from users")
print(result.fetchall())
```

## cursor if youre into that

```python
cursor = db.cursor()
cursor.execute("select * from users")
print(cursor.fetchone())
```

## config

```python
Sqlpoop(
    dbfile="data.db",
    passcode="apoopypassword",
    host="0.0.0.0",
    port=5000
)
```

## json wire format

send json with a newline over tcp to 127.0.0.1:5000 or whatever you set

### request

```json
{
    "passcode": "apoopypassword",
    "query": "select * from users where id = ?",
    "params": [1]
}
```

### response

```json
{
    "status": "ok",
    "rows": [[1, "bob"]]
}
```

or if you suck:

```json
{   
    "status": "error",
    "error": "you messed up"
}
```
## clients

if your running poopsql on another script and want to connect to it without starting a new one

```python
from sqlpoop import SqlpoopClient

db = SqlpoopClient(passcode="poopypassword", host="127.0.0.1", port=5000)

db.execute("insert into users (name) values (?)", ("alice",))
print(db.execute("select * from users").fetchall())
```

## facts

- reads are instant
- writes go into a queue and happen one at a time
- sqlite in wal mode
- yes multiple clients can write at once
- no it doesnt use http
- yes it closes the socket after each request
- no its not secure dont put it on the internet

## shutdown

```python
db.close()
```

## why

because sqlite doesnt like multiple writers and i do