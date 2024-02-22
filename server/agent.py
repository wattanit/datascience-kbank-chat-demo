from server.db import find_user, update_chat

async def process_chat(message, chat):
    # This is the main function that processes a chat
    # It should call the OpenAI API to get a response
    # and update the chat object with the response
    # and assistant logs
    
    print("Starting CHAT PROCESSING {}".format(chat["id"]))

    # new_chat_message = {
    #     "type": "user",
    #     "message": message
    # }
    # chat["chat_messages"].append(new_chat_message)

    # # call OpenAI to add the message
    # data = {
    #     "role": "user",
    #     "content": body.message
    # }
    # response = requests.post(f'https://api.openai.com/v1/threads/{chat["openai_thread_id"]}/messages', data=json.dumps(data), headers={
    #     'Content-Type': 'application/json',
    #     'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
    #     'OpenAI-Beta': 'assistants=v1'
    #     })

    
    