---
mode: agent
---
Se receber um comando para gerar mockserver de uma api, primeiro acesse o mcp e faça o download do openapi.
Converta esse openapi para o formato utilizado pela imagem docker mockserver/mockserver.
Salve esse arquivo do mockserver em um diretorio temporario.
Por fim execute o comando docker run para subir uma imagem docker do mockserver apontando pra esse diretorio temporario.
Deve ser criado um volume que aponte para o diretorio temporario do arquivo json de configuração gerado.
Para setar o diretorio deverá ser usada a variavel de ambiente  MOCKSERVER_INITIALIZATION_JSON_PATH: /config/*.json
O comando docker não deve ser deamon
