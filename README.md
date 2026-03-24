# Cargo Collector Bot

Telegram guruhlaridan kelgan xabarlarga inline tugmalar qo'shib, foydalanuvchilarni kategoriyalash uchun bot.

## Xususiyatlar

- ✅ **Inline tugmalar**: Har bir xabarga 4 ta amal tugmasi

  - ✅ Qabul - Foydalanuvchini qabul qilish
  - 🚚 Dispatch - Dispatcher bo'lib belgilash
  - ⛔ Block - Bloklash
  - ❌ Rad - Rad etish

- 🚀 **Tezkor filtrlash**: SET ma'lumot strukturasi yordamida O(1) tezlikda tekshirish
- 💾 **Ma'lumot saqlash**: JSON fayllar orqali ma'lumotlarni xavfsiz saqlash
- 🔒 **Atomik yozuv**: Temp file + rename orqali xavfsiz yozish
- 🔐 **File locking**: Bir vaqtning o'zida yozishdan himoya

## Arxitektura

```
src/
├── config/                  # Konfiguratsiya fayllari
│   ├── accepted.json       # Qabul qilinganlar
│   ├── dispatcher.json     # Dispatcherlar
│   ├── blocked.json        # Bloklangan foydalanuvchilar
│   ├── rejected.json       # Rad etilganlar
│   ├── blacklist.json      # So'zlar blacklist'i
│   └── groups.json         # Monitor qilinadigan guruhlar
│
├── utils/                   # Yordamchi modullar
│   ├── json_manager.py     # JSON o'qish/yozish (atomik + lock)
│   ├── sets_loader.py      # SET'larni yuklash va boshqarish
│   ├── button_handler.py   # Inline tugmalar va callback'lar
│   ├── separate.py         # Xabarlarni filtrlash
│   └── seperate_message.py # Dispatcher filtrlash logikasi
│
└── bot/                     # Bot modullari
    ├── admin_bot.py        # Admin panel
    ├── listen.py           # Userbot (Telethon)
    └── ...
```

## O'rnatish

1. **Repository'ni clone qiling:**

```bash
git clone https://github.com/OQdevpy/CargoCollectBot.git
cd CargoCollectBot
```

2. **Virtual environment yarating:**

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# yoki
venv\Scripts\activate  # Windows
```

3. **Kutubxonalarni o'rnating:**

```bash
pip install -r requirements.txt
```

4. **Environment faylini sozlang:**

```bash
cp .env.example .env
```

`.env` faylini tahrirlang:

```env
TG_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
AGGREGATE_CHAT_ID=-1001234567890
```

## Ishlatish

### Botni ishga tushirish:

```bash
python main.py
```

### Xususiyatlar:

#### 1. Avtomatik filtrlash

Bot guruhdan kelgan har bir xabarni ikki bosqichda filtrlayd:

- **User ID tekshiruvi**: Blocked/Rejected ro'yxatda bormi?
- **Matn tahlili**: Dispatcher xabariga o'xshaydi mi?

#### 2. Inline tugmalar

Filtrlashdan o'tgan har bir xabar aggregate guruhga inline tugmalar bilan yuboriladi.

#### 3. Callback ishlov berish

Tugma bosilganda:

1. User ID mos SET'ga qo'shiladi
2. JSON fayl yangilanadi (atomik yozuv)
3. Xabar edit qilinib, tugmalar o'chiriladi
4. Status matni qo'shiladi

## JSON Format

Barcha JSON fayllar oddiy user ID ro'yxati:

```json
[123456789, 987654321, 555666777]
```

## Texnik Tafsilotlar

### SET vs JSON

- **SET**: Xotira ichida tezkor tekshirish uchun (O(1) complexity)
- **JSON**: Disk'da doimiy saqlash uchun

### Atomik yozuv

```python
# 1. Temp faylga yozish
# 2. File lock bilan himoyalash
# 3. Rename (atomik operatsiya)
os.replace(temp_file, real_file)
```

### Callback data formati

```
action:user_id
```

Misollar:

- `accept:123456`
- `dispatch:998877`
- `block:555999`
- `reject:444333`

## Xatoliklarni bartaraf qilish

### Bot xabarlarni qabul qilmayapti

- Botni guruhga admin qilib qo'shganingizni tekshiring
- `AGGREGATE_CHAT_ID` to'g'ri ekanligini tekshiring

### JSON yozishda xatolik

- `src/config/` direktoriyasi mavjudligini tekshiring
- Fayl ruxsatlarini tekshiring

### SET'lar yuklanmayapti

- JSON fayllar to'g'ri formatda ekanligini tekshiring
- Console log'larni tekshiring

## Litsenziya

MIT License

## Muallif

OQdevpy - [@OQdevpy](https://github.com/OQdevpy)
