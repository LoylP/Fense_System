import re

def extract_contact_info(text: str) -> str:
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

text1 = "Bạn có thể nhắn tin lỗi qua ngawawdw@email.com hoặc Liên hệ qua https://example.com hoặc contact 0912345678"
email, phone, url = extract_contact_info(text1)
print("Email:", email)
print("Phone:", phone)
print("URL:", url)