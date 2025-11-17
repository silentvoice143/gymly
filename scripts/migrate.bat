@echo off
call venv\Scripts\activate
flask db migrate -m "Auto migration"
