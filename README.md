### How to SasinMed:

### 1 venv - w folderze głównym SasinMed

```
python3 -m venv venv
. venv/bin/activate
```

### 2 flask

```
pip3 install -r requirements.txt
```

### 3 postgreSQL

```
pip3 install psycopg2
sudo apt install libpq-dev
sudo apt-get -y install postgresql
sudo apt-get -y install postgresql-contrib
```

Działanie na silniku bazy postawionym na postgesie

```sudo su postgres```

Następnie odpalamy odpowiedni program:
```psql```

Tworzymy lokalnie bazę danych:
```
CREATE DATABASE sasinmeddb;
CREATE USER sasinmed WITH PASSWORD 'w4lepsze';
ALTER ROLE sasinmed SET client_encoding TO 'utf8';
ALTER ROLE sasinmed SET default_transaction_isolation TO 'read committed';
ALTER ROLE sasinmed SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sasinmeddb TO sasinmed;
```
