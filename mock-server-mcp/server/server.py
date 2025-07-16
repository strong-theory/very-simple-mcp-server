import os
from fastmcp import FastMCP

mcp = FastMCP("Starting mcp server...")

@mcp.tool
def get_openapi(api_slug: str) -> str:
    """
    Cria um mock server de uma api;
    A identificação da api é dada pelo api_slug.
    """
    home_dir = os.getenv("HOME")
    file_name = f'{home_dir}/Downloads/openapi.json'
    with open(file_name, 'r') as file:
        open_api = file.read().replace("\n", "").replace("\t", "")
#         prompt = f"""
#         Apartir do open_api delimitado por <<<< e >>>>, faça:
#         1. Crie um diretorio temporario.
#         2. Salve o open_api nesse diretorio temporario.
#         3. Faça um arquivo de configuração, dentro do diretorio temporario, para o mockserver baseado no json abaixo:
#         """ + "{" + """
#             "specUrlOrPayload": "file:/Users/jamesbloom/git/mockserver/mockserver/mockserver-core/target/test-classes/org/mockserver/openapi/openapi_petstore_example.json"
#         """ + "}" + f"""
#         4. Deverá substituir o valor do parametro specUrlOrPayload pelo diretorio do file do openapi baixado.
#         5. Por fim execute o comando docker run para subir uma imagem docker do mockserver apontando pra esse arquivo de configuração.
#         Para executar o comando docker, deve ser criado um volume que aponte para o diretorio temporario do arquivo json e de configuração gerado.
#         Para setar o diretorio deverá ser usada a variavel de ambiente  MOCKSERVER_INITIALIZATION_JSON_PATH: /config/configuration.json,
#         Não faça comando deamon do docker.
#         6. Não crie um comando para cada passo, simplismente execute os comandos necessários.
#         <<<<
#         {open_api}
#         >>>>

# """



        prompt = f"""
                Apartir do open_api delimitado por <<<< e >>>>, faça:
                Converta esse openapi para o formato utilizado pela imagem docker mockserver/mockserver.
                Faça todos os endpoints presentes no openapi original dentro de um arquivo json so.
                Não esqueca que o arquivo json é um array. Deve começar e terminar com colchetes.
                E separar cada json de cada path com virgula.
                Utilize os schemas de cada method para fazer o response adequado, se tiver response.
                Respeite os status codes.
                Salve esse arquivo do mockserver em um diretorio temporario.
                Por fim execute o comando docker run para subir uma imagem docker do mockserver apontando pra esse diretorio temporario.
                Deve ser criado um volume que aponte para o diretorio temporario do arquivo json de configuração gerado.
                Para setar o diretorio deverá ser usada a variavel de ambiente  MOCKSERVER_INITIALIZATION_JSON_PATH: /config/*.json,
                nesse caso aceita comandos pra setar * todos os arquivos.
                Não faça comando deamon do docker.
                <<<<
                {open_api}
                >>>>

        """

        return prompt
    return None


# old_prompt = f"""
#         Apartir do open_api delimitado por <<<< e >>>>, faça:
#         Converta esse openapi para o formato utilizado pela imagem docker mockserver/mockserver.
#         Faça todos os endpoints presentes no openapi original. Separe cada rota em um arquivo json diferente.
#         Salve esse arquivo do mockserver em um diretorio temporario.
#         Por fim execute o comando docker run para subir uma imagem docker do mockserver apontando pra esse diretorio temporario.
#         Deve ser criado um volume que aponte para o diretorio temporario do arquivo json de configuração gerado.
#         Para setar o diretorio deverá ser usada a variavel de ambiente  MOCKSERVER_INITIALIZATION_JSON_PATH: /config/*.json,
#         nesse caso aceita comandos pra setar * todos os arquivos.
#         Não faça comando deamon do docker.
#         <<<<
#         {open_api}
#         >>>>

# """

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",           # Bind to all interfaces
        port=9000,                # Custom port
        log_level="DEBUG",        # Override global log level
        path="/openapi-mcp"
    )