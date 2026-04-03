#!/usr/bin/env bash
# Thoát ngay nếu có lỗi
set -o errexit

# Cài đặt các thư viện
pip install -r requirements.txt

# Thu thập file tĩnh
python manage.py collectstatic --no-input

# Cập nhật database (Sẽ tạo db.sqlite3 tự động trên Render)
python manage.py migrate
