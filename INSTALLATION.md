# 🚀 دليل التثبيت الكامل - SentraOS

<!-- دليل تثبيت شامل لمشروع SentraOS خطوة بخطوة -->

---

## 📋 المتطلبات الأساسية

قبل البدء في التثبيت، تأكد من توفر المتطلبات التالية:

### 1. نظام التشغيل
<!-- أنظمة التشغيل المدعومة -->
- **Ubuntu**: 20.04 أو أحدث (موصى به)
- **Debian**: 11 أو أحدث
- **CentOS/RHEL**: 8 أو أحدث
- **Windows**: 10/11 مع WSL2 (للتطوير فقط)

### 2. البرامج المطلوبة
<!-- البرامج الأساسية المطلوبة للتشغيل -->
```bash
# Python
Python 3.11 أو أحدث

# Nmap (للفحص الأمني)
nmap version 7.0 أو أحدث

# Git (للنسخ من المستودع)
Git version 2.0 أو أحدث
```

### 3. الصلاحيات
<!-- الصلاحيات المطلوبة -->
- صلاحيات **sudo** لتثبيت الحزم
- صلاحيات **root** لفحص المنافذ (اختياري - لـ SYN scan)

---

## 📦 التثبيت على Ubuntu/Debian

<!-- خطوات التثبيت الكاملة على Ubuntu/Debian -->

### الخطوة 1: تحديث النظام
```bash
# تحديث قائمة الحزم
sudo apt update

# ترقية الحزم المثبتة
sudo apt upgrade -y
```

### الخطوة 2: تثبيت البرامج الأساسية
```bash
# تثبيت Python 3.11 والأدوات المساعدة
sudo apt install -y python3.11 python3.11-venv python3-pip

# تثبيت nmap للفحص الأمني
sudo apt install -y nmap

# تثبيت Git
sudo apt install -y git

# تثبيت أدوات التطوير (اختياري)
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### الخطوة 3: إنشاء مجلد المشروع
```bash
# إنشاء مجلد للمشروع
sudo mkdir -p /var/www/sentraos

# تغيير المالك للمستخدم الحالي
sudo chown -R $USER:$USER /var/www/sentraos

# الانتقال للمجلد
cd /var/www/sentraos
```

### الخطوة 4: نسخ ملفات المشروع
```bash
# إذا كان المشروع على Git
git clone https://github.com/your-username/sentraos.git .

# أو نسخ الملفات يدوياً
# يمكنك استخدام scp أو رفع الملفات مباشرة
```

### الخطوة 5: إنشاء البيئة الافتراضية
```bash
# إنشاء بيئة افتراضية بـ Python 3.11
python3.11 -m venv venv

# تفعيل البيئة الافتراضية
source venv/bin/activate

# ترقية pip
pip install --upgrade pip
```

### الخطوة 6: تثبيت المكتبات المطلوبة
```bash
# تثبيت كل المكتبات من requirements.txt
pip install -r requirements.txt

# التحقق من التثبيت
pip list
```

### الخطوة 7: إعداد ملف التكوين
```bash
# نسخ ملف البيئة النموذجي
cp .env.example .env

# تعديل الإعدادات
nano .env
```

**محتوى ملف `.env`:**
```env
# إعدادات الخادم
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
FLASK_DEBUG=False
SERVER_IP=72.61.192.175

# الأمان
SESSION_SECRET=غير-هذا-المفتاح-السري-في-الإنتاج

# قاعدة البيانات
DATABASE_PATH=sentra.db

# المستخدم الافتراضي
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
DEFAULT_ADMIN_EMAIL=admin@sentraos.local
```

⚠️ **مهم جداً:** غيّر `SESSION_SECRET` لمفتاح قوي وفريد!

### الخطوة 8: تهيئة قاعدة البيانات
```bash
# تشغيل المشروع للمرة الأولى لإنشاء قاعدة البيانات
python3 main.py

# انتظر حتى تظهر رسالة "Database initialized"
# ثم اضغط Ctrl+C لإيقاف التشغيل
```

### الخطوة 9: اختبار التشغيل
```bash
# تشغيل المشروع
python3 main.py

# يجب أن تظهر رسالة:
# "Starting server on http://0.0.0.0:8080"
```

### الخطوة 10: الوصول للوحة التحكم
```bash
# افتح المتصفح وانتقل إلى:
http://SERVER_IP:8080

# بيانات الدخول الافتراضية:
# Username: admin
# Password: admin123
```

---

## 🔧 التثبيت على CentOS/RHEL

<!-- خطوات التثبيت على CentOS/RHEL -->

### الخطوة 1: تحديث النظام
```bash
sudo yum update -y
```

### الخطوة 2: تثبيت Python 3.11
```bash
# إضافة EPEL repository
sudo yum install -y epel-release

# تثبيت Python 3.11
sudo yum install -y python311 python311-pip python311-devel

