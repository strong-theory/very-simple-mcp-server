
from llm import ChatStackSpot
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

model = ChatStackSpot()

response = model.invoke([HumanMessage(content="Olá, tudo bem?")])
print(response.content)