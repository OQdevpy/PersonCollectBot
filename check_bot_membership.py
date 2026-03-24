"""
Botning guruhga a'zoligini tekshirish va test habar yuborish
"""

import asyncio
from dotenv import load_dotenv
import os
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()

BOT_TOKEN = os.getenv('TG_BOT_TOKEN')

# Turli ID formatlarini sinab ko'rish
POSSIBLE_IDS = [
    '-1003871578708',
    '-3871578708',
    '3871578708',
    '1003871578708',
]


async def main():
    bot = Bot(token=BOT_TOKEN)

    print("🤖 Bot ma'lumotlari:")
    me = await bot.get_me()
    print(f"   📛 Ism: {me.first_name}")
    print(f"   🆔 Username: @{me.username}")
    print(f"   🔢 ID: {me.id}\n")

    print("🔍 Guruhga a'zolikni tekshiryapman...\n")

    for chat_id in POSSIBLE_IDS:
        print(f"{'='*60}")
        print(f"🧪 Test: {chat_id}")
        print(f"{'='*60}")

        try:
            # Guruh haqida ma'lumot olish
            chat = await bot.get_chat(chat_id)
            print(f"✅ Guruh topildi!")
            print(f"   📛 Nom: {chat.title}")
            print(f"   🆔 ID: {chat.id}")
            print(f"   📝 Turi: {chat.type}")

            # Bot a'zolarni tekshirish
            try:
                member = await bot.get_chat_member(chat_id, me.id)
                print(f"   👤 Bot holati: {member.status}")

                if member.status in ['administrator', 'member']:
                    print(f"   ✅ Bot guruhda a'zo!\n")

                    # Test habar yuborish
                    print(f"📤 Test habar yuborish...")
                    message = await bot.send_message(
                        chat_id=chat_id,
                        text="✅ Test: Monitoring bot ishlayapti!\n\n"
                             "Bu test xabari. Bot to'g'ri ishlayotganini tekshirish uchun.\n\n"
                             "🔄 Endi guruhlardan kelgan habarlar shu yerga avtomatik yuboriladi."
                    )
                    print(f"   ✅ Habar yuborildi! Message ID: {message.message_id}")
                    print(f"\n🎉 TO'G'RI ID TOPILDI: {chat_id}\n")

                    # .env faylga yozish uchun tavsiya
                    print(f"📋 .env faylga qo'shing:")
                    print(f"   AGGREGATE_CHAT_IDS={chat_id}\n")
                    return chat_id

                else:
                    print(f"   ⚠️  Bot holati: {member.status}\n")

            except TelegramError as e:
                print(f"   ❌ A'zolikni tekshirib bo'lmadi: {e}\n")

        except TelegramError as e:
            print(f"❌ Guruh topilmadi: {e}\n")

    print("\n" + "="*60)
    print("💡 Hech qanday to'g'ri ID topilmadi!")
    print("📋 Quyidagilarni tekshiring:")
    print("   1. Bot guruhga qo'shilganmi?")
    print("   2. Guruh ID to'g'rimi?")
    print("   3. Bot habar yuborish huquqiga egami?")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
