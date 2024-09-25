from langchain.memory import ConversationBufferWindowMemory

def create_memory(messages: list[dict] = [], human_prefix:str = "Human", ai_prefix: str = "AI", k:int=3) -> ConversationBufferWindowMemory:
    memory = ConversationBufferWindowMemory(k=3, input_key="input", output_key="output", human_prefix="Użytkownik", ai_prefix="Asystent",return_messages=True, memory_key="chat_history")
    input = output = ""

    for message in messages:
        if message.get("ai_response", None):
            output = message.get("content", "")
            memory.save_context({"input": input}, {"output": output})
        else:
            input = message.get("content", "")

    return memory