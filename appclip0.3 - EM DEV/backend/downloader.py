import yt_dlp
import os
from pathlib import Path
import time
import subprocess
import re
import uuid

class VideoDownloader:
    def __init__(self, socketio=None):
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        self.socketio = socketio
        self.total_size = 0  # Tamanho total do vídeo e áudio
        self.downloaded_bytes = 0  # Bytes baixados até o momento
        self.is_first_progress = True  # Para inicializar o total_size apenas uma vez por formato

    def progress_hook(self, d, sid):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and 'downloaded_bytes' in d:
                if self.is_first_progress and 'total_bytes' in d:
                    self.total_size += d['total_bytes']
                    self.is_first_progress = False
                self.downloaded_bytes = d['downloaded_bytes']
                download_progress = (self.downloaded_bytes / self.total_size) * 70 if self.total_size > 0 else 0
                if self.socketio and sid:
                    self.socketio.emit('progress', {
                        'progress': download_progress
                    }, room=sid)
        elif d['status'] == 'finished':
            self.is_first_progress = True
            if self.socketio and sid:
                self.socketio.emit('progress', {
                    'progress': 70
                }, room=sid)

    def download_video(self, url, sid=None):
        try:
            self.total_size = 0
            self.downloaded_bytes = 0
            self.is_first_progress = True
            unique_id = str(uuid.uuid4())
            output_template = str(self.download_dir / f'%(title)s_{unique_id}.%(ext)s')

            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'outtmpl': output_template,
                'quiet': False,
                'verbose': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'cookiefile': 'cookies.txt',
                'retries': 10,
                'fragment_retries': 10,
                'ffmpeg_location': 'C:\\app\\python-lib\\ffmpeg\\bin\\ffmpeg.exe',
                'postprocessors': [{
                    'key': 'FFmpegVideoRemuxer',
                    'preferedformat': 'mp4',
                }],
                'postprocessor_args': {
                    'ffmpeg': ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-map', '0:v:0', '-map', '1:a:0', '-movflags', '+faststart']
                },
                'keepvideo': True,
                'progress_hooks': [lambda d: self.progress_hook(d, sid)],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obter informações do vídeo antes de iniciar o download
                info = ydl.extract_info(url, download=False)
                total_size = 0
                for format in info['formats']:
                    if format['format_id'] in ['399', '251']:  # Formatos selecionados
                        total_size += format.get('filesize', 0) or format.get('filesize_approx', 0)
                self.total_size = total_size

                if self.socketio and sid:
                    self.socketio.emit('progress', {
                        'progress': 0
                    }, room=sid)

                # Iniciar o download
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                if not filename.endswith('.mp4'):
                    filename = filename.rsplit('.', 1)[0] + '.mp4'

                if not os.path.exists(filename):
                    raise Exception(f"Arquivo final {filename} não foi gerado.")

                # Estimar o progresso da mesclagem (70% a 90%)
                if self.socketio and sid:
                    steps = 10
                    for i in range(steps):
                        progress = 70 + (i + 1) * (20 / steps)
                        self.socketio.emit('progress', {
                            'progress': progress
                        }, room=sid)
                        time.sleep(0.1)  # Pequeno delay para simular a mesclagem

                # Verificar se o arquivo tem áudio usando ffprobe
                ffprobe_cmd = [
                    'C:\\app\\python-lib\\ffmpeg\\bin\\ffprobe.exe',
                    '-i', filename,
                    '-show_streams',
                    '-select_streams', 'a',
                    '-loglevel', 'error'
                ]
                result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Falha ao verificar áudio com ffprobe: {result.stderr}")
                if not result.stdout:
                    raise Exception(f"O arquivo {filename} foi gerado sem áudio. ffprobe stderr: {result.stderr}")

                return filename
        except Exception as e:
            self.cleanup()
            raise Exception(f"Erro ao baixar ou mesclar vídeo: {str(e)}")

    def cleanup(self):
        max_attempts = 5
        delay = 1
        for file in self.download_dir.glob("*"):
            for attempt in range(max_attempts):
                try:
                    file.unlink()
                    print(f"Arquivo {file} excluído com sucesso.")
                    break
                except PermissionError:
                    print(f"Tentativa {attempt + 1}/{max_attempts}: Não foi possível excluir {file}. O arquivo está em uso.")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                except Exception as e:
                    print(f"Erro ao excluir {file}: {str(e)}")
                    break
            else:
                print(f"Falha ao excluir {file} após {max_attempts} tentativas. Deixando o arquivo no disco.")