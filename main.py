import os
import sys
import time
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Importa as funções da API do YouTube
from youtube_api import (
    get_authenticated_service,
    agendar_transmissao,
    atualizar_status_transmissao,
    formatar_descricao,
    converter_data_hora
)

# Carrega variáveis de ambiente
load_dotenv()

# Nome da organização (usado na descrição)
ORGANIZATION_NAME = os.getenv('ORGANIZATION_NAME', 'Igreja')

def coletar_dados_transmissoes() -> List[Dict[str, str]]:
    """
    Coleta os dados das transmissões via terminal.
    Permite duas formas de entrada:
    1. Entrada individual (interativa)
    2. Entrada em lote (colando um texto com múltiplas transmissões)
    
    Retorna uma lista de dicionários com os dados de cada transmissão.
    """
    transmissoes = []
    
    print("=== ENTRADA DE DADOS DAS TRANSMISSÕES ===")
    print("Escolha o modo de entrada:")
    print("1. Entrada individual (interativa)")
    print("2. Entrada em lote (colar texto com múltiplas transmissões)")
    
    modo = input("\nEscolha uma opção (1 ou 2): ").strip()
    
    # Coleta do texto personalizado para descrição (comum para todas as transmissões)
    print("\n=== TEXTO PERSONALIZADO PARA DESCRIÇÃO ===")
    print("Informe um texto personalizado que será adicionado à descrição de todas as transmissões (opcional):")
    print("Pressione Enter para pular ou digite o texto:")
    texto_descricao = input().strip()
    
    if modo == "1":
        # Modo interativo (original)
        print("\nInsira os dados das transmissões (pressione Enter duas vezes para finalizar):")
        
        while True:
            print(f"\nTransmissão #{len(transmissoes) + 1}")
            titulo = input("Título: ").strip()
            if not titulo and not transmissoes:
                print("Pelo menos uma transmissão deve ser informada.")
                continue
            elif not titulo:
                break
                
            pregador = input("Pregador: ").strip()
            data = input("Data (DD/MM/AAAA): ").strip()
            horario = input("Horário (HH:MM): ").strip()
            
            # Validação básica
            if not all([titulo, pregador, data, horario]):
                print("Todos os campos são obrigatórios. Tente novamente.")
                continue
                
            transmissao = {
                "titulo": titulo,
                "pregador": pregador,
                "data": data,
                "horario": horario,
                "texto_descricao": texto_descricao,  # Adiciona o texto de descrição
                "link": None  # Será preenchido após o agendamento
            }
            
            transmissoes.append(transmissao)
            print("Transmissão adicionada. Pressione Enter duas vezes para finalizar ou continue com a próxima.")
    
    elif modo == "2":
        # Modo de entrada em lote
        print("\nCole o texto com os dados das transmissões no seguinte formato:")
        print("Título: [título da transmissão]")
        print("Pregador: [nome do pregador]")
        print("Data: [data no formato DD/MM/AAAA]")
        print("Horário: [horário no formato HH:MM]")
        print("\nSepare cada transmissão com uma linha em branco.")
        print("Após colar o texto, pressione Enter e depois Ctrl+D (Unix/Mac) ou Ctrl+Z seguido de Enter (Windows) para finalizar.")
        
        print("\n--- Cole seu texto abaixo ---")
        
        # Lê todas as linhas até EOF (Ctrl+D ou Ctrl+Z)
        linhas = []
        try:
            while True:
                linha = input()
                linhas.append(linha)
        except EOFError:
            pass
        
        # Processa o texto colado
        texto_completo = "\n".join(linhas)
        blocos = texto_completo.split("\n\n")
        
        for bloco in blocos:
            if not bloco.strip():
                continue
                
            linhas_bloco = bloco.strip().split("\n")
            dados = {}
            
            for linha in linhas_bloco:
                if not linha.strip():
                    continue
                    
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    chave = chave.strip().lower()
                    valor = valor.strip()
                    
                    if chave == "título" or chave == "titulo":
                        dados["titulo"] = valor
                    elif chave == "pregador":
                        dados["pregador"] = valor
                    elif chave == "data":
                        dados["data"] = valor
                    elif chave == "horário" or chave == "horario":
                        dados["horario"] = valor
            
            # Validação básica
            campos_obrigatorios = ["titulo", "pregador", "data", "horario"]
            if all(campo in dados for campo in campos_obrigatorios):
                dados["texto_descricao"] = texto_descricao  # Adiciona o texto de descrição
                dados["link"] = None  # Será preenchido após o agendamento
                transmissoes.append(dados)
            else:
                campos_faltantes = [campo for campo in campos_obrigatorios if campo not in dados]
                print(f"Aviso: Transmissão ignorada por falta de campos: {', '.join(campos_faltantes)}")
                if "titulo" in dados:
                    print(f"Título da transmissão ignorada: {dados['titulo']}")
    
    else:
        print("Opção inválida. Usando modo interativo por padrão.")
        return coletar_dados_transmissoes()
    
    # Exibe resumo das transmissões coletadas
    if transmissoes:
        print(f"\nForam coletadas {len(transmissoes)} transmissões:")
        for i, t in enumerate(transmissoes):
            print(f"{i+1}. {t['titulo']} - {t['data']} {t['horario']}")
    else:
        print("\nNenhuma transmissão foi coletada.")
    
    return transmissoes

