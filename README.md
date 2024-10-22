# VryBot - Bot Interativo do Discord

VryBot é um bot interativo do Discord projetado para fornecer respostas breves e engraçadas. Com uma pitada de sarcasmo, ele utiliza a API do Google Gemini para gerar conteúdo dinâmico e criativo.

## Funcionalidades

- Respostas baseadas em prompts que definem a personalidade do bot.
- Armazenamento de histórico de mensagens para contextos mais relevantes.
- Configurações de segurança para evitar conteúdos inapropriados.

## Pré-requisitos

Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina. Você também precisará de suas chaves de API para o Discord e o Google Gemini.

## Instalação

1. Clone este repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_DIRETORIO>
Crie um ambiente virtual (opcional, mas recomendado):

python -m venv venv
source venv/bin/activate  # Para Linux/Mac
venv\Scripts\activate  # Para Windows
Instale as dependências:

bash:
pip install -r requirements.txt
Crie dois arquivos de texto:

APIGEMINI.txt: Insira sua chave de API do Google Gemini.
APIDISCORDBOT.txt: Insira sua chave de API do Discord.


Uso
Execute o bot:

bash:
python <NOME_DO_ARQUIVO>.py
No Discord, interaja com o bot utilizando comandos que começam com v!. Por exemplo:

Exemplo: "v! Como você está?

Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

Licença
Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para mais detalhes.
