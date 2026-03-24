"""Minimal relay bot: groups.json dagi guruhlardan kelgan barcha xabarlarni target guruhga yuboradi."""

import asyncio
import json
import os
from pathlib import Path
from typing import Set
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters


load_dotenv()

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
AGGREGATE_CHAT_ID_RAW = os.getenv("AGGREGATE_CHAT_ID", "") or os.getenv("AGGREGATE_CHAT_IDS", "")
GROUPS_PATH = Path(__file__).resolve().parent / "src" / "config" / "groups.json"
STATS_PATH = Path(__file__).resolve().parent / "src" / "config" / "forward_stats.json"
REPORT_INTERVAL_SECONDS = int(os.getenv("STATS_REPORT_INTERVAL_SECONDS", "3600"))
RETENTION_DAYS = 2

if not BOT_TOKEN:
    raise ValueError("❌ TG_BOT_TOKEN topilmadi! .env faylni tekshiring")


def parse_aggregate_chat_id(raw_value: str) -> int:
    if not raw_value:
        raise ValueError("❌ AGGREGATE_CHAT_ID topilmadi! .env faylni tekshiring")

    parsed_ids = []
    for item in raw_value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            parsed_ids.append(int(item))
        except ValueError:
            print(f"⚠️ Noto'g'ri AGGREGATE_CHAT_ID qiymati: {item}")

    if not parsed_ids:
        raise ValueError("❌ To'g'ri AGGREGATE_CHAT_ID topilmadi")

    if len(parsed_ids) > 1:
        print("⚠️ Bir nechta AGGREGATE_CHAT_ID berilgan, birinchisi ishlatiladi")

    return parsed_ids[0]


def load_group_chat_ids() -> Set[int]:
    if not GROUPS_PATH.exists():
        print(f"⚠️ groups.json topilmadi: {GROUPS_PATH}")
        return set()

    try:
        with GROUPS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"❌ groups.json o'qishda xatolik: {exc}")
        return set()

    raw_groups = data.get("groups", []) if isinstance(data, dict) else []
    parsed: Set[int] = set()

    for item in raw_groups:
        if isinstance(item, int):
            parsed.add(item)
            continue
        if isinstance(item, str):
            item = item.strip()
            if not item:
                continue
            try:
                parsed.add(int(item))
            except ValueError:
                print(f"⚠️ groups.json da int bo'lmagan qiymat o'tkazib yuborildi: {item}")

    return parsed


def load_stats() -> dict:
    if not STATS_PATH.exists():
        return {"days": {}}

    try:
        with STATS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"days": {}}
        days = data.get("days", {})
        if not isinstance(days, dict):
            return {"days": {}}
        return {"days": days}
    except Exception as exc:
        print(f"⚠️ Statistika JSON o'qishda xatolik: {exc}")
        return {"days": {}}


