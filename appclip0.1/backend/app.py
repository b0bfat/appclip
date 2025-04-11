from flask import Flask, render_template, request, send_file, jsonify
from downloader import VideoDownloader
import os
from waitress import serve
import re

app = Flask(__name__, 
           static_folder='../frontend/static',
           template_folder='../frontend/templates')

downloader = VideoDownloader()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL não fornecida'}), 400

    url = data['url']
    try:
        file_path = downloader.download_video(url)
        base_filename = os.path.basename(file_path)
        sanitized_filename = re.sub(r'[^a-zA-Z0-9\.\-_]', '_', base_filename)
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=sanitized_filename,
            mimetype='video/mp4'
        )
        app.logger.info(f"Arquivo {file_path} enviado com sucesso como {sanitized_filename}.")
        return response
    except Exception as e:
        return jsonify({'error': f"Falha no download: {str(e)}"}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        downloader.cleanup()
        return jsonify({'message': 'Arquivos limpos com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': f"Falha ao limpar arquivos: {str(e)}"}), 500

if __name__ == '__main__':
    print("Iniciando o servidor em http://192.168.151.231:5000")
    serve(app, host='0.0.0.0', port=5000)