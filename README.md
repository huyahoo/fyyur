## Create a Virtual Environment
```bash
python -m venv env
source env/bin/activate
```
## Install Dependencies
```bash
cd fyyur
pip install -r requirements.txt

npm init -y
npm install bootstrap@3
```

## Create Database
```bash
psql postgres

postgres=# CREATE DATABASE fyyur;
CREATE DATABASE
postgres=# 
```

## Setup Flask-Migrate
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Seed the data base
```bash
python seed.py
```

## Run the development server
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
python3 app.py
```