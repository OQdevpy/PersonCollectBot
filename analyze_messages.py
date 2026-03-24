"""
Guruhlardan habarlarni olish va tahlil qilish
"""

import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from telethon import TelegramClient
from telethon.tl.types import (
    MessageEntityMention,
    MessageEntityTextUrl,
    MessageEntityUrl,
    MessageEntityBotCommand,
    PeerUser,
    PeerChat,
    PeerChannel,
)
from datetime import datetime

# .env faylni yuklash
load_dotenv()

# Konfiguratsiya
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = os.getenv('TG_SESSION_NAME', 'sessions/userbot_session')


def load_groups():
    """groups.json dan guruh ID larini yuklash"""
    groups_file = Path("src/config/groups.json")
    if groups_file.exists():
        with open(groups_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('groups', [])
    return []


def categorize_sender(message):
    """
    Habar yuboruvchini aniqlash:
    - user: oddiy foydalanuvchi
    - bot: bot
    - channel: kanal/guruh
    - forward: forward qilingan habar
    """
    sender_type = "unknown"
    sender_info = {}

    # Forward qilingan habarlarni tekshirish
    if message.forward:
        sender_type = "forward"
        fwd = message.forward
        if fwd.from_id:
            if isinstance(fwd.from_id, PeerUser):
                sender_info['forward_from'] = 'user'
                sender_info['forward_from_id'] = fwd.from_id.user_id
            elif isinstance(fwd.from_id, PeerChannel):
                sender_info['forward_from'] = 'channel'
                sender_info['forward_from_id'] = fwd.from_id.channel_id
        if fwd.from_name:
            sender_info['forward_from_name'] = fwd.from_name
        return sender_type, sender_info

    # Oddiy habarlar
    sender = message.sender
    if sender:
        sender_info['id'] = sender.id
        sender_info['name'] = getattr(sender, 'first_name', None) or getattr(sender, 'title', 'Unknown')

        # Bot tekshirish
        if hasattr(sender, 'bot') and sender.bot:
            sender_type = "bot"
            sender_info['username'] = getattr(sender, 'username', None)
        # Kanal/guruh tekshirish
        elif hasattr(sender, 'broadcast'):
            sender_type = "channel"
            sender_info['username'] = getattr(sender, 'username', None)
        # Oddiy foydalanuvchi
        else:
            sender_type = "user"
            sender_info['username'] = getattr(sender, 'username', None)

    return sender_type, sender_info


def analyze_message_content(message):
    """Habar mazmunini tahlil qilish"""
    content_info = {
        'has_text': bool(message.text),
        'text_length': len(message.text) if message.text else 0,
        'has_media': message.media is not None,
        'media_type': None,
        'has_links': False,
        'has_mentions': False,
        'has_hashtags': False,
    }

    # Media turi
    if message.media:
        media_type = type(message.media).__name__
        content_info['media_type'] = media_type

    # Entities (linklar, mention, hashtag)
    if message.entities:
        for entity in message.entities:
            if isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                content_info['has_links'] = True
            elif isinstance(entity, MessageEntityMention):
                content_info['has_mentions'] = True
            elif hasattr(entity, 'offset') and message.text:
                # Hashtag tekshirish
                entity_text = message.text[entity.offset:entity.offset + entity.length]
                if entity_text.startswith('#'):
                    content_info['has_hashtags'] = True

    return content_info


async def analyze_group_messages(client, chat_id, limit=15):
    """Guruhdan habarlarni olish va tahlil qilish"""
    messages_data = []

    try:
        # Guruh haqida ma'lumot olish
        entity = await client.get_entity(int(chat_id))
        group_title = getattr(entity, 'title', 'Unknown')

        print(f"\n{'='*80}")
        print(f"📊 Guruh: {group_title}")
        print(f"🆔 ID: {chat_id}")
        print(f"{'='*80}\n")

        # Habarlarni olish
        messages = await client.get_messages(entity, limit=limit)

        for i, msg in enumerate(messages, 1):
            if not msg:
                continue

            # Yuboruvchini aniqlash
            sender_type, sender_info = categorize_sender(msg)

            # Mazmunni tahlil qilish
            content_info = analyze_message_content(msg)

            # Ma'lumotlarni to'plash
            msg_data = {
                'message_id': msg.id,
                'date': msg.date.isoformat() if msg.date else None,
                'sender_type': sender_type,
                'sender_info': sender_info,
                'content': content_info,
                'text_preview': msg.text[:100] if msg.text else None,
            }

            messages_data.append(msg_data)

            # Chiroyli formatda ko'rsatish
            print(f"{i}. Habar ID: {msg.id}")
            print(f"   📅 Sana: {msg.date.strftime('%Y-%m-%d %H:%M:%S') if msg.date else 'N/A'}")
            print(f"   👤 Yuboruvchi: {sender_type.upper()}")

            if sender_type == "forward":
                print(f"      ↪️  Forward: {sender_info.get('forward_from', 'Unknown')}")
                if 'forward_from_name' in sender_info:
                    print(f"      ↪️  Ism: {sender_info['forward_from_name']}")
            else:
                print(f"      ℹ️  Ism: {sender_info.get('name', 'Unknown')}")
                if sender_info.get('username'):
                    print(f"      ℹ️  Username: @{sender_info['username']}")

            print(f"   📝 Mazmun:")
            print(f"      • Matn: {'Ha' if content_info['has_text'] else 'Yo\'q'} ({content_info['text_length']} ta belgi)")
            print(f"      • Media: {'Ha' if content_info['has_media'] else 'Yo\'q'}", end='')
            if content_info['media_type']:
                print(f" ({content_info['media_type']})")
            else:
                print()
            print(f"      • Linklar: {'Ha' if content_info['has_links'] else 'Yo\'q'}")
            print(f"      • Mention: {'Ha' if content_info['has_mentions'] else 'Yo\'q'}")

            if msg.text and len(msg.text) <= 200:
                print(f"   💬 Matn: {msg.text}")
            elif msg.text:
                print(f"   💬 Matn: {msg.text[:200]}...")

            print(f"   {'-'*75}")

    except Exception as e:
        print(f"❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()

    return {
        'chat_id': chat_id,
        'group_title': group_title,
        'total_messages': len(messages_data),
        'messages': messages_data
    }


async def main():
    """Asosiy funksiya"""
    # Guruhlarni yuklash
    groups = load_groups()

    if not groups:
        print("❌ Guruhlar topilmadi. groups.json faylini tekshiring.")
        return

    print(f"✅ {len(groups)} ta guruh topildi\n")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print("❌ Sessiya topilmadi yoki yaroqsiz.")
            return

        me = await client.get_me()
        print(f"✅ Telegram'ga ulandi: {me.first_name} (@{me.username})\n")

        all_data = []

        # Har bir guruhdan habarlarni olish
        for chat_id in groups:
            group_data = await analyze_group_messages(client, chat_id, limit=15)
            all_data.append(group_data)

        # Natijalarni saqlash
        output_file = Path("src/config/messages_analysis.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_date': datetime.now().isoformat(),
                'total_groups': len(all_data),
                'groups': all_data
            }, f, ensure_ascii=False, indent=2)

        print(f"\n\n{'='*80}")
        print(f"💾 Tahlil natijalari saqlandi: {output_file}")
        print(f"{'='*80}")

        # Umumiy statistika
        print(f"\n📈 UMUMIY STATISTIKA:")
        total_messages = sum(g['total_messages'] for g in all_data)
        print(f"   • Jami guruhlar: {len(all_data)}")
        print(f"   • Jami habarlar: {total_messages}")

        # Yuboruvchi turlari bo'yicha statistika
        sender_stats = {'user': 0, 'bot': 0, 'channel': 0, 'forward': 0, 'unknown': 0}
        for group in all_data:
            for msg in group['messages']:
                sender_type = msg.get('sender_type', 'unknown')
                sender_stats[sender_type] = sender_stats.get(sender_type, 0) + 1

        print(f"\n   📊 Yuboruvchi turlari:")
        print(f"      • Foydalanuvchi: {sender_stats['user']}")
        print(f"      • Bot: {sender_stats['bot']}")
        print(f"      • Kanal: {sender_stats['channel']}")
        print(f"      • Forward: {sender_stats['forward']}")
        print(f"      • Noma'lum: {sender_stats['unknown']}")

    except Exception as e:
        print(f"❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()
        print("\n👋 Telegram bilan aloqa uzildi")


if __name__ == "__main__":
    print("🚀 Habarlarni tahlil qilish boshlandi...\n")
    asyncio.run(main())
