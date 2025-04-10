import yt_dlp
import os
from pathlib import Path
import time
import subprocess
import re
import uuid

class VideoDownloader:
    def __init__(self):
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)

    def download_video(self, url):
        try:
            # Gerar um identificador único para evitar conflitos
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
                # Usar o FFmpeg para mesclar e converter o áudio
                'postprocessors': [{
                    'key': 'FFmpegVideoRemuxer',  # Substituir FFmpegMerger por FFmpegVideoRemuxer
                    'preferedformat': 'mp4',
                }],
                'postprocessor_args': {
                    'ffmpeg': ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-map', '0:v:0', '-map', '1:a:0', '-movflags', '+faststart']
                },
                'keepvideo': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # Ajustar a extensão do filename para .mp4
                if not filename.endswith('.mp4'):
                    filename = filename.rsplit('.', 1)[0] + '.mp4'

                # Verificar se o arquivo final existe
                if not os.path.exists(filename):
                    raise Exception(f"Arquivo final {filename} não foi gerado.")

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
            self.cleanup()  # Limpar arquivos temporários em caso de erro
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