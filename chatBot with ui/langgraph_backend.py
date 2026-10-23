from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage , HumanMessage
from typing import TypedDict , Annotated
from langgraph.graph.message import add_messages # reduser for BaseMessage same as operater.app (+)
from langgraph.checkpoint.memory import MemorySaver # this saves in RAM 


class chatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOllama(model="qwen2.5:1.5b")

def chat_node(state: chatState):
    messages= state['messages']
    responce= llm.invoke(messages)
    return {'messages': [responce]}

checkpoint=MemorySaver()

graph=StateGraph(chatState)

#nodes
graph.add_node('chat_node',chat_node)

# edges 
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatBot=graph.compile(checkpointer=checkpoint)
