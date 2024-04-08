import requests as requests
import os

def SentLM_request(message, gpt_version):
    os.environ["http_proxy"] = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"
    # 在这里配置您在本站的API_KEY
    api_key = ""

    headers = {
        "Authorization": 'Bearer ' + api_key,
    }

    params = {
        "messages": message,
        # 如果需要切换模型，在这里修改
        "model": gpt_version
    }
    response = requests.post(
        "https://aigptx.top/v1/chat/completions",
        headers=headers,
        json=params,
        stream=False
    )
    res = response.json()
    res_content = res['choices'][0]['message']['content']

    return res_content
