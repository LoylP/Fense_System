import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()
SUSPICIOUS_COUNTRIES = {"Cambodia", "Nigeria", "Pakistan", "Afghanistan", "North Korea"}
VT_API_KEY = os.getenv("VT_API_KEY")
ABSTRACT_EMAIL_API = os.getenv("ABSTRACT_EMAIL_API")
ABSTRACT_PHONE_API = os.getenv("ABSTRACT_PHONE_API")

def check_url_virustotal(url):
    api_key = VT_API_KEY
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    vt_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"

    headers = {
        "x-apikey": api_key
    }

    response = requests.get(vt_url, headers=headers)
    return response.json()

def parse_vt_result_for_display(vt_json):
    try:
        data = vt_json["data"]["attributes"]
        stats = data["last_analysis_stats"]

        url = data.get("last_final_url", data.get("url", ""))

        harmless = stats.get("harmless", 0)
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0)

        # Đánh giá tổng quát
        if malicious > 0:
            overall = "Nguy hiểm"
        elif suspicious > 0:
            overall = "Có thể đáng ngờ"
        else:
            overall = "An toàn"

        results = {
            "url": url,
            "harmless": harmless,
            "malicious": malicious,
            "suspicious": suspicious,
            "undetected": undetected,
            "overall": overall
        }

        return results

    except Exception as e:
        return {
            "error": f"Không thể phân tích dữ liệu VirusTotal: {e}"
        }

def check_email_validity(email):
    api_key = ABSTRACT_EMAIL_API
    url = "https://emailvalidation.abstractapi.com/v1/"
    params = {
        "api_key": api_key,
        "email": email
    }
    response = requests.get(url, params=params)
    return response.json()

def parse_email_result(result):
    try:
        email = result.get("email", "N/A")
        deliverability = result.get("deliverability", "UNKNOWN")
        is_format_valid = result["is_valid_format"]["value"]
        is_smtp_valid = result["is_smtp_valid"]["value"]
        is_mx_found = result["is_mx_found"]["value"]
        is_free = result["is_free_email"]["value"]
        is_disposable = result["is_disposable_email"]["value"]
        is_role = result["is_role_email"]["value"]

        # Tổng kết hợp lệ
        is_valid = all([
            is_format_valid,
            is_smtp_valid,
            is_mx_found,
            deliverability == "DELIVERABLE"
        ])

        result_dict = {
            "email": email,
            "valid": is_valid,
            "deliverability": deliverability,
            "is_format_valid": is_format_valid,
            "is_smtp_valid": is_smtp_valid,
            "is_mx_found": is_mx_found,
            "is_free_email": is_free,
            "is_disposable_email": is_disposable,
            "is_role_email": is_role,
            "conclusion": (
                "Hợp lệ (SMTP & MX tồn tại)" if is_valid else
                "Không hợp lệ hoặc không gửi được"
            ),
            "description": {
                "type": "Miễn phí" if is_free else "Domain riêng",
                "spam": "Tạm thời / spam" if is_disposable else "Không phải spam",
                "role": "Đại diện tổ chức" if is_role else "Email cá nhân"
            }
        }

        return result_dict

    except Exception as e:
        return {
            "error": f"Không thể phân tích kết quả email: {e}"
        }

def normalize_phone_vn(phone: str) -> str:
    if phone.startswith("0") and len(phone) == 10:
        return "+84" + phone[1:]
    elif phone.startswith("+84"):
        return phone
    return phone

def check_phone_validity(phone):
    api_key = ABSTRACT_PHONE_API
    if not api_key:
        raise ValueError("❌ ABSTRACT_PHONE_API chưa được thiết lập trong .env")

    url = "https://phonevalidation.abstractapi.com/v1/"
    normalized_phone = normalize_phone_vn(phone)
    params = {
        "api_key": api_key,
        "phone": normalized_phone
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Lỗi API: {response.status_code} – {response.text}")

    return response.json()

# Hàm phân tích kết quả trả về
def parse_phone_result(result):
    try:
        phone = result.get("phone")
        valid = result.get("valid", False)
        country = result.get("country", {}).get("name", "")
        country_code = result.get("country", {}).get("code", "")
        intl_format = result.get("format", {}).get("international", "")
        local_format = result.get("format", {}).get("local", "")

        is_foreign = country and country != "Vietnam"
        is_high_risk = country in SUSPICIOUS_COUNTRIES

        return {
            "phone": phone,
            "valid": valid,
            "international_format": intl_format,
            "local_format": local_format,
            "country": country,
            "country_code": country_code,
            "location": result.get("location"),
            "carrier": result.get("carrier"),
            "type": result.get("type"),
            "is_foreign_number": is_foreign,
            "is_high_risk_country": is_high_risk,
            "conclusion": (
                "Không hợp lệ" if not valid else
                "Số từ quốc gia rủi ro (cần cẩn trọng)" if is_high_risk else
                "Số từ nước ngoài" if is_foreign else
                "Số hợp lệ nội địa"
            )
        }

    except Exception as e:
        return {
            "error": f"Lỗi phân tích dữ liệu số điện thoại: {e}"
        }

def build_checks_summary(url=None, email=None, phone=None):
    parts = []

    if url:
        url_result = check_url_virustotal(url)
        check_url = parse_vt_result_for_display(url_result)
        parts.append(f"Kết quả kiểm tra URL: {check_url}")

    if email:
        mail_result = check_email_validity(email)
        check_mail = parse_email_result(mail_result)
        parts.append(f"Kết quả kiểm tra Mail: {check_mail}")

    if phone:
        phone_result = check_phone_validity(phone)
        check_phone = parse_phone_result(phone_result)
        parts.append(f"Kết quả kiểm tra Phone: {check_phone}")

    return parts


# if __name__ == "__main__":
    # Bạn có thể thay bằng bất kỳ số nào
    # test_number = "0762509156"  # Việt Nam
    # test_number = "+85512345678"  # Campuchia

    # result = check_url_virustotal("https://www.malware-traffic-analysis.net/")
    # print(parse_vt_result_for_display(result))  

    # result = check_email_validity("nhphuc183@gmail.com")
    # print(parse_email_result(result))

    # result = check_phone_validity("85512345678")
    # print(result)