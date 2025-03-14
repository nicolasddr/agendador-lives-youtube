# Agendador de Transmissões para YouTube

Este aplicativo permite agendar múltiplas transmissões no YouTube de forma eficiente, especialmente útil para igrejas e organizações que realizam transmissões regulares.

## Funcionalidades

- Coleta de dados de múltiplas transmissões (título, pregador, data, horário)
- Suporte para entrada individual ou em lote (colando um texto)
- Associação de imagens de capa para cada transmissão
- Agendamento de transmissões como "não listadas" ou "públicas"
- Opção para tornar as transmissões públicas após o agendamento
- Exibição dos links gerados para cada transmissão
- Opção para salvar os resultados em um arquivo de texto
- **Integração com a API oficial do YouTube**

## Requisitos

- Python 3.6 ou superior
- Bibliotecas Python (instaláveis via `pip install -r requirements.txt`):
  - google-auth
  - google-auth-oauthlib
  - google-api-python-client
  - python-dotenv

## Configuração da API do YouTube

Para usar a integração com a API do YouTube, você precisa:

1. Criar um projeto no [Console de Desenvolvedores do Google](https://console.developers.google.com/)
2. Ativar a API do YouTube para o projeto
3. Criar credenciais OAuth 2.0 para aplicativo de desktop
4. Baixar o arquivo JSON de credenciais e salvá-lo como `client_secret.json` no diretório raiz do projeto
5. Copiar o arquivo `.env.example` para `.env` e ajustar as configurações conforme necessário

### Instruções Detalhadas

1. Acesse o [Console de Desenvolvedores do Google](https://console.developers.google.com/)
2. Crie um novo projeto ou selecione um existente
3. No menu lateral, clique em "Biblioteca" e procure por "YouTube Data API v3"
4. Ative a API clicando no botão "Ativar"
5. No menu lateral, clique em "Credenciais"
6. Clique em "Criar credenciais" e selecione "ID do cliente OAuth"
7. Configure a tela de consentimento OAuth (se solicitado)
8. Selecione "Aplicativo de desktop" como tipo de aplicativo
9. Dê um nome para o cliente OAuth e clique em "Criar"
10. Baixe o arquivo JSON clicando no botão de download
11. Renomeie o arquivo para `client_secret.json` e coloque-o no diretório raiz do projeto

## Como Usar

1. Instale as dependências:
   ```
   pip3 install -r requirements.txt
   ```

2. Configure a API do YouTube conforme as instruções acima

3. Execute o script principal:
   ```
   python3 main.py
   ```
   
   **Nota:** Em alguns sistemas, você pode precisar usar `python3` em vez de `python` para garantir que está usando a versão correta do Python.

4. Siga as instruções na tela para inserir os dados das transmissões.

### Modos de Entrada

#### 1. Entrada Individual (Interativa)

Neste modo, você insere os dados de cada transmissão um por vez, seguindo os prompts na tela.

#### 2. Entrada em Lote

Este modo permite colar um texto contendo os dados de múltiplas transmissões de uma vez. O formato esperado é:

```
Título: [título da transmissão]
Pregador: [nome do pregador]
Data: [data no formato DD/MM/AAAA]
Horário: [horário no formato HH:MM]

Título: [título da próxima transmissão]
Pregador: [nome do próximo pregador]
Data: [data no formato DD/MM/AAAA]
Horário: [horário no formato HH:MM]
```

**Importante:** Separe cada transmissão com uma linha em branco.

**Exemplo de entrada em lote:**

```
Título: Culto de Adoração
Pregador: Pastor João
Data: 15/04/2023
Horário: 19:00

Título: Estudo Bíblico
Pregador: Pastor Pedro
Data: 17/04/2023
Horário: 20:00

Título: Culto de Jovens
Pregador: Ana
Data: 18/04/2023
Horário: 19:30
```

Após colar o texto, pressione Enter e depois:
- No Mac/Linux: pressione Ctrl+D
- No Windows: pressione Ctrl+Z seguido de Enter

### Imagens de Capa

Após inserir os dados das transmissões, o aplicativo solicitará o nome da pasta que contém as imagens de capa. As imagens devem estar na mesma ordem das transmissões inseridas.

O aplicativo mostrará como as imagens serão associadas às transmissões e pedirá sua confirmação antes de prosseguir.

### Agendamento

O aplicativo perguntará se você deseja agendar as transmissões como "não listadas". Se confirmar, o agendamento será realizado. Em seguida, você terá a opção de tornar as transmissões públicas.

### Resultado

Ao final do processo, o aplicativo exibirá os dados de cada transmissão junto com os links gerados. Você também terá a opção de salvar esses resultados em um arquivo de texto.

## Autenticação e Permissões

Na primeira execução, o aplicativo abrirá uma janela do navegador solicitando que você faça login na sua conta do Google e autorize o aplicativo a gerenciar seus vídeos do YouTube. Após a autorização, as credenciais serão salvas localmente para uso futuro.

## Observações

- O aplicativo agora utiliza a API oficial do YouTube para agendar transmissões.
- As credenciais de autenticação são armazenadas localmente no arquivo `token.pickle`.
- Certifique-se de que a conta do Google utilizada tenha permissões para gerenciar o canal do YouTube desejado.

## Melhorias Futuras

- Descrição e títulos personalizados
- Interface gráfica (GUI)
- Suporte para múltiplos canais
- Notificações por e-mail ou WhatsApp
- Geração de relatórios detalhados
- Agendamento de transmissões recorrentes 
