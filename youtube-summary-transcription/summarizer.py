import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

dotenv.load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


def summary(transcription: str, user_input: str | None):

    if not user_input:
        user_input = """
        Faça um resumo detalhado da transcrição.
        Primeiro faça um resumo rapido dos princiapis topicos abordados no viedo.
        Em seguida aprofunde os topicos colocando mais detalhes.
        """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
                You are a helpful assistant that summaryzes a youtube video transcription.
                Translate the summary to the users request language.
                The transcription is bounded by <<<< and >>>>:
                <<<<
                {transcription}
                >>>>        
                """,
            ),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm

    ai_msg = chain.invoke({"input": user_input})

    return ai_msg.content
