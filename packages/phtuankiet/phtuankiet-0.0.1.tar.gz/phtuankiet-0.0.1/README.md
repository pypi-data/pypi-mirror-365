Một thư viện Python đơn giản để gửi tin nhắn và tệp qua Telegram Bot một cách nhanh chóng.

Cài đặt
Generated bash
pip install phtuankiet

Sử dụng

Bạn cần có chat_id của người nhận hoặc nhóm chat.

Generated python
from phtuankiet import sendtelegram

# Gửi một tin nhắn văn bản
sendtelegram(chat_id="ID_CHAT_CUA_BAN", msg="Chào bạn, đây là tin nhắn tự động!")

# Gửi một tệp tin
# Tạo một tệp ví dụ
with open("test.txt", "w") as f:
    f.write("Đây là nội dung của tệp.")

sendtelegram(chat_id="ID_CHAT_CUA_BAN", file_path="test.txt")

# Gửi một tệp tin kèm theo chú thích
sendtelegram(chat_id="ID_CHAT_CUA_BAN", msg="Đây là tệp báo cáo nhé!", file_path="test.txt")

# sendtelegram(
#     chat_id="ID_CHAT_CUA_BAN",
#     msg="Gửi bằng token khác",
#     token="TOKEN_BOT_KHAC_CUA_BAN"
# )