def obter_arquivos_capa(transmissoes: List[Dict[str, str]]) -> Optional[List[str]]:
    """
    Solicita o nome da pasta com as capas e verifica se há correspondência
    com o número de transmissões.
    """
    pasta_capas = input("\nInforme o nome da pasta que contém as capas: ").strip()
    
    if not os.path.exists(pasta_capas):
        print(f"Erro: A pasta '{pasta_capas}' não foi encontrada.")
        return None
        
    arquivos = [f for f in os.listdir(pasta_capas) if os.path.isfile(os.path.join(pasta_capas, f)) 
                and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if len(arquivos) != len(transmissoes):
        print(f"Erro: O número de arquivos de capa ({len(arquivos)}) é diferente do número de transmissões ({len(transmissoes)}).")
        print(f"Arquivos encontrados: {', '.join(arquivos)}")
        return None
    
    # Ordenar arquivos (pode ser necessário ajustar a lógica de ordenação)
    arquivos.sort()
    
    # Exibe como os arquivos serão associados às transmissões
    print("\nAssociação de capas às transmissões:")
    for i, (arquivo, transmissao) in enumerate(zip(arquivos, transmissoes)):
        print(f"{i+1}. {transmissao['titulo']} -> {arquivo}")
    
    confirmacao = input("\nConfirma a associação acima? (s/n): ").lower()
    if confirmacao != 's':
        print("Associação cancelada pelo usuário.")
        return None
    
    return [os.path.join(pasta_capas, arquivo) for arquivo in arquivos]

def agendar_transmissoes(transmissoes: List[Dict[str, str]], capas: List[str], nao_listado: bool = True) -> bool:
    """
    Agenda as transmissões no YouTube usando a API oficial.
    """
    print("\n=== AGENDAMENTO DE TRANSMISSÕES ===")
    print(f"Status inicial: {'Não listadas' if nao_listado else 'Públicas'}")
    print(f"Total de transmissões a agendar: {len(transmissoes)}")
    
    # Obtém o serviço autenticado da API do YouTube
    try:
        print("\nAutenticando com a API do YouTube...")
        youtube = get_authenticated_service()
        print("Autenticação concluída com sucesso!")
    except Exception as e:
        print(f"Erro ao autenticar com a API do YouTube: {str(e)}")
        return False
    
    # Define o status de privacidade
    privacidade = 'unlisted' if nao_listado else 'public'
    
    # Agenda cada transmissão
    for i, (transmissao, capa) in enumerate(zip(transmissoes, capas)):
        print(f"\nAgendando transmissão {i+1}/{len(transmissoes)}:")
        print(f"  Título: {transmissao['titulo']}")
        print(f"  Pregador: {transmissao['pregador']}")
        print(f"  Data/Horário: {transmissao['data']} às {transmissao['horario']}")
        print(f"  Capa: {os.path.basename(capa)}")
        
        # Prepara os dados para a API
        titulo = transmissao['titulo']
        descricao = formatar_descricao(
            transmissao['pregador'], 
            transmissao['data'], 
            transmissao['horario'],
            transmissao.get('texto_descricao', '')  # Passa o texto personalizado, se existir
        )
        data_inicio = converter_data_hora(
            transmissao['data'], 
            transmissao['horario']
        )
        
        # Simula o tempo de processamento para feedback visual
        print("  Processando...", end="", flush=True)
        
        # Chama a API para agendar a transmissão
        sucesso, link, erro = agendar_transmissao(
            youtube=youtube,
            titulo=titulo,
            descricao=descricao,
            data_inicio=data_inicio,
            privacidade=privacidade,
            thumbnail_path=capa
        )
        
        if sucesso:
            print(" concluído!")
            transmissao['link'] = link
            print(f"  Link gerado: {link}")
        else:
            print(" falhou!")
            print(f"  Erro: {erro}")
            return False
    
    print("\nTodas as transmissões foram agendadas com sucesso!")
    return True

def atualizar_status_transmissoes(transmissoes: List[Dict[str, str]], publico: bool = True) -> bool:
    """
    Atualiza o status de privacidade das transmissões usando a API oficial.
    """
    print("\n=== ATUALIZAÇÃO DE STATUS DAS TRANSMISSÕES ===")
    print(f"Novo status: {'Públicas' if publico else 'Não listadas'}")
    print(f"Total de transmissões a atualizar: {len(transmissoes)}")
    
    # Obtém o serviço autenticado da API do YouTube
    try:
        youtube = get_authenticated_service()
    except Exception as e:
        print(f"Erro ao autenticar com a API do YouTube: {str(e)}")
        return False
    
    # Define o novo status de privacidade
    novo_status = 'public' if publico else 'unlisted'
    
    # Atualiza cada transmissão
    for i, transmissao in enumerate(transmissoes):
        print(f"\nAtualizando transmissão {i+1}/{len(transmissoes)}:")
        print(f"  Título: {transmissao['titulo']}")
        print(f"  Link: {transmissao['link']}")
        
        # Extrai o ID do vídeo do link
        video_id = transmissao['link'].split('v=')[1] if 'v=' in transmissao['link'] else transmissao['link']
        
        # Simula o tempo de processamento para feedback visual
        print("  Processando...", end="", flush=True)
        
        # Chama a API para atualizar o status
        sucesso, erro = atualizar_status_transmissao(
            youtube=youtube,
            video_id=video_id,
            privacidade=novo_status
        )
        
        if sucesso:
            print(" concluído!")
        else:
            print(" falhou!")
            print(f"  Erro: {erro}")
            return False
    
    print("\nTodas as transmissões foram atualizadas com sucesso!")
    return True

def exibir_resultados(transmissoes: List[Dict[str, str]]) -> None:
    """
    Exibe os resultados finais com os links gerados.
    """
    print("\n=== RESULTADO FINAL ===")
    
    for i, transmissao in enumerate(transmissoes):
        print(f"\nTransmissão #{i+1}")
        print(f"Título: {transmissao['titulo']}")
        print(f"Pregador: {transmissao['pregador']}")
        print(f"Data: {transmissao['data']}")
        print(f"Horário: {transmissao['horario']}")
        print(f"Link: {transmissao['link']}")
    
    print("\nProcesso concluído com sucesso!")

def salvar_resultados(transmissoes: List[Dict[str, str]], nome_arquivo: str = "resultados.txt") -> None:
    """
    Salva os resultados das transmissões em um arquivo de texto.
    """
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write("=== RESULTADO DO AGENDAMENTO DE TRANSMISSÕES ===\n\n")
            
            for i, transmissao in enumerate(transmissoes):
                arquivo.write(f"Transmissão #{i+1}\n")
                arquivo.write(f"Título: {transmissao['titulo']}\n")
                arquivo.write(f"Pregador: {transmissao['pregador']}\n")
                arquivo.write(f"Data: {transmissao['data']}\n")
                arquivo.write(f"Horário: {transmissao['horario']}\n")
                arquivo.write(f"Link: {transmissao['link']}\n\n")
            
            arquivo.write("Processo concluído com sucesso!\n")
        
        print(f"\nResultados salvos no arquivo: {nome_arquivo}")
        return True
    except Exception as e:
        print(f"\nErro ao salvar resultados: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("=== AGENDADOR DE TRANSMISSÕES PARA YOUTUBE ===")
    print("=" * 50)
    print("\nEste aplicativo permite agendar múltiplas transmissões no YouTube.")
    
    # Verifica se o arquivo de segredos do cliente existe
    client_secrets_file = os.getenv('CLIENT_SECRETS_FILE', 'client_secret.json')
    if not os.path.exists(client_secrets_file):
        print(f"\nATENÇÃO: O arquivo de segredos do cliente '{client_secrets_file}' não foi encontrado.")
        print("Você precisa baixar este arquivo do Console de Desenvolvedores do Google.")
        print("Instruções:")
        print("1. Acesse https://console.developers.google.com/")
        print("2. Crie um projeto (ou selecione um existente)")
        print("3. Ative a API do YouTube para o projeto")
        print("4. Crie credenciais OAuth 2.0 para aplicativo de desktop")
        print("5. Baixe o arquivo JSON e salve-o como 'client_secret.json' no diretório raiz deste projeto")
        
        continuar = input("\nDeseja continuar mesmo assim? (s/n): ").lower()
        if continuar != 's':
            print("Operação cancelada pelo usuário.")
            return
    
    # Etapa 1: Coleta de dados
    print("\n--- ETAPA 1: COLETA DE DADOS ---")
    transmissoes = coletar_dados_transmissoes()
    if not transmissoes:
        print("Nenhuma transmissão informada. Encerrando.")
        return
    
    # Etapa 2: Obtenção das capas
    print("\n--- ETAPA 2: SELEÇÃO DE CAPAS ---")
    capas = None
    while capas is None:
        capas = obter_arquivos_capa(transmissoes)
        if capas is None:
            retry = input("Deseja tentar novamente? (s/n): ").lower()
            if retry != 's':
                print("Operação cancelada pelo usuário.")
                return
    
    # Etapa 3: Confirmação do modo "não listado"
    print("\n--- ETAPA 3: CONFIGURAÇÃO DE PRIVACIDADE ---")
    modo_nao_listado = input("Deseja agendar as transmissões como 'não listadas'? (s/n): ").lower() == 's'
    if not modo_nao_listado:
        reiniciar = input("Você optou por não agendar como 'não listadas'. Deseja reiniciar o processo? (s/n): ").lower()
        if reiniciar == 's':
            print("\nReiniciando o processo...\n")
            main()  # Reinicia o processo
            return
    
    # Etapa 4: Agendamento das transmissões
    print("\n--- ETAPA 4: AGENDAMENTO DAS TRANSMISSÕES ---")
    if not agendar_transmissoes(transmissoes, capas, nao_listado=modo_nao_listado):
        print("Erro ao agendar transmissões. Operação cancelada.")
        return
    
    # Etapa 5: Atualização para público (se solicitado)
    print("\n--- ETAPA 5: ATUALIZAÇÃO DE STATUS (OPCIONAL) ---")
    tornar_publico = input("Deseja tornar as transmissões públicas agora? (s/n): ").lower() == 's'
    if tornar_publico:
        if not atualizar_status_transmissoes(transmissoes, publico=True):
            print("Erro ao atualizar status das transmissões.")
            return
    
    # Etapa 6: Exibição dos resultados
    print("\n--- ETAPA 6: RESULTADOS FINAIS ---")
    exibir_resultados(transmissoes)
    
    # Etapa 7: Salvar resultados (opcional)
    salvar = input("\nDeseja salvar os resultados em um arquivo? (s/n): ").lower() == 's'
    if salvar:
        nome_arquivo = input("Nome do arquivo (padrão: resultados.txt): ").strip()
        if not nome_arquivo:
            nome_arquivo = "resultados.txt"
        salvar_resultados(transmissoes, nome_arquivo)
    
    print("\nObrigado por usar o Agendador de Transmissões!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação interrompida pelo usuário. Encerrando...")
    except Exception as e:
        print(f"\n\nErro inesperado: {str(e)}")
        import traceback
        traceback.print_exc() 