import sqlite3, json
from .config import DB_PATH

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            score REAL NOT NULL,
            language TEXT NOT NULL,
            payload TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            added_at TEXT NOT NULL,
            content TEXT NOT NULL
        )""")

def save_audit(result):
    init_db()
    with _connect() as conn:
        conn.execute("INSERT INTO audits(title,created_at,score,language,payload) VALUES(?,?,?,?,?)",
            (result["title"],result["created_at"],result["score"],result["language"],json.dumps(result,ensure_ascii=False)))

def list_audits(limit=100):
    with _connect() as conn:
        rows = conn.execute("SELECT id,title,created_at,ROUND(score,1) AS score,language FROM audits ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    return [dict(r) for r in rows]

def get_dashboard_stats():
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) n, AVG(score) avg FROM audits").fetchone()
        docs = row["n"]
        risks = 0
        for r in conn.execute("SELECT payload FROM audits"):
            try:
                payload = json.loads(r["payload"])
                risks += payload["counts"]["risk"]
            except Exception:
                pass
    return {"audits":docs,"documents":docs,"average_score":row["avg"],"risk_items":risks}

def add_knowledge(filename, content, added_at):
    with _connect() as conn:
        conn.execute("INSERT INTO knowledge(filename,added_at,content) VALUES(?,?,?)",(filename,added_at,content))

def get_knowledge():
    with _connect() as conn:
        return [dict(r) for r in conn.execute("SELECT id,filename,added_at,content FROM knowledge ORDER BY id DESC")]

def delete_knowledge(item_id):
    with _connect() as conn:
        conn.execute("DELETE FROM knowledge WHERE id=?",(item_id,))


def get_audit_payloads(limit=100):
    """Return decoded audit payloads for dashboard visualisations."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT payload FROM audits ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    results = []
    for row in rows:
        try:
            results.append(json.loads(row["payload"]))
        except (TypeError, json.JSONDecodeError):
            continue
    return results
