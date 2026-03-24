"""
Guruhlarni real-time monitoring qilish va aggregate guruhga jo'natish
Telethon (userbot) - guruhlarni tinglash
python-telegram-bot (bot API) - aggregate guruhga yuborish
"""

import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from telethon import TelegramClient, events
from telethon.tl.types import (
    PeerUser,
    PeerChat,
    PeerChannel,
    MessageMediaDocument,
    MessageMediaPhoto,
    MessageMediaGeo,
    MessageMediaContact,
    MessageMediaWebPage,
)
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime

# .env faylni yuklash
load_dotenv()

# Konfiguratsiya
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = os.getenv('TG_SESSION_NAME', 'sessions/userbot_session')
BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
AGGREGATE_CHAT_ID = os.getenv('AGGREGATE_CHAT_IDS', '').split(',')[0].strip()


def load_groups():
    """groups.json dan guruh ID larini yuklash"""
    groups_file = Path("src/config/groups.json")
    if groups_file.exists():
        with open(groups_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [int(g) for g in data.get('groups', [])]
    return []


def get_sender_info(message):
    """Habar yuboruvchi haqida ma'lumot"""
    sender_type = "Unknown"
    sender_name = "Unknown"
    sender_username = None

    # Forward qilingan habar
    if message.forward:
        sender_type = "Forward"
        if message.forward.from_name:
            sender_name = message.forward.from_name
        elif message.forward.from_id:
            if isinstance(message.forward.from_id, PeerUser):
                sender_type = "Forward (User)"
            elif isinstance(message.forward.from_id, PeerChannel):
                sender_type = "Forward (Channel)"
        return sender_type, sender_name, sender_username

    # Oddiy habar
    sender = message.sender
    if sender:
        # Bot
        if hasattr(sender, 'bot') and sender.bot:
            sender_type = "Bot"
            sender_name = getattr(sender, 'first_name', 'Bot')
            sender_username = getattr(sender, 'username', None)
        # Kanal
        elif hasattr(sender, 'broadcast'):
            sender_type = "Channel"
            sender_name = getattr(sender, 'title', 'Channel')
            sender_username = getattr(sender, 'username', None)
        # Foydalanuvchi
        else:
            sender_type = "User"
            first_name = getattr(sender, 'first_name', '')
            last_name = getattr(sender, 'last_name', '')
            sender_name = f"{first_name} {last_name}".strip() or "User"
            sender_username = getattr(sender, 'username', None)

    return sender_type, sender_name, sender_username


def get_media_info(message):
    """Media haqida ma'lumot"""
    if not message.media:
        return None

    media_type = type(message.media).__name__

    media_map = {
        'MessageMediaPhoto': '📷 Foto',
        'MessageMediaDocument': '📄 Fayl',
        'MessageMediaGeo': '📍 Lokatsiya',
        'MessageMediaContact': '👤 Kontakt',
        'MessageMediaWebPage': '🔗 Web sahifa',
        'MessageMediaPoll': '📊 So\'rovnoma',
    }

    return media_map.get(media_type, f'📎 {media_type}')


def escape_html(text):
    """HTML maxsus belgilarni escape qilish"""
    if not text:
        return ""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))


async def format_message(message, group_title):
    """
    Habarni formatlash - barcha habarlarni bir xil formatda (HTML)
    """
    sender_type, sender_name, sender_username = get_sender_info(message)
    media_info = get_media_info(message)

    # Escape qilish
    group_title = escape_html(group_title)
    sender_name = escape_html(sender_name)
    sender_type = escape_html(sender_type)

    # Asosiy header
    header = f"📨 <b>Yangi habar: {group_title}</b>\n"
    header += f"{'─' * 40}\n"

    # Yuboruvchi ma'lumotlari
    sender_line = f"👤 <b>Yuboruvchi:</b> {sender_name}"
    if sender_username:
        sender_line += f" (@{sender_username})"
    sender_line += f"\n📋 <b>Turi:</b> {sender_type}\n"

    # Vaqt
    time_line = f"🕐 <b>Vaqt:</b> {message.date.strftime('%Y-%m-%d %H:%M:%S')}\n"

    # Media
    media_line = ""
    if media_info:
        media_line = f"📎 <b>Media:</b> {media_info}\n"

    # Matn
    text_line = ""
    if message.text:
        # Matnni escape qilish va cheklash
        escaped_text = escape_html(message.text)
        if len(escaped_text) > 500:
            escaped_text = escaped_text[:500] + "..."
        text_line = f"\n💬 <b>Habar:</b>\n{escaped_text}\n"

    # To'liq xabar
    formatted = header + sender_line + time_line + media_line + text_line
    formatted += f"{'─' * 40}"

    return formatted


