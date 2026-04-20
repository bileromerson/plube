import csv
import yt_dlp

CSV_INPUT = 'Alone.csv'

with open(CSV_INPUT, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        url = row[-1].strip()
        if not url or not url.startswith('http'):
            continue

        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            artist = info.get('artist', info.get('uploader', 'Artista Desconhecido'))

        # Correção: múltiplos post-processadores em uma lista
        ydl_opts = {
            'format': 'bestaudio/best',
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {'key': 'FFmpegMetadata'},  # Adiciona metadados
                {'key': 'EmbedThumbnail'},  # Incorpora a miniatura
            ],
            'quiet': True,
            'no_warnings': True,
            # Correção: caminho com nome do artista e título do vídeo
            'outtmpl': f'songs/{artist}/%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])   