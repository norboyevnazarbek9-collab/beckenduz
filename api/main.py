from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "app_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_store (
            id INTEGER PRIMARY KEY,
            data TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM app_store WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        empty_data = json.dumps({"users": [], "posts": {}, "bookings": [], "ratings": [], "dayOffs": {}, "favorites": {}})
        cursor.execute("INSERT INTO app_store (id, data) VALUES (1, ?)", (empty_data,))
    conn.commit()
    conn.close()

init_db()

class DBData(BaseModel):
    data: dict

@app.get("/api/db")
def get_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM app_store WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/db")
def save_db(payload: DBData):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE app_store SET data = ? WHERE id = 1", (json.dumps(payload.data),))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Saqlashda xatolik yuz berdi")