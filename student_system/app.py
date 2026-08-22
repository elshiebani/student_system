import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hist_suluq_secret_key_2026'

# ضبط الحد الأقصى لحجم المرفقات (16 ميجابايت) لمنع تعليق السيرفر
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

# إعدادات البريد الإلكتروني
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_app_password')

INSTITUTE_EMAIL = 'admission@suluq.edu.ly'

mail = Mail(app)

@app.route('/')
@app.route('/admission')
def admission():
    return render_template('admission.html')

@app.route('/submit_admission', methods=['POST'])
def submit_admission():
    try:
        full_name = request.form.get('full_name')
        national_id = request.form.get('national_id')
        phone = request.form.get('phone')
        email = request.form.get('email', '')
        qualification = request.form.get('qualification')
        gpa = request.form.get('gpa')
        department = request.form.get('department')

        cert_file = request.files.get('certificate_file')
        photo_file = request.files.get('photo_file')

        # حفظ الملفات في المجلد المؤقت الآمن للسيرفر (Temp) لتفادي أخطاء الأذونات على Render
        temp_dir = tempfile.gettempdir()
        cert_path = None
        photo_path = None

        if cert_file and cert_file.filename != '':
            cert_filename = f"{national_id}_cert_{cert_file.filename}"
            cert_path = os.path.join(temp_dir, cert_filename)
            cert_file.save(cert_path)

        if photo_file and photo_file.filename != '':
            photo_filename = f"{national_id}_photo_{photo_file.filename}"
            photo_path = os.path.join(temp_dir, photo_filename)
            photo_file.save(photo_path)

        # محاولة إرسال البريد
        try:
            msg = Message(
                subject=f"طلب تسجيل جديد - الطالب: {full_name}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[INSTITUTE_EMAIL]
            )
            msg.body = f"""
            طلب تسجيل جديد عبر المنظومة الإلكترونية للمعهد العالي للعلوم والتقنية سلوق:

            - الاسم الكامل: {full_name}
            - الرقم الوطني: {national_id}
            - رقم الهاتف: {phone}
            - البريد الإلكتروني للطالب: {email}
            - المؤهل العلمي: {qualification}
            - المعدل: {gpa}%
            - القسم المطلوب: {department}
            """

            if cert_path and os.path.exists(cert_path):
                with open(cert_path, 'rb') as fp:
                    msg.attach(os.path.basename(cert_path), "application/octet-stream", fp.read())

            if photo_path and os.path.exists(photo_path):
                with open(photo_path, 'rb') as fp:
                    msg.attach(os.path.basename(photo_path), "application/octet-stream", fp.read())

            mail.send(msg)
        except Exception as mail_err:
            print(f"Mail Error: {mail_err}")

        # التوجيه لصفحة النجاح مباشرة
        return render_template('success.html', full_name=full_name, national_id=national_id, department=department)

    except Exception as e:
        print(f"Server Processing Error: {e}")
        # عرض الخطأ للوقوف على أسبابه بدلاً من الشاشة البيضاء
        return f"حدث خطأ في السيرفر أثناء رفع البيانات: {str(e)}", 500

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
        flash(f'شكراً لك {name}، تم إرسال استفسارك بنجاح.', 'success')
    except Exception as e:
        flash(f'شكراً لك {name}، تم استلام استفسارك بنجاح.', 'success')

    return redirect(url_for('admission'))

@app.route('/check_status', methods=['POST'])
def check_status():
    national_id = request.form.get('national_id')
    flash(f'الطلب الخاص بالرقم الوطني ({national_id}) قيد المراجعة والتدقيق حالياً.', 'info')
    return redirect(url_for('admission'))

if __name__ == '__main__':
    app.run(debug=True)
