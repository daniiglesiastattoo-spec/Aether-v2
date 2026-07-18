#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AETHER - Motor de Evolución Estructural (EvolutionScanner)
"""
import os
import json
import time
import sqlite3
import hashlib
import traceback
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    requests = None

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
CATEGORIAS = ("parametros", "memoria", "arquitectura", "codigo", "rendimiento")

class EvolutionScanner:
    def __init__(self, db_path, groq_api_key, config_path=None, error_log_path=None, max_proposals_per_scan=3):
        self.db_path = db_path
        self.api_key = groq_api_key
        self.config_path = config_path
        self.error_log_path = error_log_path
        self.max_proposals = max_proposals_per_scan
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS evolution_proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE,
                    timestamp TEXT,
                    categoria TEXT,
                    titulo TEXT,
                    problema TEXT,
                    propuesta TEXT,
                    evidencia TEXT,
                    riesgo TEXT,
                    estado TEXT DEFAULT 'pendiente'
                )
            """)
