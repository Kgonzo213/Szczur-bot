from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, User, FFmpegPCMAudio, PCMVolumeTransformer, AudioSource
from responses import get_response
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ścieżka do folderu projektu

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Ustawienie bota
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

# Globalna kolejka dla dźwięków
audio_queue = []

async def play_audio_queue(voice_client):
    """Odtwarza dźwięki z kolejki w pętli."""
    while audio_queue:
        next_audio = audio_queue.pop(0)  # Pobierz pierwszy element z kolejki
        audio_source = PCMVolumeTransformer(FFmpegPCMAudio(next_audio['path'], executable=next_audio['ffmpeg_path']))
        
        # Odtwarzanie dźwięku
        voice_client.play(audio_source)
        
        # Czekaj, aż dźwięk się skończy
        while voice_client.is_playing():
            await asyncio.sleep(1)

    # Jeśli kolejka jest pusta, rozłącz bota
    await voice_client.disconnect()

# Obsługa wiadomości i komend
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Wyszczurzyło mnie na chwilę)')
        return
    else:
        if user_message.startswith('?'):
            command: str = user_message[1:].lower()
            if command == 'help':
                response: str = '?Szczur <nazwauzytkownika> <iloscszcuzrow> <co_ile_szczurzy> \n?chodz \n?graj <link>' 
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

                    # Ścieżki do FFmpeg i pliku audio
                    ffmpeg_path = os.path.join(BASE_DIR, 'ffmpeg.exe')
                    audio_path = command[5:]  # Link do pliku audio
                    if not audio_path:
                        await message.channel.send('Musisz podać link do pliku audio!')
                        return

                    # Dodanie pliku audio do kolejki
                    audio_queue.append({'path': audio_path, 'ffmpeg_path': ffmpeg_path})
                    await message.channel.send(f'Dodano do kolejki: {audio_path}')

                    # Jeśli nic nie jest odtwarzane, rozpocznij odtwarzanie
                    if not voice_client.is_playing():
                        await play_audio_queue(voice_client)

                except Exception as e:
                    await message.channel.send(f'Wystąpił błąd: {e}')
                return
            elif command == 'stop':
                # Sprawdzenie, czy bot jest połączony z kanałem głosowym
                if message.guild.voice_client:
                    voice_client = message.guild.voice_client
                    if voice_client.is_playing():
                        voice_client.stop()
                        await message.channel.send('Odtwarzanie zostało zatrzymane.')
                    else:
                        await message.channel.send('Nie odtwarzam żadnego dźwięku.')
                else:
                    await message.channel.send('Nie jestem połączony z żadnym kanałem głosowym.')
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
                # Sprawdzenie, czy bot jest połączony z kanałem głosowym
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
                    queue_list = '\n'.join([f"{idx + 1}. {audio['path']}" for idx, audio in enumerate(audio_queue)])
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