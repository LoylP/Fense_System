import json
from tools.LLMs import describe_request
from tools.check import (
    check_url_virustotal, parse_vt_result_for_display,
    check_email_validity, parse_email_result,
    check_phone_validity, parse_phone_result
)
from tools.search_googleapi import search_google_api
from tools.rag_database import rag_db
from tools.url_info import get_domain_info
from typing import Optional
from crewai import Task
from agents import Agents

class Pipeline:
    def __init__(self, text_input: str, image_path: Optional[str] = None):
        self.text_input = text_input
        self.image_path = image_path
        self.result = None

    def build_context(self):
        parsed = describe_request(self.text_input, self.image_path)
        self.parsed = parsed
        self.keywords = parsed.get("keyword", [])
        self.query = " ".join(self.keywords)

        self.urls_info = [parse_vt_result_for_display(check_url_virustotal(url)) for url in parsed.get("urls", [])]
        self.domain_details = [get_domain_info(url) for url in parsed.get("urls", [])]
        self.emails_info = [parse_email_result(check_email_validity(email)) for email in parsed.get("emails", [])]
        self.phones_info = [parse_phone_result(check_phone_validity(phone)) for phone in parsed.get("phones", [])]
        self.web_results = search_google_api(self.query).to_dict(orient="records")[:5] if self.query else []
        self.db_results = rag_db(self.query)

        self.context = {
            "request": parsed.get("request"),
            "summary": parsed.get("summary"),
            "keywords": self.keywords,
            "urls": self.urls_info,
            "domain_info": self.domain_details,
            "emails": self.emails_info,
            "phones": self.phones_info,
            "web": self.web_results,
            "db": self.db_results
        }

    def build_task(self, agent):
        prompt = f"""
            Yêu cầu người dùng: {self.context['request']}
            Tóm tắt: {self.context['summary']}
            Từ khóa: {', '.join(self.context['keywords'])}
            URL check: {json.dumps(self.context['urls'], ensure_ascii=False)}
            Domain Info (IP, registrar, org...): {json.dumps(self.context['domain_info'], ensure_ascii=False)}
            Email check: {json.dumps(self.context['emails'], ensure_ascii=False)}
            Phone check: {json.dumps(self.context['phones'], ensure_ascii=False)}
            Web results: {json.dumps(self.context['web'], ensure_ascii=False)}
            Internal DB results (BM25 + TFIDF): {json.dumps(self.context['db'], ensure_ascii=False)}

            Lưu ý cho AI: Cảnh báo nếu domain mới đăng ký, tổ chức không rõ ràng, hoặc IP trỏ đến quốc gia/vùng đáng ngờ (nếu có).
            Ngoài ra một số kết quả từ RAG có thể không liên quan. 
            Chỉ sử dụng những phần thực sự hữu ích để xác minh thông tin người dùng.
        """
        return Task(
            description=(
                "Phân tích dữ liệu bên dưới và đưa ra đánh giá rõ ràng theo cấu trúc:\n"
                "1. Kết luận (✅ An toàn / ⚠️ Đáng ngờ / ❌ Lừa đảo)\n"
                "2. Giải thích lý do\n"
                "3. Gợi ý hành động\n\n"
                + prompt
            ),
            expected_output="Kết luận ngắn gọn, rõ ràng, đúng cấu trúc yêu cầu.",
            agent=agent
        )

    def run(self):
        self.build_context()
        agents = Agents()
        task = self.build_task(agents.verifier)
        crew = agents.build_crew(task)
        self.result = crew.kickoff()
        return self.result
