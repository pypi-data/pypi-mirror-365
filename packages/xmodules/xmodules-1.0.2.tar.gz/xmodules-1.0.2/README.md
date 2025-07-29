# XModules haqida

Bu modul yordamida Telegram’dagi *view‑once* (bir marta ko‘rinadigan) media fayllarini osongina saqlab qolish mumkin. Biz XModules kutubxonasini kengaytirishda davom etamiz. 

**Foydalanish tartibi:**

1. Avval *view‑once* media yuborilgan xabarga **reply** qilasiz.  
2. So‘ng `.ok` komandasini yuborasiz. ( buyruqni o'zgartirish mumkin. )

Shundan so‘ng userbot:

✅ Ushbu media‑ni ochib yubormasdan yuklab oladi.  
✅ Uni sizning **Saved Messages** (Saqlangan xabarlar) bo‘limingizga jo‘natadi.

Shu tarzda bir marta ko‘rinadigan media‑larni yo‘qolmasdan saqlab qo‘yishingiz mumkin.

## O‘rnatish
```bash
pip install xmodules
```

## Foydalanish misoli

`main.py` faylida quyidagicha yozing:

```python
from xmodules import run

API_ID = 123456 # my.telegram.org'dan olingan API_ID
API_HASH = "your_api_hash" # my.telegram.org'dan olingan API_HASH
ADMIN_ID = 987654321 # Telegram ID raqamingiz

run(API_ID, API_HASH, ADMIN_ID)
