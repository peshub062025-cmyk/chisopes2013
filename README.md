# ⚽ Discord Bot - Tra cứu chỉ số cầu thủ PES13

## 📁 Cấu trúc project
```
discord-bot-pes/
├── bot.py            ← Code chính
├── data.xls          ← File dữ liệu PES13 (11,302 cầu thủ)
├── .env              ← Token bot (tạo từ .env.example)
├── requirements.txt  ← Thư viện cần cài
```

---

## 🚀 Cài đặt

### Bước 1: Tạo Discord Bot (miễn phí)
1. Vào https://discord.com/developers/applications → **New Application**
2. Tab **Bot** → **Add Bot**
3. Bật **MESSAGE CONTENT INTENT** (bắt buộc, vì bot đọc nội dung tin nhắn thường, không chỉ lệnh `!`)
4. **Reset Token** → copy lại, giữ bí mật
5. **OAuth2 > URL Generator** → scope `bot`, permission `Send Messages`, `Read Message History`, `Embed Links` → mở URL → invite vào server

### Bước 2: Cài thư viện
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình token
```bash
cp .env.example .env
# Mở .env, dán token vào
```

### Bước 4: Chạy
```bash
python bot.py
```

---

## 💬 Cách dùng

Gõ thẳng tên cầu thủ vào kênh chat, không cần lệnh:
```
Messi
```

**Nếu chỉ khớp 1 người** → bot trả về ngay toàn bộ chỉ số:
```
**NAME**: Lionel Messi
**AGE**: 36
**NATIONALITY**: Argentina
**FOOT**: L
**HEIGHT**: 170
**WEAK FOOT ACCURACY**: 6
...
**CLUB TEAM**: INTER MIAMI

**SKILLS**: 1-TOUCH PLAY, LONG RANGE DRIVE, DOUBLE TOUCH, TRICKSTER, ...
```

**Nếu khớp nhiều người** (ví dụ gõ "Messi" trùng vài bản ghi, hoặc tên phổ biến như "Ronaldo") → bot hiện **menu thả xuống (dropdown)** để bạn chọn đúng người, sau đó hiện đầy đủ chỉ số.

> Lưu ý: dữ liệu PES có nhiều cầu thủ trùng tên (phiên bản theo năm/CLB khác nhau, ví dụ "Adriano - Inter Milan 2006" và "Adriano - Barcelona 2013"), nên cơ chế chọn lựa rất hữu ích để tránh nhầm.

### Lệnh
| Lệnh | Mô tả |
|------|-------|
| `!reload` | Đọc lại file Excel sau khi bạn cập nhật `data.xls` |
| `!help_bot` | Xem hướng dẫn |

---

## 🔄 Cập nhật dữ liệu
1. Sửa file `data.xls` (vẫn giữ đúng tên cột, sheet tên `Worksheet`)
2. Gõ `!reload` trong Discord — không cần khởi động lại bot

> File hiện tại ~16MB, bot cache dữ liệu trong RAM sau lần đọc đầu để trả lời nhanh, không phải đọc lại Excel mỗi câu hỏi.

---

## 💰 Có mất phí không?
**Không, hoàn toàn miễn phí** nếu bạn tự chạy:
- Discord Bot API: miễn phí, không giới hạn server nhỏ-vừa
- Các thư viện Python: mã nguồn mở, miễn phí
- Chạy trên máy tính cá nhân: miễn phí (nhưng máy phải bật thì bot mới online)

**Muốn bot online 24/7 mà không cần mở máy:**
- [Railway](https://railway.app) — free tier ~500 giờ/tháng
- [Render](https://render.com) — free tier (tự ngủ khi không dùng, có thể chậm lúc đầu)
- VPS giá rẻ (Vultr, DigitalOcean...) — khoảng $4-6/tháng nếu muốn ổn định tuyệt đối

---

## ⚠️ Lưu ý kỹ thuật
- File `.xls` (định dạng Excel cũ) cần thư viện `xlrd`, **không dùng được** `openpyxl` (chỉ đọc `.xlsx`)
- Cột `S01-S26` (kỹ năng đặc biệt) và `P01-P18` (playstyle) là cờ nhị phân: `1` = cầu thủ sở hữu kỹ năng, `0` = không có. Bot chỉ liệt kê các kỹ năng có giá trị `1` để tránh rối mắt.
