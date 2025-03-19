import os
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env, se existir
load_dotenv()

# Configurações da API
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_FILE', 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/youtube']
TOKEN_PICKLE_FILE = 'token.pickle'

def get_authenticated_service():
    """
    Autentica o usuário e retorna o serviço da API do YouTube.
    """
    credentials = None

    # Tenta carregar as credenciais do arquivo pickle
    if os.path.exists(TOKEN_PICKLE_FILE):
        print("Carregando credenciais salvas...")
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            credentials = pickle.load(token)

    # Se não há credenciais válidas, solicita ao usuário que faça login
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Atualizando credenciais expiradas...")
            credentials.refresh(Request())
        else:
            print("Obtendo novas credenciais...")
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"Arquivo de segredos do cliente não encontrado: {CLIENT_SECRETS_FILE}. "
                    "Baixe-o do Console de Desenvolvedores do Google e salve-o no diretório raiz do projeto."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Salva as credenciais para a próxima execução
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(credentials, token)

    # Constrói o serviço
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def agendar_transmissao(
    youtube, 
    titulo: str, 
    descricao: str, 
    data_inicio: datetime, 
    privacidade: str = 'unlisted',
    thumbnail_path: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Agenda uma transmissão ao vivo no YouTube.
    
    Args:
        youtube: Serviço autenticado da API do YouTube
        titulo: Título da transmissão
        descricao: Descrição da transmissão
        data_inicio: Data e hora de início da transmissão
        privacidade: Status de privacidade ('public', 'private', 'unlisted')
        thumbnail_path: Caminho para a imagem de miniatura (opcional)
        
    Returns:
        Tupla contendo (sucesso, id_da_transmissao, mensagem_de_erro)
    """
    try:
        # Formata a data para o formato ISO 8601 requerido pela API
        start_time = data_inicio.isoformat() + 'Z'  # 'Z' indica UTC
        
        # Cria a transmissão
        broadcast_insert_response = youtube.liveBroadcasts().insert(
            part="snippet,status,contentDetails",
            body={
                "snippet": {
                    "title": titulo,
                    "description": descricao,
                    "scheduledStartTime": start_time
                },
                "status": {
                    "privacyStatus": privacidade
                },
                "contentDetails": {
                    "enableAutoStart": True,
                    "enableAutoStop": True
                }
            }
        ).execute()
        
        broadcast_id = broadcast_insert_response["id"]
        
        # Cria o stream
        stream_insert_response = youtube.liveStreams().insert(
            part="snippet,cdn",
            body={
                "snippet": {
                    "title": titulo
                },
                "cdn": {
                    "frameRate": "variable",
                    "ingestionType": "rtmp",
                    "resolution": "variable"
                }
            }
        ).execute()
        
        stream_id = stream_insert_response["id"]
        
        # Vincula o stream à transmissão
        youtube.liveBroadcasts().bind(
            part="id,contentDetails",
            id=broadcast_id,
            streamId=stream_id
        ).execute()
        
        # Se uma imagem de miniatura foi fornecida, faz o upload
        if thumbnail_path and os.path.exists(thumbnail_path):
            from googleapiclient.http import MediaFileUpload
            
            youtube.thumbnails().set(
                videoId=broadcast_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
        
        # Retorna o ID da transmissão e o link
        video_url = f"https://youtube.com/watch?v={broadcast_id}"
        return True, video_url, None
        
    except HttpError as e:
        error_content = e.content.decode("utf-8")
        return False, None, f"Erro na API do YouTube: {error_content}"
    except Exception as e:
        return False, None, f"Erro ao agendar transmissão: {str(e)}"

def atualizar_status_transmissao(
    youtube, 
    video_id: str, 
    privacidade: str
) -> Tuple[bool, Optional[str]]:
    """
    Atualiza o status de privacidade de uma transmissão.
    
    Args:
        youtube: Serviço autenticado da API do YouTube
        video_id: ID da transmissão
        privacidade: Novo status de privacidade ('public', 'private', 'unlisted')
        
    Returns:
        Tupla contendo (sucesso, mensagem_de_erro)
    """
    try:
        # Obtém os detalhes atuais da transmissão
        broadcast = youtube.liveBroadcasts().list(
            part="status",
            id=video_id
        ).execute()
        
        if not broadcast.get("items"):
            return False, f"Transmissão com ID {video_id} não encontrada."
        
        # Atualiza o status de privacidade
        youtube.liveBroadcasts().update(
            part="status",
            body={
                "id": video_id,
                "status": {
                    "privacyStatus": privacidade
                }
            }
        ).execute()
        
        return True, None
        
    except HttpError as e:
        error_content = e.content.decode("utf-8")
        return False, f"Erro na API do YouTube: {error_content}"
    except Exception as e:
        return False, f"Erro ao atualizar status da transmissão: {str(e)}"

def formatar_descricao(pregador: str, data: str, horario: str, texto_personalizado: str = "") -> str:
    """
    Retorna o texto personalizado como descrição da transmissão.
    Se nenhum texto personalizado for fornecido, retorna uma string vazia.
    
    Args:
        pregador: Nome do pregador (não utilizado na descrição)
        data: Data da transmissão (não utilizado na descrição)
        horario: Horário da transmissão (não utilizado na descrição)
        texto_personalizado: Texto personalizado para usar como descrição
    """
    # Retorna apenas o texto personalizado como descrição
    return texto_personalizado

def converter_data_hora(data_str: str, hora_str: str) -> datetime:
    """
    Converte strings de data e hora para um objeto datetime.
    Considera o fuso horário do Brasil (UTC-4).
    
    Args:
        data_str: Data no formato DD/MM/AAAA
        hora_str: Hora no formato HH:MM
        
    Returns:
        Objeto datetime já com o ajuste para UTC
    """
    from datetime import timedelta
    
    # Converte para datetime no horário local
    data_completa = f"{data_str} {hora_str}"
    data_hora_local = datetime.strptime(data_completa, "%d/%m/%Y %H:%M")
    
    # Ajusta o fuso horário para UTC (Brasil é UTC-4)
    fuso_horario_brasil = -4  # horas
    data_hora_utc = data_hora_local + timedelta(hours=-fuso_horario_brasil)
    
    return data_hora_utc 