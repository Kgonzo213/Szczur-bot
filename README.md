
# 🐀 SzczurBot – Discord Szczur Attack & Audio Bot

SzczurBot to rozrywkowy bot na Discorda, który może:
- Spamować użytkowników wiadomościami typu „Szczurzeeeeeeee!” 🐀
- Dołączać do kanału głosowego i odtwarzać dźwięki 📢
- Obsługiwać kolejkę audio 🎶

---

## 📦 Wymagania

- Python 3.8+
- FFmpeg (binarka musi znajdować się w folderze projektu jako `ffmpeg.exe`)
- Zainstalowane biblioteki:

```bash
pip install -r requirements.txt
```

Plik `requirements.txt` może wyglądać tak:
```
discord.py
python-dotenv
```

---

## ⚙️ Konfiguracja

1. Stwórz bota na [Discord Developer Portal](https://discord.com/developers/applications) i wygeneruj token.
2. W folderze projektu utwórz plik `.env`:

```
DISCORD_TOKEN=twój_token_tutaj
```

3. Upewnij się, że w folderze projektu znajduje się plik audio `szczur.mp3` oraz `ffmpeg.exe`.

---

## ▶️ Uruchomienie

```bash
python bot.py
```

---

## 💬 Komendy

Bot reaguje na wiadomości zaczynające się od `?`.

| Komenda                     | Opis |
|----------------------------|------|
| `?help`                    | Wyświetla listę dostępnych komend. |
| `?szczur @user N T`        | Wysyła N szczurów co T sekund do wskazanego użytkownika. |
| `?chodz`                   | Bot dołącza do twojego kanału głosowego i odtwarza szczura. |
| `?graj <link lub ścieżka>` | Dodaje podany plik audio do kolejki i odtwarza. |
| `?stop`                    | Zatrzymuje aktualnie odtwarzany dźwięk. |
| `?idz`                     | Rozłącza bota z kanału głosowego. |

---

## 📂 Struktura folderu

```
📁 projekt/
│
├── .env
├── bot.py
├── ffmpeg.exe
├── szczur.mp3
├── responses.py
└── requirements.txt
```

## 📜 Licencja

Projekt do celów edukacyjnych i humorystycznych. Używaj odpowiedzialnie! 😉

---
