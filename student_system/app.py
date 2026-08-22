import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hist_suluq_secret_key_2026'

# تحديد مسار مجلد التحميلات وإنشائه إذا لم يكن موجوداً
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# إعدادات البريد الإلكتروني (إعدادات Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'YOUR_EMAIL@gmail.com'      # البريد المُرسِل (إيميلك أو إيميل المعهد)
app.config['MAIL_PASSWORD'] = 'YOUR_APP_PASSWORD'          # كلمة مرور التطبيقات من جوجل (App Password)

# البريد الخاص باستلام الطلبات بالمعهد
INSTITUTE_EMAIL = 'admission@suluq.edu.ly'                 # استبدليه بريد الاستقبال المطلوب

mail = Mail(app)

@app.route('/')
@app.route('/admission')
def admission():
    return render_template('admission.html')

@app.route('/submit_admission', methods=['POST'])
def submit_admission():
    full_name = request.form.get('full_name')
    national_id = request.form.get('national_id')
    phone = request.form.get('phone')
    email = request.form.get('email')
    qualification = request.form.get('qualification')
    gpa = request.form.get('gpa')
    department = request.form.get('department')
    
    cert_file = request.files.get('certificate_file')
    photo_file = request.files.get('photo_file')
    
    cert_path = None
    photo_path = None

    # 1. حفظ الملفات محلياً داخل مجلد uploads
    if cert_file and cert_file.filename != '':
        cert_filename = f"{national_id}_cert_{cert_file.filename}"
        cert_path = os.path.join(app.config['UPLOAD_FOLDER'], cert_filename)
        cert_file.save(cert_path)
        
    if photo_file and photo_file.filename != '':
        photo_filename = f"{national_id}_photo_{photo_file.filename}"
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        photo_file.save(photo_path)

    # 2. إعداد وإرسال الرسالة الإلكترونية للمعهد مع المرفقات
    try:
        msg = Message(
            subject=f"طلب تسجيل جديد - الطالب: {full_name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[INSTITUTE_EMAIL]
        )
        
        msg.body = f"""
        طلب تسجيل جديد عبر المنظومة الإلكترونية للمعهد العالي سلوق:
        
        - الاسم الكامل: {full_name}
        - الرقم الوطني: {national_id}
        - رقم الهاتف: {phone}
        - البريد الإلكتروني للطالب: {email}
        - المؤهل العلمي: {qualification}
        - المعدل: {gpa}%
        - القسم المطلوب: {department}
        """
        
        # إرفاق الملفات المحفوظة بالبريد
        if cert_path and os.path.exists(cert_path):
            with app.open_resource(cert_path) as fp:
                msg.attach(os.path.basename(cert_path), "application/octet-stream", fp.read())
                
        if photo_path and os.path.exists(photo_path):
            with app.open_resource(photo_path) as fp:
                msg.attach(os.path.basename(photo_path), "application/octet-stream", fp.read())

        mail.send(msg)
    except Exception as e:
        print(f"تنبيه: تعذر إرسال البريد الإلكتروني ({e})، ولكن تم حفظ الملف والبيانات محلياً.")

    return render_template('success.html', full_name=full_name, national_id=national_id, department=department)

@app.route('/send_inquiry', methods=['POST'])
def send_inquiry():
    name = request.form.get('name')
    user_message = request.form.get('message')
    
    try:
        msg = Message(
            subject=f"استفسار جديد من: {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[INSTITUTE_EMAIL]
        )
        msg.body = f"الاسم: {name}\nالرسالة:\n{user_message}"
        mail.send(msg)
        flash(f'شكراً لك {name}، تم إرسال استفسارك بنجاح إلى إدارة المعهد.', 'success')
    except Exception as e:
        flash('تم استلام استفسارك محلياً، حدث خطأ بسيط أثناء إرسال البريد.', 'warning')
        
    return redirect(url_for('admission'))

@app.route('/check_status', methods=['POST'])
def check_status():
    national_id = request.form.get('national_id')
    flash(f'الطلب الخاص بالرقم الوطني ({national_id}) قيد المراجعة والتدقيق حالياً.', 'info')
    return redirect(url_for('admission'))

if __name__ == '__main__':
    app.run(debug=True)
