"""
Aggregate guruhni tekshirish va to'g'ri ID ni olish
"""

import asyncio
from dotenv import load_dotenv
import os
from telethon import TelegramClient

load_dotenv()

API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = os.getenv('TG_SESSION_NAME', 'sessions/userbot_session')
AGGREGATE_CHAT_ID = os.getenv('AGGREGATE_CHAT_IDS', '').split(',')[0].strip()


async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    try:
        await client.start()
        me = await client.get_me()
        print(f"✅ Ulandi: {me.first_name} (@{me.username})\n")

        print(f"🔍 Aggregate guruh ID: {AGGREGATE_CHAT_ID}")
        print(f"🔍 Int formatda: {int(AGGREGATE_CHAT_ID)}\n")

        # Barcha dialoglarni olish
        print("📂 Barcha guruhlarni qidiryapman...\n")
        dialogs = await client.get_dialogs()

        found = False
        for dialog in dialogs:
            entity = dialog.entity

            # ID lar
            entity_id = entity.id
            full_id = f"-100{entity_id}" if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast') else f"-{entity_id}"

            # Aggregate ID ga mos kelishini tekshirish
            if str(entity_id) in AGGREGATE_CHAT_ID or str(full_id) == AGGREGATE_CHAT_ID:
                found = True
                title = getattr(entity, 'title', 'Unknown')
                print(f"✅ TOPILDI!")
                print(f"   📛 Nom: {title}")
                print(f"   🆔 Raw ID: {entity_id}")
                print(f"   🆔 Full ID: {full_id}")
                print(f"   ℹ️  Type: {type(entity).__name__}")

                # Test: habar jo'natish
                print(f"\n🧪 Test habar jo'natish...")
                try:
                    await client.send_message(entity, "✅ Test: Monitoring bot ishlayapti!")
                    print(f"✅ Test habar yuborildi!")
                except Exception as e:
                    print(f"❌ Test habar yuborilmadi: {e}")

                break

        if not found:
            print(f"❌ Aggregate guruh topilmadi!")
            print(f"\n📋 Mavjud guruhlar:")
            for dialog in dialogs[:20]:
                entity = dialog.entity
                if hasattr(entity, 'title'):
                    entity_id = entity.id
                    full_id = f"-100{entity_id}" if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast') else f"-{entity_id}"
                    print(f"   • {entity.title[:40]:40} | ID: {full_id}")

    except Exception as e:
        print(f"❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
