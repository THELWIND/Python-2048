#1 Migrate Database:
python manage.py makemigrations
python manage.py migrate

#2 Tạo Superuser (để vào admin xem điểm):
python manage.py createsuperuser

#3 Chạy server:
python manage.py runserver

Truy cập http://127.0.0.1:8000/.
Sẽ bị chuyển hướng đến trang Login.
Bấm "Register" để tạo tài khoản mới.
Sau khi đăng ký xong sẽ tự login và vào trang Game (/game/).
Chơi game (dùng phím mũi tên).
thua (để tiles đầy màn hình) -> Game sẽ in "Game Over" và gửi điểm về API.
Trình duyệt sẽ hiện Alert: "Score saved successfully!".s
Xem điểm (Quyền Host/Admin):
Truy cập http://127.0.0.1:8000/admin/.
Login bằng tài khoản superuser.
Vào mục Core > Game scores để xem danh sách điểm, thời gian chơi của người dùng.