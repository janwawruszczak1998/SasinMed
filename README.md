### How to SasinMed:

### 1 venv - w folderze głównym SasinMed

```python3 -m venv venv
. venv/bin/activate
```

### 2 flask

```pip3 install flask
pip3 install flask-admin
pip3 install flask-migrate
```

### 3 postgreSQL

```pip3 install psycopg2
sudo apt install libpq-dev
sudo apt-get -y install postgresql
```

Działanie na silniku bazy postawionym na postgesie

```sudo su postgres```

Następnie odpalamy odpowiedni program:
```psql```
