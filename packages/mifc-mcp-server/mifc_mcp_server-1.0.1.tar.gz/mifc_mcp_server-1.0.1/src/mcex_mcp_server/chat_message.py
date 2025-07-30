import os
import requests
import json

def chat(content, bot_id, access_token):
    url = "https://api.coze.cn/v3/chat"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "bot_id": bot_id,
        "user_id": "123456789",
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": content,
                "content_type": "text"
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def retrieve(chat_id,conversation_id, access_token):
    url = 'https://api.coze.cn/v3/chat/retrieve'
    params = {
        'chat_id': chat_id,
        'conversation_id': conversation_id
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()

def list_message(chat_id,conversation_id, access_token):
    url = f"https://api.coze.cn/v3/chat/message/list?chat_id={chat_id}&conversation_id={conversation_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()




if __name__ == '__main__':
    pass