# تثبيت أدوات التطوير
sudo yum groupinstall -y "Development Tools"
```

### الخطوة 3: تثبيت البرامج الإضافية
```bash
# تثبيت nmap
sudo yum install -y nmap

# تثبيت Git
sudo yum install -y git
```

### الخطوة 4-10: نفس الخطوات من Ubuntu/Debian
<!-- اتبع نفس الخطوات من 3 إلى 10 المذكورة أعلاه -->

---

## 🪟 التثبيت على Windows (للتطوير)

<!-- خطوات التثبيت على Windows -->

### الخطوة 1: تثبيت WSL2
```powershell
# فتح PowerShell كمسؤول وتشغيل:
wsl --install

# إعادة تشغيل الكمبيوتر
```

### الخطوة 2: تثبيت Ubuntu على WSL
```powershell
# تثبيت Ubuntu
wsl --install -d Ubuntu-22.04

# إنشاء مستخدم وكلمة مرور
```

### الخطوة 3: اتباع خطوات Ubuntu
```bash
# بعد تشغيل WSL Ubuntu
# اتبع خطوات التثبيت على Ubuntu المذكورة أعلاه
```

### الخطوة 4: الوصول من Windows
```
# فتح المتصفح في Windows والذهاب إلى:
http://localhost:8080
```

---

## 🚀 التشغيل التلقائي (Production)

<!-- إعداد التشغيل التلقائي للمشروع -->

### استخدام Systemd (Linux)

#### 1. إنشاء ملف الخدمة
```bash
sudo nano /etc/systemd/system/sentraos.service
```

#### 2. محتوى ملف الخدمة
```ini
[Unit]
Description=SentraOS Monitoring Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/sentraos
Environment="PATH=/var/www/sentraos/venv/bin"
ExecStart=/var/www/sentraos/venv/bin/python3 /var/www/sentraos/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. تفعيل وتشغيل الخدمة
```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمة للتشغيل التلقائي
sudo systemctl enable sentraos

# تشغيل الخدمة
sudo systemctl start sentraos

# التحقق من حالة الخدمة
sudo systemctl status sentraos
```

#### 4. أوامر إدارة الخدمة
```bash
# إيقاف الخدمة
sudo systemctl stop sentraos

# إعادة تشغيل الخدمة
sudo systemctl restart sentraos

# عرض السجلات
sudo journalctl -u sentraos -f
```

---

## 🌐 إعداد Nginx (Reverse Proxy)

<!-- إعداد Nginx كـ reverse proxy -->

### الخطوة 1: تثبيت Nginx
```bash
sudo apt install -y nginx
```

### الخطوة 2: إنشاء ملف التكوين
```bash
sudo nano /etc/nginx/sites-available/sentraos
```

### الخطوة 3: محتوى ملف التكوين
```nginx
server {
    listen 80;
    server_name your-domain.com;  # غيّر هذا باسم النطاق الخاص بك

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # زيادة حجم الطلبات المسموح به
    client_max_body_size 10M;
}
```

### الخطوة 4: تفعيل الموقع
```bash
# إنشاء رابط رمزي
sudo ln -s /etc/nginx/sites-available/sentraos /etc/nginx/sites-enabled/

# اختبار التكوين
sudo nginx -t

# إعادة تحميل Nginx
sudo systemctl reload nginx
```

---

## 🔒 إعداد SSL/HTTPS (Let's Encrypt)

<!-- إعداد شهادة SSL مجانية -->

### الخطوة 1: تثبيت Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### الخطوة 2: الحصول على الشهادة
```bash
# استبدل your-domain.com بنطاقك
sudo certbot --nginx -d your-domain.com
```

### الخطوة 3: التجديد التلقائي
```bash
# اختبار التجديد
sudo certbot renew --dry-run

# التجديد التلقائي مفعّل افتراضياً
```

---

## 🔥 إعداد Firewall

<!-- إعداد جدار الحماية -->

### استخدام UFW (Ubuntu/Debian)
```bash
# تثبيت UFW
sudo apt install -y ufw

# السماح بـ SSH (مهم!)
sudo ufw allow ssh

# السماح بـ HTTP
sudo ufw allow 80/tcp

# السماح بـ HTTPS
sudo ufw allow 443/tcp

# السماح بـ port المشروع (إذا كنت تستخدمه مباشرة)
sudo ufw allow 8080/tcp

# تفعيل الجدار
sudo ufw enable

# التحقق من الحالة
sudo ufw status
```

### استخدام firewalld (CentOS/RHEL)
```bash
# تفعيل firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# السماح بالخدمات
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8080/tcp

# إعادة التحميل
sudo firewall-cmd --reload
```

---

## 📊 إعداد Gunicorn (Production Server)

<!-- استخدام Gunicorn بدلاً من Flask development server -->

### الخطوة 1: تثبيت Gunicorn
```bash
# تفعيل البيئة الافتراضية
source venv/bin/activate

# تثبيت Gunicorn
pip install gunicorn
```

### الخطوة 2: اختبار Gunicorn
```bash
# تشغيل Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 dashboard.app:app
```

