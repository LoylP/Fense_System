import os
import base64
import json
import ast
from dotenv import load_dotenv
from openai import OpenAI

# Load API key từ file .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

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
                    "Hãy mô tả ảnh (nếu có), tóm tắt và làm rõ yêu cầu của người dùng, trích xuất từ khóa quan trọng"
                    "(liên quan đến địa điểm, tổ chức, nội dung gây tranh cãi). "
                    "Trả kết quả ở định dạng JSON như: "
                    "{'summary': ..., 'keywords': [...], 'request_user': ...}"
                )
            }

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[system_prompt, {"role": "user", "content": messages}],
                max_tokens=700
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bạn là trợ lý AI (Phản hồi đúng ngôn ngữ người dùng hỏi). Tóm tắt và làm rõ yêu cầu của người dùng, trích xuất từ khóa quan trọng (keyword), "
                            "xác định loại yêu cầu, và trả về định dạng JSON như:\n\n"
                            "{'summary': ..., 'keywords': [...], 'request_user': ...}"
                        )
                    },
                    {
                        "role": "user",
                        "content": text_input
                    }
                ],
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
                return {
                    "summary": data.get("summary"),
                    "request": data.get("raw_content") or text_input,
                    "keyword": data.get("keywords", [])
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
#         text_input="Bản đồ này có đúng không",
#         image_path="/home/phuc/project/FakeBuster_System/public/duongluoibo.png"
#     )
#     print(json.dumps(result, indent=2, ensure_ascii=False))
