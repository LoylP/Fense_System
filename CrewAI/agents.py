from crewai import Agent, Crew
from langchain_openai import ChatOpenAI

class Agents:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0.2)
        self.input_parser = Agent(
            role="Input Analyzer",
            goal="Tóm tắt nội dung và trích xuất thông tin",
            backstory="Bạn là AI chuyên phân tích đầu vào người dùng để phục vụ xác minh.",
            tools=[],
            llm=self.llm,
            verbose=True
        )
        self.checker = Agent(
            role="Entity Checker",
            goal="Kiểm tra độ tin cậy của URL, email, số điện thoại",
            backstory="Bạn đánh giá rủi ro các thực thể đã trích xuất.",
            tools=[],
            llm=self.llm,
            verbose=True
        )
        self.searcher = Agent(
            role="Web Researcher",
            goal="Tìm kiếm thông tin từ Google để hỗ trợ xác minh",
            backstory="Bạn sử dụng Google để xác minh thông tin.",
            tools=[],
            llm=self.llm,
            verbose=True
        )
        self.db_researcher = Agent(
            role="Database Researcher",
            goal="Phân tích kết quả tìm kiếm từ database và chọn lọc thông tin thực sự liên quan đến yêu cầu người dùng.",
            backstory=(
                "Bạn có quyền truy cập vào cơ sở dữ liệu tin tức nội bộ. "
                "Kết quả tìm kiếm có thể chứa các bài viết không liên quan hoặc không hữu ích. "
                "Nhiệm vụ của bạn là đọc kỹ từng đoạn, chọn lọc thông tin nào thực sự có giá trị trong việc xác minh nội dung người dùng cung cấp. "
                "Bỏ qua các bài viết không liên quan hoặc không giúp ích trong đánh giá tính xác thực."
            ),
            tools=[],
            llm=self.llm,
            verbose=True
        )
        self.verifier = Agent(
            role="Final Verifier",
            goal="Đưa ra kết luận cuối cùng về tính xác thực",
            backstory="Tổng hợp thông tin và đánh giá độ an toàn của yêu cầu người dùng.",
            tools=[],
            llm=self.llm,
            verbose=True
        )

    def build_crew(self, task):
        return Crew(
            agents=[
                self.input_parser,
                self.checker,
                self.searcher,
                self.db_researcher,
                self.verifier
            ],
            tasks=[task],
            verbose=True
        )