### الخطوة 3: تعديل ملف systemd
```bash
sudo nano /etc/systemd/system/sentraos.service
```

**المحتوى المحدث:**
```ini
[Unit]
Description=SentraOS Monitoring Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/sentraos
Environment="PATH=/var/www/sentraos/venv/bin"
ExecStart=/var/www/sentraos/venv/bin/gunicorn -w 4 -b 127.0.0.1:8080 dashboard.app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### الخطوة 4: إعادة تشغيل الخدمة
```bash
sudo systemctl daemon-reload
sudo systemctl restart sentraos
```

---

## 🧪 اختبار التثبيت

<!-- التحقق من نجاح التثبيت -->

### 1. اختبار قاعدة البيانات
```bash
python3 -c "from models import get_session; session = get_session(); print('✅ Database: OK')"
```

### 2. اختبار الاتصال بالخادم
```bash
curl http://localhost:8080
```

### 3. اختبار API
```bash
# اختبار endpoint المقاييس
curl http://localhost:8080/api/metrics/current

# اختبار endpoint التنبيهات
curl http://localhost:8080/api/alerts
```

### 4. اختبار nmap
```bash
nmap --version
python3 -c "import nmap; print('✅ Python-nmap: OK')"
```

---

## 🐛 حل المشاكل الشائعة

<!-- حلول للمشاكل المتكررة -->

### المشكلة 1: Python version خاطئة
```bash
# التحقق من إصدار Python
python3 --version

# إذا كان أقل من 3.11، قم بالترقية:
sudo apt install -y python3.11
```

### المشكلة 2: nmap غير موجود
```bash
# تثبيت nmap
sudo apt install -y nmap

# التحقق من التثبيت
nmap --version
```

### المشكلة 3: Permission denied عند الفحص
```bash
# تشغيل الفحص بصلاحيات root (غير موصى به)
sudo python3 main.py

# أو السماح لـ Python بصلاحيات فحص المنافذ
sudo setcap cap_net_raw,cap_net_admin=eip $(readlink -f $(which python3))
```

### المشكلة 4: Port مستخدم بالفعل
```bash
# معرفة ما يستخدم Port 8080
sudo netstat -tulpn | grep 8080

# إيقاف العملية
sudo kill -9 PID

# أو تغيير Port في ملف .env
```

### المشكلة 5: Database locked
```bash
# إيقاف كل العمليات
sudo systemctl stop sentraos

# حذف ملف القفل
rm -f sentra.db-journal

# إعادة التشغيل
sudo systemctl start sentraos
```

### المشكلة 6: Module not found
```bash
# التأكد من تفعيل البيئة الافتراضية
source venv/bin/activate

# إعادة تثبيت المكتبات
pip install -r requirements.txt
```

---

## 📝 الصيانة الدورية

<!-- مهام الصيانة الدورية -->

### النسخ الاحتياطي
```bash
# إنشاء نسخة احتياطية من قاعدة البيانات
cp sentra.db sentra.db.backup-$(date +%Y%m%d)

# نسخ احتياطي كامل
tar -czf sentraos-backup-$(date +%Y%m%d).tar.gz /var/www/sentraos
```

### تحديث المشروع
```bash
# إيقاف الخدمة
sudo systemctl stop sentraos

# تحديث الكود
git pull origin main

# تحديث المكتبات
source venv/bin/activate
pip install -r requirements.txt --upgrade

# إعادة التشغيل
sudo systemctl start sentraos
```

### تنظيف السجلات
```bash
# حذف السجلات القديمة
sudo journalctl --vacuum-time=7d

# تنظيف ملفات السجل
find /var/www/sentraos/logs -type f -mtime +30 -delete
```

---

## 📚 موارد إضافية

<!-- روابط ومصادر مفيدة -->

- **التوثيق الرسمي:** [README.md](README.md)
- **Flask Documentation:** https://flask.palletsprojects.com/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **Nmap Documentation:** https://nmap.org/book/man.html
- **Nginx Documentation:** https://nginx.org/en/docs/

---

## 💬 الدعم والمساعدة


---

## ✅ قائمة التحقق النهائية

<!-- التأكد من اكتمال كل شيء -->

- [ ] تم تثبيت Python 3.11+
- [ ] تم تثبيت nmap
- [ ] تم إنشاء البيئة الافتراضية
- [ ] تم تثبيت كل المكتبات من requirements.txt
- [ ] تم إنشاء وتعديل ملف .env
- [ ] تم تهيئة قاعدة البيانات
- [ ] يعمل المشروع على http://localhost:8080
- [ ] تم إنشاء حساب admin
- [ ] تم إعداد systemd service (للإنتاج)
- [ ] تم إعداد Nginx (للإنتاج)
- [ ] تم إعداد SSL (للإنتاج)
- [ ] تم إعداد Firewall

---

**آخر تحديث:** نوفمبر 2024  
**الإصدار:** 1.0.0  
**المطور:** [اسمك هنا]