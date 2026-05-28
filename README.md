python -m venv .venv
.venv\\Scripts\\activate

pip install -r requirements.txt

Rename/copy `.env.example` to `.env` and set values:

Copy-Item .env.example .env

Create the MySQL schema:

Option A (recommended): run the initializer:

.venv\\Scripts\\python.exe database\\init_db.py

Option B: run `database/schema.sql` in your MySQL client (it creates `virtual_classroom` and all tables).

Start the app:

python app.py
