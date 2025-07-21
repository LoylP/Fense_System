import os
import base64
import json
import ast
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load API key từ file .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_contact_info(text: str):
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    url_pattern = r"https?://[^\s]+|www\.[^\s]+"
    phone_pattern = r"(\+?84|0)?\s?(\d{9,10})"

    email = ''
    phone = ''
    url = ''

    email_match = re.search(email_pattern, text)
    if email_match:
        email = email_match.group(0)
    
    # Tìm URL đầu tiên
    url_match = re.search(url_pattern, text)
    if url_match:
        url = url_match.group(0)
    
    # Tìm số điện thoại đầu tiên
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        phone = "".join([g if g is not None else "" for g in phone_match.groups()]) if phone_match else ""

    return email, phone, url

def describe_request(text_input='Xác thực thông tin sau:', image_path=None):
    """
    Mô tả và trích xuất yêu cầu xác minh thông tin.
    Trả về dict gồm: summary, request (raw_content), keyword.
    Thêm cơ chế gọi lại tối đa 3 lần nếu kết quả chưa đúng định dạng.
    """
    if not text_input and not image_path:
        return {
            "summary": None,
            "request": None,
            "keyword": [],
            "error": "⚠️ Không có dữ liệu đầu vào"
        }

    def make_prompt_call():
        if image_path:
            base64_image = encode_image_to_base64(image_path)
            messages = []

            if text_input:
                messages.append({
                    "type": "text",
                    "text": f"Người dùng gửi ảnh kèm lời nhắn: {text_input}"
                })

            messages.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

            system_prompt = {
                "role": "system",
                "content": (
                    "Bạn là một trợ lý AI (Phản hồi đúng ngôn ngữ người dùng hỏi) chuyên xác minh thông tin. "
                    "Hãy mô tả ảnh (nếu có), tóm tắt và làm rõ yêu cầu của người dùng, trích xuất từ khóa quan trọng "
                    "(liên quan đến địa điểm, tổ chức, nội dung gây tranh cãi). "
                    "Ngoài ra, nếu có xuất hiện trong nội dung, hãy trích xuất thêm các trường: "
                    "`emails`, `phones`, `urls`.\n\n"
                    "Trả kết quả ở định dạng JSON như:\n"
                    "{'summary': ..., 'keywords': [...], 'request_user': ..., 'emails': [...], 'phones': [...], 'urls': [...]}."
                )
            }

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[system_prompt, {"role": "user", "content": messages}],
                max_tokens=700
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "system",
                    "content": (
                        "Bạn là trợ lý AI (Phản hồi đúng ngôn ngữ người dùng hỏi). "
                        "Hãy tóm tắt và làm rõ yêu cầu của người dùng ngắn gọn dễ hiểu. "
                        "Trả về định dạng JSON như:\n"
                        "{'summary': ..., 'keywords': [...], 'request_user': ..., 'emails': [...], 'phones': [...], 'urls': [...]}."
                    )
                },
                {
                    "role": "user",
                    "content": text_input
                }],
                max_tokens=700
            )
        return response.choices[0].message.content

    last_content = None
    for attempt in range(3):  # tối đa 3 lần
        try:
            content_str = make_prompt_call()
            last_content = content_str
            data = ast.literal_eval(content_str)

            if isinstance(data, dict) and data.get("summary"):
                # Trích xuất thông tin liên quan đến email, phone, và URL
                email, phone, url = extract_contact_info(text_input)
                return {
                    "summary": data.get("summary"),
                    "request": data.get("request_user") or text_input,
                    "keyword": data.get("keywords", []),
                    "phones": [phone] if phone else [],
                    "emails": [email] if email else [],
                    "urls": [url] if url else []
                }
        except Exception as e:
            continue  # thử lại lần sau

    # Nếu sau 3 lần vẫn không ổn, trả kết quả thô
    return {
        "summary": None,
        "request": last_content,
        "keyword": [],
        "error": "❌ Không trích xuất được dữ liệu sau 3 lần thử."
    }

# if __name__ == "__main__":
#     result = describe_request(
#         text_input="Một số điện thoại +85598765432 gọi đến tôi liên tục và dọa nạt, tôi lo là có hành vi lừa đảo."
#         # image_path="/home/phuc/project/FakeBuster_System/public/duongluoibo.png"
#     )
#     print(json.dumps(result, indent=2, ensure_ascii=False))
