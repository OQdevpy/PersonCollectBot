"""
Passengers papkasidagi barcha guruhlarning ID va linklarini olish
"""

import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, Dialog
from telethon.tl.functions.messages import GetDialogFiltersRequest

# .env faylni yuklash
load_dotenv()

# Konfiguratsiya
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = os.getenv('TG_SESSION_NAME', 'sessions/userbot_session')


async def get_passenger_groups():
    """
    Passengers papkasidagi barcha guruhlarni olish
    """
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    try:
        print(f"🔧 Sessiya fayli: {SESSION_NAME}")
        print(f"🔧 API ID: {API_ID}")

        await client.connect()
        print("🔗 Client ulandi")

        if not await client.is_user_authorized():
            print("❌ Sessiya topilmadi yoki yaroqsiz. Iltimos, create_session.py ni ishga tushiring.")
            print("\n💡 Yoki quyidagi buyruqni bajaring:")
            print(f"   python create_session.py")
            return

        me = await client.get_me()
        print(f"✅ Telegram'ga ulandi: {me.first_name} (@{me.username})\n")
        print("📂 Papkalarni tekshiryapman...\n")

        # Barcha papkalarni olish (Dialog Filters)
        filters_result = await client(GetDialogFiltersRequest())

        passenger_folder = None
        folder_name = None
        passenger_chat_ids = set()

        # "passengers" papkasini topish
        for folder in filters_result.filters:
            if hasattr(folder, 'title'):
                # TextWithEntities obyektidan text olish
                title_text = folder.title.text if hasattr(folder.title, 'text') else str(folder.title)
                print(f"📁 Topilgan papka: {title_text} (ID: {folder.id})")
                if 'passenger' in title_text.lower():
                    passenger_folder = folder
                    folder_name = title_text
                    print(f"✅ Maqsad papka topildi: {title_text}")

                    # Papkadagi chat ID larni olish
                    if hasattr(folder, 'include_peers'):
                        for peer in folder.include_peers:
                            # Peer obyektidan chat ID ni olish
                            if hasattr(peer, 'channel_id'):
                                passenger_chat_ids.add(peer.channel_id)
                            elif hasattr(peer, 'chat_id'):
                                passenger_chat_ids.add(peer.chat_id)
                            elif hasattr(peer, 'user_id'):
                                passenger_chat_ids.add(peer.user_id)

                        print(f"📊 Papkada {len(passenger_chat_ids)} ta chat ID topildi\n")
                    break

        if not passenger_folder:
            print("⚠️  'passengers' papkasi topilmadi. Barcha guruhlarni ko'rsataman:\n")

        # Barcha dialoglarni olish
        dialogs = await client.get_dialogs()

        groups_data = []

        print(f"🔍 Jami {len(dialogs)} ta dialog topildi. Guruhlarni filtrlayapman...\n")

        for dialog in dialogs:
            entity = dialog.entity

            # Faqat guruhlar va kanallarni olish
            if isinstance(entity, (Channel, Chat)):
                # Agar passengers papkasi topilmagan bo'lsa, barcha guruhlarni ko'rsatish
                # Yoki entity ID papka ID lari to'plamida bo'lsa
                if not passenger_folder or entity.id in passenger_chat_ids:

                    # Guruh ID
                    chat_id = entity.id
                    full_chat_id = f"-100{chat_id}" if isinstance(entity, Channel) else f"-{chat_id}"

                    # Guruh nomi
                    title = entity.title

                    # Username (public guruhlar uchun)
                    username = getattr(entity, 'username', None)

                    # Link yaratish
                    if username:
                        link = f"https://t.me/{username}"
                    else:
                        # Private guruh uchun internal link
                        link = f"https://t.me/c/{chat_id}/1"

                    # Guruh turi
                    group_type = "Kanal" if isinstance(entity, Channel) and entity.broadcast else "Guruh"

                    groups_data.append({
                        "title": title,
                        "id": full_chat_id,
                        "raw_id": chat_id,
                        "username": username,
                        "link": link,
                        "type": group_type,
                        "is_public": username is not None
                    })

        # Natijalarni chiroyli formatda ko'rsatish
        print("=" * 80)
        if passenger_folder:
            print(f"📦 '{folder_name}' PAPKASIDAGI GURUHLAR")
        else:
            print("📦 BARCHA GURUHLAR")
        print("=" * 80)
        print(f"\n✅ Jami topildi: {len(groups_data)} ta guruh/kanal\n")

        for i, group in enumerate(groups_data, 1):
            print(f"\n{i}. {group['title']}")
            print(f"   🆔 ID: {group['id']}")
            print(f"   🔢 Raw ID: {group['raw_id']}")
            print(f"   🔗 Link: {group['link']}")
            print(f"   📝 Turi: {group['type']}")
            print(f"   🌐 Username: @{group['username']}" if group['username'] else "   🔒 Private guruh")
            print(f"   {'─' * 70}")

        # JSON faylga saqlash
        output_file = Path("src/config/passenger_groups.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "folder_name": folder_name if passenger_folder else "All Groups",
                "total_groups": len(groups_data),
                "groups": groups_data
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Ma'lumotlar saqlandi: {output_file}")

        # groups.json uchun faqat ID larni tayyorlash
        group_ids = [group['id'] for group in groups_data]
        groups_json_file = Path("src/config/groups.json")

        print(f"\n📋 groups.json uchun ID lar ro'yxati:")
        print(json.dumps({"groups": group_ids}, ensure_ascii=False, indent=2))

        # Foydalanuvchidan so'rash
        print(f"\n❓ groups.json faylga avtomatik qo'shishni xohlaysizmi? (y/n): ", end='')

    except Exception as e:
        print(f"❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()
        print("\n👋 Telegram bilan aloqa uzildi")


if __name__ == "__main__":
    print("🚀 Passengers guruhlarini olish boshlandi...\n")
    asyncio.run(get_passenger_groups())