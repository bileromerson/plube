import csv
import yt_dlp
import os
# Nome do arquivo CSV de entrada (deve ter uma coluna com URLs)
CSV_INPUT = 'Alone.csv'
# Nome do arquivo M3U de saída
M3U_OUTPUT = 'playlist/playlist.m3u'

# Lista para armazenar as entradas da playlist
playlist_entries = []

# Configurações para extrair informações sem baixar
ydl_opts = {
    'quiet': True,  # Reduz mensagens no console
    'no_warnings': True,
    'extract_flat': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
}

print("Extraindo metadados dos vídeos do YouTube...")

with open(CSV_INPUT, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        url = row[-1].strip()
        if not url or not url.startswith('http'):
            continue

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Título Desconhecido')
                artist = info.get('artist', info.get('uploader', 'Artista Desconhecido')) # Usa 'uploader' como fallback
                duration_seconds = info.get('duration', 0)

                # Define o caminho local: ./songs/artista/titulo.mp3
                filename = f"{title}.mp3"
                filepath = os.path.join('songs', artist, filename)

                playlist_entries.append((title, artist, duration_seconds, filepath))
                print(f"Adicionado: {artist} - {title}")

        except Exception as e:
            print(f"Erro ao processar {url}: {e}")

# Cria os diretórios e escreve o M3U
with open(M3U_OUTPUT, 'w', encoding='utf-8') as f:
    f.write("#EXTM3U\n")
    for title, artist, duration, filepath in playlist_entries:
        # Cria o diretório do artista, se não existir
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        f.write(f"#EXTINF:{duration},{artist} - {title}\n")
        f.write(f"../{filepath}\n")

print(f"Playlist M3U gerada: {M3U_OUTPUT}")