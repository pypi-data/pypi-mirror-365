import requests
import os

__all__ = ['sendtelegram']

DEFAULT_TOKEN = "8216345887:AAF61dDyWmur-BJ7-NLME77w_PcDDIOJDfI"

def sendtelegram(chat_id, msg=None, file_path=None, token=None):
    token_to_use = token if token else DEFAULT_TOKEN

    if not token_to_use or not chat_id:
        print("Cần Có Token Và ChatID.")
        return

    if not msg and not file_path:
        print("Cần Có Tin Nhắn (msg) Hoặc Đuờng Dẫn Tệp (file_path).")
        return

    base_url = f"https://api.telegram.org/bot{token_to_use}"

    if file_path:
        if not os.path.exists(file_path):
            print(f"Lỗi Tệp Không Tồn Tại: {file_path}")
            return
        
        url = f"{base_url}/sendDocument"
        files = {'document': open(file_path, 'rb')}
        data = {'chat_id': chat_id}
        if msg:
            data['caption'] = msg
        
        try:
            r = requests.post(url, data=data, files=files)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Gửi Tệp Thất Bại: {e}")

    elif msg:
        url = f"{base_url}/sendMessage"
        data = {'chat_id': chat_id, 'text': msg}
        
        try:
            r = requests.post(url, data=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Gửi Tin Nhắn Đến Telegram Faild: {e}")