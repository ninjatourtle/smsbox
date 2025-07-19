import json
import logging
import os
import sqlite3
import tempfile
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import openai
from pdfminer.high_level import extract_text as pdf_extract
import docx2txt
import pytesseract
from PIL import Image
from fpdf import FPDF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_PASSWORD = os.getenv("BOT_PASSWORD", "")

openai_client = openai.Client(api_key=OPENAI_API_KEY)

DB_PATH = "bot.db"
AUTH_USERS = set()

conn = sqlite3.connect(DB_PATH)
conn.execute(
    """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
)
conn.execute(
    """CREATE TABLE IF NOT EXISTS documents (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            storage_path TEXT
        )"""
)
conn.execute(
    """CREATE TABLE IF NOT EXISTS analyses (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER,
            risk_score REAL,
            summary TEXT,
            issues TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
)
conn.commit()

def extract_file_text(path: str) -> str:
    lower = path.lower()
    try:
        if lower.endswith(".pdf"):
            return pdf_extract(path)
        if lower.endswith(".docx"):
            return docx2txt.process(path)
        if lower.endswith(".doc"):
            return docx2txt.process(path)
        if lower.endswith((".png", ".jpg", ".jpeg")):
            return pytesseract.image_to_string(Image.open(path), lang="rus+eng")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as exc:
        logger.error("Ошибка чтения файла: %s", exc)
        return ""

def build_pdf(summary: str, issues: list[str], risk: float, filename: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, txt=f"Файл: {filename}", ln=1)
    pdf.cell(0, 10, txt=f"Риск: {risk}%", ln=1)
    pdf.multi_cell(0, 10, txt="Резюме:\n" + summary)
    if issues:
        pdf.multi_cell(0, 10, txt="Подводные камни:")
        for item in issues:
            pdf.multi_cell(0, 10, txt="- " + item)
    tmp = tempfile.mktemp(suffix=".pdf")
    pdf.output(tmp)
    return tmp

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Укажите пароль: /login <пароль>")
        return
    if context.args[0] == BOT_PASSWORD:
        AUTH_USERS.add(update.effective_user.id)
        conn.execute(
            "INSERT OR IGNORE INTO users(user_id, username) VALUES (?, ?)",
            (update.effective_user.id, update.effective_user.username or ""),
        )
        conn.commit()
        await update.message.reply_text("Пароль принят. Отправьте договор файлом.")
    else:
        await update.message.reply_text("Неверный пароль.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Отправьте /login <пароль> для начала работы.")

async def analyze_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in AUTH_USERS:
        await update.message.reply_text("Сначала войдите командой /login <пароль>.")
        return
    if not update.message.document:
        await update.message.reply_text("Пожалуйста, отправьте договор файлом.")
        return

    document = update.message.document
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, document.file_name or "contract")
        new_file = await document.get_file()
        await new_file.download_to_drive(file_path)
        text = extract_file_text(file_path)

    if not text.strip():
        await update.message.reply_text("Не удалось извлечь текст из файла.")
        return

    try:
        truncated = text[:15000]
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Вы юридический помощник. Проанализируйте договор и верните JSON "
                        "с ключами summary (короткий текст), risks (список строк) и "
                        "risk_score (число от 0 до 100). Отвечайте по-русски."
                    ),
                },
                {"role": "user", "content": truncated},
            ],
        )
        data = json.loads(response.choices[0].message.content)
    except Exception as exc:
        logger.error("OpenAI API request failed: %s", exc)
        await update.message.reply_text("Не удалось проанализировать договор.")
        return

    summary = data.get("summary", "")
    issues = data.get("risks", [])
    risk_score = data.get("risk_score", 0)

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents(user_id, filename, storage_path) VALUES (?, ?, ?)",
        (update.effective_user.id, document.file_name, "")
    )
    doc_id = cur.lastrowid
    cur.execute(
        "INSERT INTO analyses(doc_id, risk_score, summary, issues) VALUES (?, ?, ?, ?)",
        (doc_id, risk_score, summary, json.dumps(issues, ensure_ascii=False))
    )
    analysis_id = cur.lastrowid
    conn.commit()

    text_out = f"Риск: {risk_score}%\n\nРезюме:\n{summary}"
    if issues:
        text_out += "\n\nПодводные камни:\n" + "\n".join(f"- {i}" for i in issues)
    text_out += f"\n\nID анализа: {analysis_id}"

    await update.message.reply_text(text_out)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in AUTH_USERS:
        await update.message.reply_text("Сначала войдите командой /login <пароль>.")
        return
    rows = conn.execute(
        "SELECT analysis_id, risk_score, analyzed_at FROM analyses JOIN documents USING(doc_id) WHERE user_id=? ORDER BY analyzed_at DESC LIMIT 5",
        (update.effective_user.id,),
    ).fetchall()
    if not rows:
        await update.message.reply_text("История пуста.")
        return
    text_lines = [f"{r[0]} — риск {r[1]}% ({r[2]})" for r in rows]
    await update.message.reply_text("\n".join(text_lines))

async def export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in AUTH_USERS:
        await update.message.reply_text("Сначала войдите командой /login <пароль>.")
        return
    if not context.args:
        await update.message.reply_text("Укажите ID анализа: /export <id>")
        return
    aid = context.args[0]
    row = conn.execute(
        """SELECT summary, issues, risk_score, filename FROM analyses
           JOIN documents USING(doc_id)
           WHERE analysis_id=? AND user_id=?""",
        (aid, update.effective_user.id),
    ).fetchone()
    if not row:
        await update.message.reply_text("Анализ не найден.")
        return
    summary, issues_json, risk, filename = row
    issues = json.loads(issues_json or "[]")
    pdf_path = build_pdf(summary, issues, risk, filename)
    await update.message.reply_document(document=open(pdf_path, "rb"))
    os.remove(pdf_path)


def main() -> None:
    if not TELEGRAM_TOKEN or not OPENAI_API_KEY or not BOT_PASSWORD:
        raise SystemExit(
            "Необходимо задать TELEGRAM_TOKEN, OPENAI_API_KEY и BOT_PASSWORD"
        )
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("export", export_cmd))
    app.add_handler(MessageHandler(filters.Document.ALL, analyze_document))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
