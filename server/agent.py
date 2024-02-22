from server.db import find_user, update_chat

async def process_chat(chat):
    # This is the main function that processes a chat
    # It should call the OpenAI API to get a response
    # and update the chat object with the response
    # and assistant logs
    
    print("Starting CHAT PROCESSING {}".format(chat["id"]))

    # check for user's NPL status
    user = await find_user(chat["user_id"])
    if user is None:
        return chat

    if user["NPL_status"] == "NPL":
        chat["chat_messages"].append({
            "type": "system",
            "message": "ขออภัยค่ะ คุณไม่ได้รับสิทธิ์ในการใช้บริการนี้เนื่องจากมีหนี้ค้างชำระกับทางธนาคาร กรุณาติดต่อธนาคารเพื่อขอข้อมูลเพิ่มเติมค่ะ"
        })

        chat["assistant_logs"].append({
            "type": "assistant",
            "message": "User is not eligible for this service due to NPL status"
        })
        await update_chat(chat)
        return chat

    