def save_stats(stats: dict):
    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATS_PATH.open("w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def chat_link(chat_id: int, username: str = "") -> str:
    if username:
        return f"https://t.me/{username}"
    if str(chat_id).startswith("-100"):
        internal_id = str(chat_id)[4:]
        return f"https://t.me/c/{internal_id}/1"
    return f"https://t.me/c/{abs(chat_id)}/1"


def trim_stats(stats: dict):
    days = stats.get("days", {})
    if not isinstance(days, dict):
        stats["days"] = {}
        return

    sorted_dates = sorted(days.keys(), reverse=True)
    keep = set(sorted_dates[:RETENTION_DAYS])
    stats["days"] = {k: v for k, v in days.items() if k in keep}


def add_forward_stat(chat_id: int, chat_username: str = ""):
    stats = load_stats()
    day_key = datetime.now().strftime("%Y-%m-%d")

    days = stats.setdefault("days", {})
    day_stat = days.setdefault(day_key, {"total": 0, "groups": {}})
    day_stat["total"] = int(day_stat.get("total", 0)) + 1

    groups = day_stat.setdefault("groups", {})
    group_key = str(chat_id)
    group_stat = groups.setdefault(group_key, {"count": 0, "username": ""})
    group_stat["count"] = int(group_stat.get("count", 0)) + 1
    if chat_username:
        group_stat["username"] = chat_username

    trim_stats(stats)
    save_stats(stats)


def build_stats_report_text() -> str:
    stats = load_stats()
    days = stats.get("days", {})
    if not days:
        return "📊 Statistika hozircha yo'q."

    lines = ["📊 Forward statistikasi (oxirgi 2 kun)"]
    for day_key in sorted(days.keys(), reverse=True)[:RETENTION_DAYS]:
        day_stat = days.get(day_key, {})
        total = int(day_stat.get("total", 0))
        lines.append("")
        lines.append(f"📅 {day_key}")
        lines.append(f"Jami: {total} ta")

        groups = day_stat.get("groups", {})
        sortable = sorted(
            groups.items(),
            key=lambda item: int(item[1].get("count", 0)),
            reverse=True,
        )
        for group_id_str, info in sortable:
            try:
                gid = int(group_id_str)
            except ValueError:
                continue
            username = str(info.get("username", "") or "").strip().lstrip("@")
            link = chat_link(gid, username)
            count = int(info.get("count", 0))
            lines.append(f"- <a href=\"{link}\">{gid}</a>: {count} ta")

    return "\n".join(lines)


async def periodic_stats_sender(application: Application):
    while True:
        await asyncio.sleep(max(60, REPORT_INTERVAL_SECONDS))
        try:
            report_text = build_stats_report_text()
            await application.bot.send_message(
                chat_id=AGGREGATE_CHAT_ID,
                text=report_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            print("📊 Statistika yuborildi")
        except Exception as exc:
            print(f"⚠️ Statistikani yuborishda xatolik: {exc}")


AGGREGATE_CHAT_ID = parse_aggregate_chat_id(AGGREGATE_CHAT_ID_RAW)
ALLOWED_CHAT_IDS = load_group_chat_ids()

if not ALLOWED_CHAT_IDS:
    print("⚠️ groups.json bo'sh. Hech qaysi guruhdan xabar forward qilinmaydi.")


async def forward_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    from_chat_id = message.chat_id
    if from_chat_id not in ALLOWED_CHAT_IDS:
        return

    try:
        await context.bot.copy_message(
            chat_id=AGGREGATE_CHAT_ID,
            from_chat_id=from_chat_id,
            message_id=message.message_id,
        )
        add_forward_stat(from_chat_id, message.chat.username if message.chat else "")
        print(f"✅ Copy: {from_chat_id} -> {AGGREGATE_CHAT_ID} | msg={message.message_id}")
    except Exception as copy_exc:
        print(f"❌ Copy muvaffaqiyatsiz: {copy_exc}")


async def post_init(application: Application):
    print("\n" + "=" * 60)
    print("🤖 Minimal relay bot ishga tushmoqda")
    print("=" * 60)
    print(f"🎯 Target aggregate group: {AGGREGATE_CHAT_ID}")
    if ALLOWED_CHAT_IDS:
        print("📥 Kuzatilayotgan guruhlar:")
        for chat_id in sorted(ALLOWED_CHAT_IDS):
            print(f"  - {chat_id}")
    else:
        print("⚠️ groups.json bo'sh. Xabar forward qilinmaydi")
    print(f"🕒 Statistika intervali: {max(60, REPORT_INTERVAL_SECONDS)} soniya")
    if not STATS_PATH.exists():
        save_stats({"days": {}})
    application.create_task(periodic_stats_sender(application))
    print("=" * 60 + "\n")


def main():
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    application.add_handler(
        MessageHandler(
            filters.ALL & filters.ChatType.GROUPS,
            forward_group_message,
        )
    )

    print("🚀 Relay bot ishga tushirilmoqda...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
