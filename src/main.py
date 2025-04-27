from src.chatbot.chatbot import chatbot_respond

if __name__ == "__main__":
    print("Welcome to Restaurant Chatbot!")
    while True:
        query = input("\nAsk your question (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        response = chatbot_respond(query)
        print(f"\n🤖 Bot: {response}")
