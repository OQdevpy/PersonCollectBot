# PersonCollectBot - Foydalanish Qo'llanmasi

## 📋 Loyiha Haqida

PersonCollectBot - bir nechta Telegram guruhlaridan kelgan habarlarni real-time monitoring qilib, markaziy aggregate guruhga jo'natuvchi bot.

## 🎯 Asosiy Xususiyatlar

- ✅ Bir nechta guruhni bir vaqtda monitoring qilish
- ✅ Habar yuboruvchini aniqlash (User, Bot, Forward)
- ✅ Habarlarni umumiy formatda aggregate guruhga jo'natish
- ✅ Media fayllarni ham jo'natish
- ✅ Real-time monitoring

## 📁 Skriptlar

### 1. `get_passenger_groups.py`
**Maqsad:** Telegram papkasidagi guruhlarni olish va ID larini saqlash

**Ishlatish:**
```bash
python get_passenger_groups.py
```

**Natija:**
- `src/config/passenger_groups.json` - barcha guruhlar haqida batafsil ma'lumot
- Guruh ID lari, nomlari, linklari

---

### 2. `analyze_messages.py`
**Maqsad:** Har bir guruhdan 15 ta habarni olish va tahlil qilish

**Ishlatish:**
```bash
python analyze_messages.py
```

**Natija:**
- `src/config/messages_analysis.json` - habarlar tahlili
- Yuboruvchi turlari statistikasi
- Media va matn ma'lumotlari

**Tahlil natijalari:**
- 📊 105 ta habar tahlil qilindi
- 👤 Foydalanuvchi: 41
- 🤖 Bot: 42
- 📤 Forward: 9
- ❓ Noma'lum: 13

---

### 3. `monitor_groups.py` ⭐ (Asosiy)
**Maqsad:** Guruhlarni real-time monitoring qilish va habarlarni aggregate guruhga jo'natish

**Ishlatish:**
```bash
python monitor_groups.py
```

**Imkoniyatlari:**
- Real-time habarlarni tinglash
- Barcha habarlarni bir xil formatda jo'natish
- Media fayllarni ham jo'natish
- Yuboruvchi ma'lumotlarini ko'rsatish

**Habar formati:**
```
📨 **Yangi habar: Guruh nomi**
────────────────────────────────────────
👤 **Yuboruvchi:** Ism Familiya (@username)
📋 **Turi:** User/Bot/Forward
🕐 **Vaqt:** 2026-03-24 18:10:01
📎 **Media:** 📷 Foto (agar bor bo'lsa)

💬 **Habar:**
Habar matni...
────────────────────────────────────────
```

**To'xtatish:**
- `Ctrl+C` tugmasini bosing

---

## ⚙️ Konfiguratsiya

### `.env` fayli
```env
# Telegram API
TG_API_ID=21505944
TG_API_HASH=2f76beb74cac9c97cfa18c9235bd485d
TG_SESSION_NAME=sessions/userbot_session

# Bot token
TG_BOT_TOKEN=8793821405:AAH...

# Aggregate guruh (habarlar jo'natiladigan guruh)
AGGREGATE_CHAT_IDS=-1003871578708

# Admin ID lar
ADMIN_IDS=1614151217,1478336262,7741398763,6501973746
```

### `src/config/groups.json`
Monitoring qilinadigan guruhlar ro'yxati:
```json
{
  "groups": [
    "-1002227900964",
    "-1002563400876",
    "-1002278599289",
    "-1002721584286",
    "-4949164962",
    "-1002016693433"
  ]
}
```

**Guruhlar:**
1. Қозон Группа
2. Safar taksi
3. ELTUVCHI TAXI
4. САФДОШЛАР ( ПРЕМИУМ )
5. QADIRDONLAR 7777
6. OLDI BORDI

---

## 🚀 Ishga Tushirish

### 1. Birinchi marta
```bash
# 1. Sessiya yaratish (agar yo'q bo'lsa)
python create_session.py

# 2. Guruhlarni olish
python get_passenger_groups.py

# 3. Habarlarni tahlil qilish (ixtiyoriy)
python analyze_messages.py

# 4. Monitoring boshlash
python monitor_groups.py
```

### 2. Kundalik ishlatish
```bash
# Faqat monitoring botni ishga tushiring
python monitor_groups.py
```

---

## 📊 Monitoring Jarayoni

1. **Bot ishga tushadi** → Telegram ga ulanadi
2. **Guruhlarni tinglaydi** → 6 ta guruhdan real-time habarlarni oladi
3. **Habarni tahlil qiladi** → Yuboruvchi, matn, media
4. **Formatlab jo'natadi** → Aggregate guruhga umumiy formatda
5. **Konsolga log** → Har bir habar haqida ma'lumot

---

## 🔍 Xatoliklarni Hal Qilish

### Xatolik: "Sessiya topilmadi"
```bash
python create_session.py
```

### Xatolik: "AGGREGATE_CHAT_IDS o'rnatilmagan"
`.env` faylida `AGGREGATE_CHAT_IDS` ni to'ldiring

### Xatolik: "Guruhlar topilmadi"
```bash
python get_passenger_groups.py
```
So'ng guruh ID larini `src/config/groups.json` ga qo'shing

---

## 📈 Statistika

Monitoring davomida quyidagi statistika yig'iladi:
- Har bir guruhdan kelgan habarlar soni
- Yuboruvchi turlari (User, Bot, Forward)
- Media turlari
- Kunlik statistika

---

## 🛠️ Texnologiyalar

- **Python 3.12**
- **Telethon** - Telegram userbot
- **python-telegram-bot** - Bot API
- **python-dotenv** - Konfiguratsiya

---

## 📝 Eslatmalar

1. **Sessiya xavfsizligi:** `sessions/` papkasini GitHub ga qo'shmang
2. **API ma'lumotlari:** `.env` faylni himoya qiling
3. **Aggregate guruh:** Bot shu guruhga habar jo'natish huquqiga ega bo'lishi kerak
4. **Monitoring:** Bot uzluksiz ishlashi uchun serverdа ishga tushiring

---

## 🤝 Yordam

Muammolar yuzaga kelsa:
1. `.env` faylni tekshiring
2. Sessiya yaratilganligini tasdiqlang
3. Guruh ID larini tekshiring
4. Bot huquqlarini tekshiring

---

## 📞 Kontakt

Muallif: OQdevpy
Repository: https://github.com/OQdevpy/PersonCollectBot

---

**Omad!** 🚀
