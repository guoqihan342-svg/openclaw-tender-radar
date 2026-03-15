#!/usr/bin/env python3
"""
极简数据库初始化 - SQLite单文件
"""

import sqlite3
import os

DB_PATH = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/data/tender_radar.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 只创建最核心的3个表
    
    # 1. 招标信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tenders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        budget TEXT,
        region TEXT,
        deadline TEXT,
        category TEXT,
        purchaser TEXT,
        url TEXT,
        created_date DATE DEFAULT CURRENT_DATE
    )
    ''')
    
    # 2. 订阅用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        plan TEXT DEFAULT 'free',  -- free/standard/premium
        status TEXT DEFAULT 'active',
        created_date DATE DEFAULT CURRENT_DATE
    )
    ''')
    
    # 3. 支付记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscriber_id INTEGER,
        amount INTEGER,
        plan TEXT,
        pay_method TEXT,
        pay_date DATE DEFAULT CURRENT_DATE,
        status TEXT DEFAULT 'pending'
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DB_PATH}")

if __name__ == "__main__":
    init_db()
