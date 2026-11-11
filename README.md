# HealthTree ID3 – Dự án Python + giao diện web

## 1. Giới thiệu
Ứng dụng minh họa phân lớp dữ liệu sức khỏe bằng cây quyết định ID3. Backend được viết bằng Python/Flask, giao diện bằng HTML/CSS/JavaScript.

Thuật toán bám theo tài liệu PDF đã cung cấp:
- Entropy(S) = -Σ p(c) log2 p(c)
- Gain(S,A) = Entropy(S) - Σ (|Sv|/|S|) Entropy(Sv)
- Chọn thuộc tính có Information Gain lớn nhất.
- Xây dựng cây đệ quy; dừng khi tập con thuần nhất hoặc hết thuộc tính.
- Mỗi đường đi từ gốc đến lá tương ứng một luật phân lớp.

## 2. Yêu cầu
- Python 3.10 trở lên (khuyến nghị Python 3.11/3.12)
- pip

## 3. Cài đặt và chạy trên Windows
Giải nén thư mục dự án, mở CMD/PowerShell tại thư mục `healthtree_id3_project`, sau đó chạy:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Mở trình duyệt tại:
http://127.0.0.1:5000

## 4. Cài đặt và chạy trên macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Mở http://127.0.0.1:5000

## 5. Chức năng
- Chọn 1 trong 5 bộ bài toán minh họa: tiểu đường, tăng huyết áp, nguy cơ tim mạch, sốt xuất huyết, thiếu máu.
- Mỗi bộ có 5 thuộc tính đầu vào riêng.
- Dự đoán bằng cây ID3 được huấn luyện từ dữ liệu đang có.
- Xem cây quyết định, Entropy và Information Gain ở nút gốc.
- Thêm, sửa giá trị, xóa mẫu, khôi phục dữ liệu minh họa.
- Nhập CSV và xuất CSV.
- Tự đổi tên 5 thuộc tính, các giá trị thuộc tính và tên cột kết quả.

## 6. Định dạng CSV
CSV phải có 6 cột: 5 thuộc tính đầu vào và 1 cột nhãn ở cuối. Ví dụ:

```csv
DuongHuyet,BMI,HuyetAp,KhatNuoc,MetMoi,KetQua
Cao,Beo phi,Cao,Thuong xuyen,Nhieu,Tieu duong
Binh thuong,Binh thuong,Binh thuong,Khong,Khong,Khong benh
```

Các thuộc tính là dữ liệu phân loại (nominal), đúng với phạm vi ID3 trong tài liệu. Nếu có giá trị mới, hãy đưa giá trị đó vào danh sách giá trị của thuộc tính trong tab Tùy chỉnh trước khi nhập dữ liệu.

## 7. Cấu trúc thư mục

```text
healthtree_id3_project/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── style.css
```

## 8. Lưu ý học thuật và y tế
Các bộ dữ liệu mẫu được tạo để minh họa luồng hoạt động của ID3, KHÔNG phải dữ liệu bệnh nhân thật, không được xem là dữ liệu lâm sàng có kiểm chứng. Kết quả ứng dụng không phải chẩn đoán y khoa. Nếu dùng trong báo cáo nghiên cứu, cần thay bằng dữ liệu có nguồn, mô tả cách thu thập, kiểm tra chất lượng nhãn và đánh giá trên tập kiểm tra độc lập.
