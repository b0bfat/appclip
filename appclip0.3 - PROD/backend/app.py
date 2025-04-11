from flask import Flask, render_template, request, send_file, jsonify, Response
from flask_socketio import SocketIO, emit
from downloader import VideoDownloader
import os
import re
import traceback
import time
import logging

app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['TIMEOUT'] = 14400  # 4 horas
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurar logging
logging.basicConfig(
    filename='appclip.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

downloader = VideoDownloader(socketio=socketio)

# Limpar arquivos temporários ao iniciar o servidor
downloader.cleanup()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    if not data or 'url' not in data:
        app.logger.error("URL não fornecida na requisição.")
        return jsonify({'error': 'URL não fornecida'}), 400

    url = data['url']
    sid = data.get('sid')
    if not sid:
        app.logger.warning("Nenhum SID fornecido na requisição. Progresso não será enviado.")
    
    try:
        app.logger.info(f"Iniciando download da URL: {url} (SID: {sid})")
        file_path = downloader.download_video(url, sid)
        app.logger.info(f"Arquivo baixado e mesclado: {file_path}")
        
        base_filename = os.path.basename(file_path)
        title, ext = os.path.splitext(base_filename)
        sanitized_title = re.sub(r'[^a-zA-Z0-9\.\-_]', '_', title)
        sanitized_filename = f"{sanitized_title}.mp4"
        
        # Enviar progresso final (90% a 100%) sem estimativa de tempo
        if sid:
            steps = 5  # Dividir em 5 passos (90% a 100% = 10%, 2% por passo)
            for i in range(steps):
                progress = 90 + (i + 1) * (10 / steps)
                socketio.emit('progress', {
                    'progress': progress
                }, room=sid)
                app.logger.debug(f"Progresso de envio: {progress}% (SID: {sid})")
                time.sleep(0.1)  # Pequeno delay para simular o envio

        # Usar send_file com suporte a transferências parciais
        app.logger.debug(f"Iniciando envio do arquivo: {file_path}")
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=sanitized_filename,
            mimetype='video/mp4',
            conditional=True,  # Suporte a Range requests
            max_age=0  # Desativar cache para evitar problemas
        )
        app.logger.info(f"Arquivo {file_path} enviado com sucesso como {sanitized_filename}.")
        return response

    except Exception as e:
        app.logger.error(f"Erro ao processar download: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f"Falha no download: {str(e)}"}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        downloader.cleanup()
        app.logger.info("Arquivos temporários limpos com sucesso.")
        return jsonify({'message': 'Arquivos limpos com sucesso'}), 200
    except Exception as e:
        app.logger.error(f"Erro ao limpar arquivos: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f"Falha ao limpar arquivos: {str(e)}"}), 500

@socketio.on('connect')
def handle_connect():
    app.logger.info(f"Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    app.logger.info(f"Cliente desconectado: {request.sid}")

if __name__ == '__main__':
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', 5000))
    print(f"Iniciando o servidor em http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False)