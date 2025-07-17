from fastmcp import FastMCP
from summarizer import summary
from documentation import generate
from transcript_downloader import download

mcp = FastMCP("Starting mcp server...")

@mcp.tool
def get_transcription_from_video(video_id: str) -> str:
    """
    Através do id de video do youtube, retorna a transcrição desse video.
    Exemplo: https://youtu.be/uvubLp5o5Wg?t=275, para essa url o video_id é uvubLp5o5Wg, ou seja,
    o video_id é o parametro v= da url quando a url é https://www.youtube.com/watch?v=uvubLp5o5Wg.
    Ou apenas depois do / quando a url é encurtada.
    """

    print("### chamando get_transcription_from_video ###")

    return download(video_id)


@mcp.tool
def summaryze_transcription(transcription: str, user_input: str | None) -> str:
    """
    Pega uma transcrição e faz um resumo dela utlizando o input do usuario.
    O campo user_input pode ser detalhes adicionais que o usuario selecionou para
    gerar o resumo.
    O user_input não é obrigatorio. Caso nao seja informado será gerado um resumo basico.
    """
    print("### chamando summaryze_transcription ###")
    return summary(transcription, user_input)


@mcp.tool
def create_documentation_from_sumarry(sumarry: str, user_input: str | None, file_path: str) -> str:
    """
    Pega o resumo e transforma em um arquivo markdown.
    O campo user_input pode ser detalhes adicionais que o usuario selecionou para
    gerar o resumo ou detalhes de como fazer a documentação.
    Salva a documentação no filesystem definida na variavel file_path.
    """
    
    print("### chamando create_documentation_from_sumarry ###")

    return generate(sumarry, user_input, file_path)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",           # Bind to all interfaces
        port=9000,                # Custom port
        log_level="DEBUG",        # Override global log level
        path="/youtube-summaryzer"
    )