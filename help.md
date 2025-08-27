# Các phần mềm cần thiết trong project

1. Editor: Visual Studio Code
2. Python
3. Mysql Workbench

# Các extension visual studio code

1. Python (Microsoft)
2. Django
3. Material Icon Theme

# Khám phá Django

- Link Document 5.2: https://docs.djangoproject.com/en/5.2/
- Xem version Django: py -m django --version
- Tạo project mới: django-admin startproject my-project
- Chạy server: py manage.py runserver
- Đổi port: py manage.py runserver port-number
- Tạo app mới: py manage.py startapp my-app
- py manage.py migrations
- Tạo mới, áp dụng sự thay đổi cho CSDL:py manage.py migrate
- Tạo user mới: py manage.py createsuperuser

# Áp dụng MySql

- Tạo database mới tạo MySql Workbench
- Config database tại settings.py
- Chạy lệnh py manage.py migrate

# Các câu lệnh

- Liệt kê toàn bộ các package và phiên bản đang cài trong môi trường: pip freeze > requirements.txt
- Tự động xóa các file media: pip install django-cleanup
