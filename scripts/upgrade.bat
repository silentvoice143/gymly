@echo off
call venv\Scripts\activate
flask db upgrade
