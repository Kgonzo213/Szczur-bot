from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, User, FFmpegPCMAudio, PCMVolumeTransformer, AudioSource
from responses import get_response
import asyncio
import yt_dlp  
import re  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ścieżka do folderu projektu

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    raise ValueError("Brak tokena Discorda. Upewnij się, że plik .env zawiera DISCORD_TOKEN.")

# Ustawienie bota
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

# Globalna kolejka dla dźwięków
audio_queue = []


async def play_audio_queue(voice_client):
    while audio_queue:
        next_audio = audio_queue.pop(0)
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': False,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(next_audio['url'], download=False)
                audio_url = info.get('url')
                if not audio_url:
                    raise Exception("Nie udało się uzyskać URL strumienia audio.")

            audio_source = PCMVolumeTransformer(FFmpegPCMAudio(audio_url))
            voice_client.play(audio_source)

            while voice_client.is_playing():
                await asyncio.sleep(1)

        except Exception as e:
            print(f'Błąd podczas odtwarzania: {e}')
            await voice_client.disconnect()
            return

    await voice_client.disconnect()

# Obsługa wiadomości i komend
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Wyszczurzyło mnie na chwilę)')
        return
    else:
        if user_message.startswith('?'):
            # Wyszukiwanie linku w wiadomości
            link_match = re.search(r'http[s]?://\S+', user_message)
            link = link_match.group(0) if link_match else ''  # Pobierz link, jeśli istnieje

            # Usunięcie linku z wiadomości i konwersja komendy na małe litery
            command_part = user_message[1:].replace(link, '').strip().lower()

            # Połącz komendę i link (jeśli istnieje)
            command = f"{command_part} {link}".strip()

            if command == 'help':
                response: str = (
                    "**Lista dostępnych komend Szczur-bota:**\n\n"
                    "**?szczur @użytkownik <ilość> <interwał>**\n"
                    "   - Wysyła określoną liczbę szczurów do oznaczonego użytkownika w podanym interwale czasowym (w sekundach).\n"
                    "   - Przykład: `?szczur @username 5 10` (wysyła 5 szczurów co 10 sekund).\n\n"
                    "**?chodz**\n"
                    "   - Bot dołącza do Twojego kanału głosowego i odtwarza dźwięk szczura.\n\n"
                    "**?idz**\n"
                    "   - Bot opuszcza kanał głosowy, na którym aktualnie się znajduje.\n\n"
                    "**?graj <link lub fraza>**\n"
                    "   - Odtwarza dźwięk z podanego linku YouTube lub wyszukuje i odtwarza pierwszy wynik dla podanej frazy.\n"
                    "   - Przykład: `?graj https://www.youtube.com/watch?v=dQw4w9WgXcQ` lub `?graj Rick Astley Never Gonna Give You Up`.\n\n"
                    "**?skip**\n"
                    "   - Pomija aktualnie odtwarzany utwór i przechodzi do następnego w kolejce.\n"
                    "   - Jeśli kolejka jest pusta, zatrzymuje odtwarzanie.\n\n"
                    "**?list**\n"
                    "   - Wyświetla aktualną kolejkę utworów do odtworzenia.\n\n"
                    "**?help**\n"
                    "   - Wyświetla tę wiadomość pomocy z opisem wszystkich dostępnych komend.\n\n"
                    "Jeśli masz pytania lub potrzebujesz pomocy, skontaktuj się z administratorem bota!"
                )
                await message.channel.send(response)
                return
            elif command[0:6] == 'szczur':
                try:
                    _, mention, count, interval = command.split()
                    
                    count: int = int(count)
                    interval: int = int(interval)
                    if count <= 0 or interval < 0:
                        await message.channel.send('Liczba szczurów i interwał muszą być większe od zera!')
                        return

                    # Pobieranie użytkownika z oznaczenia
                    if len(message.mentions) == 0:
                        await message.channel.send('Musisz oznaczyć użytkownika, np. @username!')
                        return

                    target_user = message.mentions[0]  # Pierwszy oznaczony użytkownik
                    # Zabezpieczenie przed spamowaniem
                    if target_user.id == 000000000000:  # ID użytkownika, którego nie można spamować
                        await message.channel.send('Nie możesz spamować tej osoby!')
                        return
                    response: str = f'Wysyłam {count} szczurów co {interval} sekund do {target_user.name}!'
                    await message.channel.send(response)

                    # Wysyłanie wiadomości prywatnych
                    for _ in range(count):
                        try:
                            await target_user.send('Szczurzeeeeeeeeeeeeeeeeeeeeeeee!')
                        except Exception as e:
                            print(f'Nie udało się wysłać wiadomości do {target_user}: {e}')
                            await message.channel.send(f'Nie udało się wysłać wiadomości do {target_user.name}.')
                            return
                        await asyncio.sleep(interval)

                except ValueError:
                    response: str = 'Niepoprawne argumenty! Użyj: ?szczur @użytkownik <ilość> <interwał>'
                    await message.channel.send(response)
                except Exception as e:
                    await message.channel.send(f'Wystąpił błąd: {e}')
                return
            elif command == 'chodz':
                try:
                    if not message.author.voice:
                        await message.channel.send('Musisz być na kanale głosowym, aby użyć tej komendy!')
                        return

                    # Pobieranie kanału głosowego użytkownika
                    voice_channel = message.author.voice.channel

                    # Sprawdzenie, czy bot jest już połączony z kanałem głosowym
                    voice_client = None
                    if message.guild.voice_client:
                        voice_client = message.guild.voice_client

                    # Jeśli bot nie jest połączony, dołącz do kanału użytkownika
                    if not voice_client:
                        voice_client = await voice_channel.connect()
                    elif voice_client.channel != voice_channel:
                        await message.channel.send('Jestem już połączony z innym kanałem głosowym!')
                        return

                    # Ścieżki do FFmpeg i pliku audio
                    ffmpeg_path = os.path.join(BASE_DIR, 'ffmpeg.exe')
                    audio_path = os.path.join(BASE_DIR, 'szczur.mp3')

                    # Odtwarzanie pliku audio
                    if not voice_client.is_playing():
                        audio_source = PCMVolumeTransformer(FFmpegPCMAudio(audio_path, executable=ffmpeg_path))
                        voice_client.play(audio_source)

                    # Oczekiwanie na zakończenie odtwarzania
                    while voice_client.is_playing():
                        await asyncio.sleep(1)

                    # Rozłączanie bota po zakończeniu odtwarzania
                    await voice_client.disconnect()

                except Exception as e:
                    await message.channel.send(f'Wystąpił błąd: {e}')
                    return
            elif command[0:4] == 'graj':
                try:
                    # Sprawdzenie, czy użytkownik jest na kanale głosowym
                    if not message.author.voice:
                        await message.channel.send('Musisz być na kanale głosowym, aby użyć tej komendy!')
                        return

                    # Pobieranie kanału głosowego użytkownika
                    voice_channel = message.author.voice.channel

                    # Sprawdzenie, czy bot jest już połączony z kanałem głosowym
                    voice_client = None
                    if message.guild.voice_client:
                        voice_client = message.guild.voice_client

                    # Jeśli bot nie jest połączony, dołącz do kanału użytkownika
                    if not voice_client:
                        voice_client = await voice_channel.connect()
                    elif voice_client.channel != voice_channel:
                        await message.channel.send('Jestem już połączony z innym kanałem głosowym!')
                        return

                    # Pobierz link lub frazę do wyszukiwania z komendy
                    query = command[5:]
                    if not query:
                        await message.channel.send('Musisz podać link do filmu na YouTube lub frazę do wyszukania!')
                        return

                    # Sprawdzenie, czy podano bezpośredni link do YouTube
                    if "youtube.com" in query or "youtu.be" in query:
                        youtube_url = query
                    else:
                        # Wyszukiwanie na YouTube za pomocą yt-dlp
                        ydl_opts = {
                            'format': 'bestaudio/best',
                            'quiet': True,
                            'noplaylist': True,
                            'extract_flat': True,
                        }
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            search_results = ydl.extract_info(f"ytsearch:{query}", download=False)
                            if 'entries' in search_results and len(search_results['entries']) > 0:
                                youtube_url = search_results['entries'][0]['url']
                                await message.channel.send(f'Znaleziono: {search_results["entries"][0]["title"]}')
                            else:
                                await message.channel.send('Nie znaleziono wyników dla podanej frazy.')
                                return

                    # Dodanie linku do kolejki
                    audio_queue.append({'url': youtube_url})
                    await message.channel.send(f'Dodano do kolejki: {youtube_url}')

                    # Jeśli nic nie jest odtwarzane, rozpocznij odtwarzanie
                    if not voice_client.is_playing():
                        await play_audio_queue(voice_client)

                except Exception as e:
                    await message.channel.send(f'Wystąpił błąd: {e}')
                return
            elif command == 'idz':
                # Sprawdzenie, czy bot jest połączony z kanałem głosowym
                if message.guild.voice_client:
                    voice_client = message.guild.voice_client
                    await voice_client.disconnect()
                    await message.channel.send('Rozłączono z kanałem głosowym.')
                else:
                    await message.channel.send('Nie jestem połączony z żadnym kanałem głosowym.')
                return
            elif command == 'skip':
                if message.guild.voice_client:
                    voice_client = message.guild.voice_client
                    if voice_client.is_playing():
                        voice_client.stop()  # Zatrzymanie aktualnego utworu
                        if audio_queue:
                            await message.channel.send('Pominięto utwór. Odtwarzam następny.')
                            await play_audio_queue(voice_client)  # Odtwarzanie następnego utworu
                        else:
                            await message.channel.send('Pominięto utwór. Kolejka jest pusta.')
                    else:
                        await message.channel.send('Nie odtwarzam żadnego dźwięku.')
                else:
                    await message.channel.send('Nie jestem połączony z żadnym kanałem głosowym.')
                return
            elif command == 'list':
                if audio_queue:
                    queue_list = '\n'.join([f"{idx + 1}. {audio['url']}" for idx, audio in enumerate(audio_queue)])
                    await message.channel.send(f'Aktualna kolejka:\n{queue_list}')
                else:
                    await message.channel.send('Kolejka jest pusta.')
                return
            else:
                response: str = 'Nie znam takiej komendy!'
                await message.channel.send(response)

        else:
            response: str = get_response(user_message)
            if response == '':
                return
            await message.channel.send(response)
            return


# Logowania bota
@client.event
async def on_ready() -> None:
    print(f'{client.user} Szczurzy w sieci!')


# Obługa wiadomości 
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)



def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()