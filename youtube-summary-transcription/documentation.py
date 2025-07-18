import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

dotenv.load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


def generate(summary: str, user_input: str | None, file_path: str):

    if not user_input:
        user_input = """
        Faça uma documentação em formato markdown do resumo do video
        Primeiro faça um resumo rapido dos princiapis topicos abordados no viedo.
        Em seguida aprofunde os topicos colocando mais detalhes.
        """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
                You are a helpful assistant that create a markdown document from a summary made from a youtube video transcript.
                Translate the markdown baseded on user's request language.
                The summary is bounded by <<<< and >>>>:
                <<<<
                {summary}
                >>>>        
                """,
            ),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm

    ai_msg = chain.invoke({"input": user_input})

    with open(file_path, "w") as file:
        file.write(ai_msg.content)
    return f"""
            Documentação salva no arquiv {file_path}!
            """
    