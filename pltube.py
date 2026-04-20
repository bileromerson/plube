# Version 2.1.0(BETA)

import os
import csv
import yt_dlp

# --- CONFIGURAÇÃO DE DIRETÓRIOS ---
BASE_DIR = os.getcwd()
SONGS_DIR = os.path.join(BASE_DIR, 'songs')
PLAYLISTS_DIR = os.path.join(BASE_DIR, 'playlists')
LOG_FILE = os.path.join(BASE_DIR, 'links_falhos.txt')

def registrar_erro(url, motivo, playlist):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"Link: {url} | Motivo: {motivo}, playlist: {playlist}\n")

class MeuLogger:
    def __init__(self, url, csv_file):
        self.url = url
        self.playlist = csv_file

    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg):
        print(f"Erro capturado: {msg}")
        registrar_erro(self.url, msg, self.playlist)

def criar_diretorios():
    # Cria as pastas no seu diretório atual
    os.makedirs(SONGS_DIR, exist_ok=True)
    os.makedirs(PLAYLISTS_DIR, exist_ok=True)

def obter_csvs():
    # Procura os arquivos .csv
    return [f for f in os.listdir(BASE_DIR) if f.endswith('.csv')]

def extrair_metadados(url):
    ydl_opts = {
        # 'cookiefile':'./cookie',
        'quiet': True,
        'logger': MeuLogger(url, csv_file),
        'ignore_errors': True,
        'noplaylist': True, # Garante apenas o vídeo individual
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None: return None
            return {
                'title': info.get('title'),
                'artist': info.get('artist', info.get('uploader')),
                'duration': info.get('duration', 0)
            }
    except Exception:
        return None

def baixar_musica(url, artist, title):
    safe_title = ''.join(c for c in title if c.isalnum() or c in ' -_').rstrip()
    folder_path = os.path.join(SONGS_DIR, artist)
    filepath_mp3 = os.path.join(folder_path, f"{safe_title}.mp3")
    
    # --- VERIFICAÇÃO DE DUPLICADOS ---
    if os.path.exists(filepath_mp3):
        print(f"Pular: {safe_title} já existe em {artist}")
        return filepath_mp3

    os.makedirs(folder_path, exist_ok=True)
    filepath_base = os.path.join(folder_path, safe_title)

    ydl_opts = {
        # 'cookiefile':'./cookie',
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'addmetadata': True,
        'outtmpl': filepath_base,
        'download_archive': 'Histrico.txt',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}],
        'quiet': False,
        'logger': MeuLogger(url, csv_file),
        'ignore_errors': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return filepath_mp3
    except Exception:
        return None

def processar_csv(csv_file):
    playlist_entries = []
    # Lê o CSV da pasta atual
    csv_path = os.path.join(BASE_DIR, csv_file)
    playlist_name = os.path.splitext(csv_file)[0]

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader) # Pula o cabeçalho do Furry.csv
        except StopIteration:
            return

        for row in reader:
            if len(row) < 3: continue
            url = row[2].strip() # Coluna dos csvs para a url <---
            
            if url.startswith('http'):
                print(f"Verificando: {url}")
                meta = extrair_metadados(url)

                if meta is None or meta['artist'] is None: continue
                
                music_path = baixar_musica(url, meta['artist'], meta['title'])
                print(music_path)
                if music_path is None: continue
                
                # Gera caminho relativo para a playlist funcionar na pasta atual
                rel_path = os.path.relpath(music_path, start=PLAYLISTS_DIR)
                playlist_entries.append((meta['title'], meta['artist'], meta['duration'], rel_path))

    m3u_path = os.path.join(PLAYLISTS_DIR, f'{playlist_name}.m3u')
    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for title, artist, duration, path in playlist_entries:
            f.write(f"#EXTINF:{duration},{artist} - {title}\n")
            f.write(f"{path}\n")

if __name__ == "__main__":
    criar_diretorios()
    csvs = obter_csvs()
    if not csvs:
        print(f"Nenhum arquivo .csv encontrado em: {BASE_DIR}")
    for csv_file in csvs:
        print(f"Processando arquivo: {csv_file}")
        processar_csv(csv_file)
        