# inoAIDB



## Installation

### General path:

1. Install the base requirements:
    * Python 3.10+
    * nodejs
    * PostgreSQL (new database with empty schema; user must have CREATE TABLE privileges)
1. Create database in PostgreSQL
1. Create virtual environment for Python with `python3 -m venv .venv` and start it with `. .venv/bin/activate`
1. Inside the venv install dependecies with `python3 -m pip install -r requirements.txt`
1. Change into folder `frontend` and run `npm install` followed by `npm build`
1. Create configuartion file `config.ini` from template file [`config.ini.template`](/backend/app/config.ini.template) in `/backend/app/`.
1. Change the OAuth Signing Secret in configuation file

    Create private key (e.g. via openssl or xca) and place the base64-encoded DER as secret without line breaks.
1. Start `start_app.py` within folder where it is located with `python3 ./start_app`. This ensures that the path `./frontend/dist/` is valid.

1. Create language html files for imprint and dataprotection with the pattern name_lg.html (lg - language) from [`template_XX.html.template]`(/frontend/public/hdocs/template_XX.html.template)

TBD    If the configuaration file `config.ini` is not stored next to `myapp.py` start with `python3 .\myapp.py --config PathTo\myapp.ini`
1. If application startup is successful the database will be populated with an empty schema and the web interface will become available after a few seconds at `http://localhost:8000`.
1. In a production environment the web application should be used behind a reverse proxy to hold static assets in its cache and improve system performance.

### Setup for development

1. Create database in PostgreSQL
1. Create `config.ini` (see abvove)
1. Open workfolder
1. Create environment
1. Open terminal
1. `python3 -m pip install -r PyKeyInfoService/requirements.txt`
1. `cd ./backend/`
1. `python3 app/generate_frontend_env.py`
1. `cd ..`
1. `cd ./frontend/`
1. `npm install`
1. `npm run build`
1. `cd ..`
1. `python3 ./start_app.py`

### Initialise database

The database is populated automatically during the first application start. To use all functions of the application at least one user is needed as some functions are only available for an user who is logged in.

During the installation a first invite is create with with `SepcialInvite` as code.

Use Register or `/api/users/register` to create a first admin user by using the code `SepcialInvite`.


### Settings

### For unit testing

$env:APP_ENV = "test"
python -m pytest --cov=app --cov-report=term-missing

### Production

$env:APP_ENV="default"
uvicorn app.main:app --reload
