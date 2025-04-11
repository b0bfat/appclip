### AppClip - YouTube Video Downloader
Visão Geral
AppClip é uma aplicação web que permite aos usuários baixar vídeos do YouTube em formato MP4 com áudio e vídeo mesclados. A aplicação é composta por um backend em Python (usando Flask) e um frontend em HTML/JavaScript, com o yt-dlp como biblioteca principal para download e o ffmpeg para mesclagem de vídeo e áudio.

O projeto foi desenvolvido para rodar em um servidor Windows, com suporte a múltiplos downloads simultâneos, limpeza automática de arquivos temporários e conversão de áudio para o formato AAC (compatível com a maioria dos players).

### Estrutura do Projeto
O projeto está organizado da seguinte forma:

appclip/
├── backend/
│   ├── app.py              # Arquivo principal do backend (Flask)
│   ├── downloader.py       # Módulo para download e mesclagem de vídeos
│   ├── downloads/          # Diretório para armazenar arquivos temporários
│   └── cookies.txt         # Arquivo de cookies (opcional, para autenticação)
├── frontend/
│   ├── static/
│   │   └── style.css       # Estilos CSS do frontend
│   └── templates/
│       └── index.html      # Página principal do frontend
└── README.md               # Documentação do projeto

### Backend
- app.py: Configura o servidor Flask, define as rotas (/, /download, /cleanup) e gerencia o envio de arquivos ao cliente.
- downloader.py: Contém a classe VideoDownloader, responsável por baixar vídeos do YouTube usando yt-dlp, mesclar vídeo e áudio com ffmpeg, e limpar arquivos temporários.
- downloads/: Diretório onde os vídeos são temporariamente armazenados durante o download e mesclagem.
- cookies.txt: Arquivo opcional para autenticação em vídeos restritos (ex.: vídeos que requerem login).

### Frontend
- index.html: Interface do usuário, com um formulário para inserir a URL do vídeo e um script JavaScript para interagir com o backend.
- style.css: Arquivo de estilos para a interface (minimalista).


## Dependências
- Backend
    Python 3.13.2 (ou superior)
    Flask: Framework web para o backend.
    Flask-SocketIO: Para suportar WebSockets (barra de andamento) no Flask
    yt-dlp: Biblioteca para baixar vídeos do YouTube.
    waitress: Servidor WSGI para rodar o Flask em produção.
    ffmpeg: Ferramenta para mesclagem de vídeo e áudio (instalado em C:\app\python-lib\ffmpeg\bin).
    ffprobe: Parte do pacote ffmpeg, usado para verificar a presença de áudio nos arquivos.

- Frontend
    Socket.IO (via CDN): Para comunicação em tempo real com o backend (atualizações de progresso).

## Instalação
1. Configuração do Ambiente
    -   Instale o Python:
            Baixe e instale o Python 3.13.2 (ou superior) em python.org.
            Certifique-se de adicionar o Python ao PATH durante a instalação.
    -   Instale o ffmpeg:
            Baixe o ffmpeg em ffmpeg.org.
            Extraia para C:\app\python-lib\ffmpeg.
            Adicione C:\app\python-lib\ffmpeg\bin ao PATH do sistema:
            No Windows, vá para Painel de Controle → Sistema → Configurações Avançadas → Variáveis de Ambiente → Editar PATH.
    -   Verifique a instalação:
            CLI: ffmpeg -version
            CLI: ffprobe -version
    -   Clone o Projeto:
            Crie um diretório para o projeto
                CLI: mkdir C:\app\appclip
                CLI: cd C:\app\appclip
            Clone ou copie os arquivos do projeto para C:\app\appclip

2. Instale as Dependências do Python
    -   Crie um ambiente virtual (opcional, mas recomendado)
            CLI: python -m venv venv
            CLI: .\venv\Scripts\activate
    -   Instale as dependências
            CLI: pip install flask yt-dlp waitress

3. Configure o Diretório de Downloads
    -    Certifique-se de que o diretório C:\app\appclip\backend\downloads existe. Ele será criado automaticamente pelo downloader.py se não existir. 

### Arquivos do Projeto
- backend/app.py - https://github.com/b0bfat/appclip/blob/main/backend/app.py
- backend/downloader.py - https://github.com/b0bfat/appclip/blob/main/backend/downloader.py
- frontend/templates/index.html - https://github.com/b0bfat/appclip/blob/main/frontend/templates/index.html
- frontend/static/style.css - https://github.com/b0bfat/appclip/blob/main/frontend/static/style.css

### Como Executar
1.  Inicie o Servidor:
    -   Navegue até o diretório do backend
            CLI: cd C:\app\appclip\backend
    -   Execute o servidor:
            CLI: python app.py
    -   O servidor será iniciado em http://192.168.151.231:5000 (ou outro IP/porta configurado).

2.  Acesse a Interface:
    -   Abra um navegador e acesse http://192.168.151.231:5000
    -   Insira a URL de um vídeo do YouTube (ex.: https://www.youtube.com/watch?v=ong1ROJJuYM) e clique em "Baixar Vídeo".

3.  Download e Limpeza:
    -   O vídeo será baixado com áudio e vídeo mesclados em formato MP4.
    -   Após o download, os arquivos temporários serão limpos automaticamente.

### Funcionamento Técnico
-   Fluxo de Download
1.  O usuário insere a URL do vídeo no frontend e envia uma requisição POST para /download.
2.  O backend (app.py) chama o método download_video() do VideoDownloader (downloader.py).
3.  O VideoDownloader:
    -   Usa o yt-dlp para baixar o vídeo e o áudio separadamente (formatos bestvideo e bestaudio).
    -   Mescla os arquivos usando o ffmpeg, convertendo o áudio para AAC.
    -   Verifica se o arquivo final tem áudio usando o ffprobe.
    -   Retorna o caminho do arquivo final ao app.py.
4.  O app.py envia o arquivo ao cliente usando send_file.
5.  O frontend chama a rota /cleanup para excluir os arquivos temporários.

### Detalhes Técnicos
-   Identificador Único: Cada download gera um identificador único (uuid) para evitar conflitos entre downloads simultâneos.
-   Conversão de Áudio: O áudio é convertido para AAC (-c:a aac -b:a 192k) para garantir compatibilidade com a maioria dos players.
-   Limpeza de Arquivos: O método cleanup() tenta excluir os arquivos temporários com até 5 tentativas, com um atraso de 1 segundo entre tentativas, para lidar com bloqueios de arquivo no Windows.
-   Sanitização de Nomes: O nome do arquivo é sanitizado no app.py para substituir caracteres especiais por underscores (_).
