@echo off
cd backend
venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 1112 --reload