async def send_to_aggregate(bot, message, group_title):
    """
    Habarni Bot API orqali aggregate guruhga jo'natish
    """
    try:
        if not AGGREGATE_CHAT_ID:
            print("⚠️  AGGREGATE_CHAT_ID o'rnatilmagan!")
            return

        # Habarni formatlash
        formatted_text = await format_message(message, group_title)

        # Media bilan habar yuborish
        if message.media:
            # Media faylni yuklab olish
            try:
                # Telethon orqali media yuklab olish
                file_path = await message.download_media(file=f"temp_media_{message.id}")

                if file_path:
                    # Bot API orqali yuborish
                    if isinstance(message.media, MessageMediaPhoto):
                        await bot.send_photo(
                            chat_id=AGGREGATE_CHAT_ID,
                            photo=open(file_path, 'rb'),
                            caption=formatted_text,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await bot.send_document(
                            chat_id=AGGREGATE_CHAT_ID,
                            document=open(file_path, 'rb'),
                            caption=formatted_text,
                            parse_mode=ParseMode.HTML
                        )

                    # Temp faylni o'chirish
                    import os as os_module
                    if os_module.path.exists(file_path):
                        os_module.remove(file_path)
                else:
                    # Media yuklab olinmasa, faqat matn
                    await bot.send_message(
                        chat_id=AGGREGATE_CHAT_ID,
                        text=formatted_text,
                        parse_mode=ParseMode.HTML
                    )
            except Exception as media_error:
                print(f"⚠️  Media yuklashda xatolik: {media_error}")
                # Media xatolik bo'lsa, faqat matn yuborish
                await bot.send_message(
                    chat_id=AGGREGATE_CHAT_ID,
                    text=formatted_text,
                    parse_mode=ParseMode.HTML
                )
        else:
            # Faqat matn
            await bot.send_message(
                chat_id=AGGREGATE_CHAT_ID,
                text=formatted_text,
                parse_mode=ParseMode.HTML
            )

        print(f"✅ Habar jo'natildi: {group_title}")

    except Exception as e:
        print(f"❌ Xatolik (jo'natish): {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Asosiy funksiya"""
    # Guruhlarni yuklash
    groups = load_groups()

    if not groups:
        print("❌ Guruhlar topilmadi. groups.json faylini tekshiring.")
        return

    if not AGGREGATE_CHAT_ID:
        print("❌ AGGREGATE_CHAT_IDS .env faylida o'rnatilmagan!")
        return

    if not BOT_TOKEN:
        print("❌ TG_BOT_TOKEN .env faylida o'rnatilmagan!")
        return

    print(f"✅ {len(groups)} ta guruh monitoring qilinadi")
    print(f"📤 Aggregate guruh: {AGGREGATE_CHAT_ID}\n")

    # Telethon client (guruhlarni tinglash uchun)
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    # Bot API (aggregate guruhga yuborish uchun)
    bot = Bot(token=BOT_TOKEN)

    try:
        # Telethon client ishga tushirish
        await client.start()
        me = await client.get_me()
        print(f"✅ Userbot ishga tushdi: {me.first_name} (@{me.username})")

        # Bot API tekshirish
        bot_me = await bot.get_me()
        print(f"✅ Bot API ishga tushdi: {bot_me.first_name} (@{bot_me.username})")

        # Aggregate guruhni tekshirish
        print(f"\n📤 Aggregate guruhga ulanish: {AGGREGATE_CHAT_ID}")
        try:
            agg_chat = await bot.get_chat(AGGREGATE_CHAT_ID)
            print(f"✅ Aggregate guruh: {agg_chat.title}\n")
        except Exception as e:
            print(f"❌ Aggregate guruhga ulanib bo'lmadi: {e}")
            print("💡 Bot guruhga a'zo ekanligini va ID to'g'riligini tekshiring.\n")
            return

        print(f"🔄 Guruhlarni tinglayapman...\n")
        print("=" * 60)

        # Guruh nomlari
        for group_id in groups:
            try:
                entity = await client.get_entity(group_id)
                title = getattr(entity, 'title', 'Unknown')
                print(f"   📂 {title} ({group_id})")
            except Exception as e:
                print(f"   ❌ {group_id}: {e}")

        print("=" * 60)
        print("\n💡 Bot ishlamoqda. To'xtatish uchun Ctrl+C bosing.\n")

        # Habar handler (bot ni closure orqali oladi)
        @client.on(events.NewMessage(chats=groups))
        async def handler(event):
            message = event.message
            chat = await event.get_chat()
            group_title = getattr(chat, 'title', 'Unknown Group')

            # Konsolga log
            sender_type, sender_name, sender_username = get_sender_info(message)
            print(f"\n📩 Yangi habar: {group_title}")
            print(f"   👤 {sender_name} ({sender_type})")
            if message.text:
                preview = message.text[:50] + "..." if len(message.text) > 50 else message.text
                print(f"   💬 {preview}")

            # Aggregate guruhga jo'natish (Bot API orqali)
            await send_to_aggregate(bot, message, group_title)

        # Cheksiz kutish
        await client.run_until_disconnected()

    except KeyboardInterrupt:
        print("\n\n⏹️  Bot to'xtatildi")
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
        print("👋 Telegram bilan aloqa uzildi")


if __name__ == "__main__":
    print("🚀 Guruhlarni monitoring qilish boshlandi...\n")
    asyncio.run(main())
