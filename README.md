### How to SasinMed:

### 1 update i upgrade

```
sudo apt update
sudo apt upgrade
```

### 2 venv - w folderze głównym SasinMed

```
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
```

### 3 postgreSQL

```
sudo apt install libpq-dev
sudo apt-get -y install postgresql
sudo apt-get -y install postgresql-contrib
```

Działamy na użytkowniku postgres

```
sudo su postgres
```

Następnie uruchamiamy odpowiedni program:
```
psql
```

Tworzymy lokalnie bazę danych:
```
CREATE DATABASE sasinmeddb;
CREATE USER sasinmed WITH PASSWORD 'w4lepsze';
ALTER ROLE sasinmed SET client_encoding TO 'utf8';
ALTER ROLE sasinmed SET default_transaction_isolation TO 'read committed';
ALTER ROLE sasinmed SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sasinmeddb TO sasinmed;
```
