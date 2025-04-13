# TOEIC Mock Test Generator 📝

## 📌 Tổng Quan
TOEIC Mock Test Generator là một ứng dụng web được xây dựng bằng Flask, cho phép người dùng luyện tập ngữ pháp và đọc hiểu tiếng Anh theo định dạng TOEIC. Ứng dụng sử dụng Gemini AI để tạo ra các câu hỏi ngẫu nhiên và độc đáo.

## ✨ Tính Năng Chính
- Tạo đề thi ngữ pháp TOEIC với 10 câu hỏi
- Tạo đề thi đọc hiểu TOEIC với 3 đoạn văn
- Giải thích chi tiết bằng tiếng Việt cho mỗi câu trả lời
- Hệ thống đăng nhập/đăng ký tài khoản người dùng
- Theo dõi chuỗi ngày làm bài liên tiếp (streak)
- Lưu và quản lý câu hỏi yêu thích
- Thay đổi mật khẩu tài khoản
- Giao diện thân thiện, responsive với người dùng
- Hiển thị kết quả và phân tích bài làm chi tiết
- Bằng việc thay đổi prompts.py, có thể chuyển web app này từ tạo câu hỏi TOEIC sang JLPT, TOPIK, HSK...

## 🌐 Web Demo
[TOEIC Mock Test Generator v1.0 - hosted by Render](https://toeic-test-generator.onrender.com/)

## 🛠 Công Nghệ Sử Dụng
- **Backend**: Python, Flask
- **Frontend**: HTML, TailwindCSS, JavaScript
- **AI**: Google Gemini 2.0 Flash
- **Cơ sở dữ liệu**: SQLite3, Flask-Session

## 📋 Yêu Cầu Hệ Thống
- Python 3.8+
- Google Gemini API key (đăng kí free từ [Google AI Studio](https://aistudio.google.com/apikey))
- SQLite3
- Trình duyệt web hiện đại

## ⚙️ Cài Đặt
1. Clone repository:
```bash
git clone <repository-url>
```

2. Tạo môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

4. Tạo file .env trong thư mục gốc và thêm các biến môi trường:
```bash
GEMINI_API_KEY=your_api_key
FLASK_SECRET_KEY=your_secret_key
```

5. Khởi tạo cơ sở dữ liệu:
```bash
# Database sẽ tự động được tạo khi chạy ứng dụng lần đầu
```

6. Chạy ứng dụng:
```bash
python app.py
```

## 🌐 Truy Cập Ứng Dụng
Mở trình duyệt và truy cập: http://localhost:5000

## 🚀 Tính Năng Người Dùng
- **Đăng ký/Đăng nhập**: Tạo tài khoản để lưu trữ tiến độ học tập
- **Streak**: Theo dõi chuỗi ngày làm bài liên tiếp
- **Yêu thích**: Lưu các câu hỏi yêu thích để ôn tập sau
- **Quản lý tài khoản**: Thay đổi mật khẩu, xem lịch sử làm bài
- **Dashboard**: Xem tổng quan tiến độ và thành tích

## 👥 Đóng Góp
Mọi đóng góp đều được hoan nghênh! Vui lòng:

1. Fork repository
2. Tạo nhánh mới (git checkout -b feature/AmazingFeature)
3. Commit thay đổi (git commit -m 'Add some AmazingFeature')
4. Push lên nhánh (git push origin feature/AmazingFeature)
5. Mở Pull Request

## 📄 Giấy Phép
Dự án này được phân phối dưới giấy phép MIT. Xem LICENSE để biết thêm thông tin.

## 🙏 Ghi Nhận
- Google Gemini API cho việc tạo câu hỏi
- TailwindCSS cho thiết kế giao diện
- SQLite3 cho cơ sở dữ liệu
- Flask và các extension đi kèm