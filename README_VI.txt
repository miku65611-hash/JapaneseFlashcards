JAPANESE FLASHCARDS v2 - PYTHON / KIVY

TÍNH NĂNG
1. Phát âm tiếng Nhật: nút 🔊 dùng Android Text-to-Speech (TTS) hệ thống.
   Để dùng hoàn toàn ngoại tuyến, hãy cài giọng tiếng Nhật offline trong cài đặt
   Text-to-Speech của Android/Google Speech Services. Tính khả dụng tùy thiết bị.
   Trên máy tính có thể cài thêm pyttsx3 và giọng tiếng Nhật tương ứng.
2. Thống kê tiến độ: tổng từ, đã thuộc, chưa thuộc, từ đến hạn ôn, lượt ôn và thống kê chủ đề.
3. Ôn tập thông minh: trả lời đúng sẽ tăng khoảng cách ôn (1, 2, 4, 9... ngày,
   tối đa 60 ngày); trả lời sai đưa từ về lịch ôn hôm nay.
4. Sao lưu và khôi phục: tạo JapaneseFlashcards_backup.json trong thư mục dữ liệu
   riêng của ứng dụng; chọn file JSON để khôi phục. Hãy giữ bản sao lưu ở nơi an toàn.
5. Kiểm tra trắc nghiệm: tối đa 10 câu mỗi lượt, 4 lựa chọn nếu có đủ từ.
6. Dark Mode: nút GIAO DIỆN chuyển đổi sáng/tối.
7. Phân loại theo chủ đề: chọn chủ đề khi thêm từ và lọc trong danh sách.
8. Học, thêm từ, tìm kiếm, xóa, đánh dấu đã thuộc/chưa thuộc.
9. Dữ liệu được lưu cục bộ bằng JSON. Ứng dụng không gọi API hay cần Internet.

CHẠY TRÊN MÁY TÍNH
1. Cài Python 3.10 trở lên.
2. pip install -r requirements.txt
3. python main.py
   Phát âm trên desktop là tùy chọn: pip install pyttsx3 và cài giọng Nhật hệ thống.

TẠO APK ANDROID
Buildozer được hỗ trợ tốt nhất trên Linux/Ubuntu hoặc WSL2.
1. Cài các phụ thuộc Buildozer theo tài liệu chính thức:
   https://buildozer.readthedocs.io/
2. Trong thư mục dự án chạy: pip install buildozer
3. Chạy: buildozer android debug
4. APK nằm trong thư mục bin/.

LƯU Ý QUAN TRỌNG
- ZIP này là mã nguồn Python, không phải APK cài trực tiếp.
- TTS ngoại tuyến phụ thuộc việc thiết bị đã cài giọng đọc tiếng Nhật offline.
- Sao lưu được lưu trong vùng dữ liệu riêng của app. Trên Android mới, quyền truy cập
  thư mục Downloads bị giới hạn; hãy dùng trình quản lý tệp của thiết bị để giữ bản
  sao lưu ở vị trí an toàn và chọn file JSON khi khôi phục nếu trình chọn tệp cho phép.
- Lịch ôn được lưu theo ngày trên thiết bị.
