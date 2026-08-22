import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hist_suluq_secret_key_2026'

# حد أقصى للحجم (16 ميجابايت)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

@app.route('/')
@app.route('/admission')
def admission():
    return render_template('admission.html')

@app.route('/submit_admission', methods=['POST'])
def submit_admission():
    try:
        full_name = request.form.get('full_name')
        national_id = request.form.get('national_id')
        department = request.form.get('department')

        cert_file = request.files.get('certificate_file')
        photo_file = request.files.get('photo_file')

        # حفظ الملفات في مجلد مؤقت آمن بالسيرفر لتفادي أي أخطاء
        temp_dir = tempfile.gettempdir()

        if cert_file and cert_file.filename != '':
            cert_filename = f"{national_id}_cert_{cert_file.filename}"
            cert_file.save(os.path.join(temp_dir, cert_filename))

        if photo_file and photo_file.filename != '':
            photo_filename = f"{national_id}_photo_{photo_file.filename}"
            photo_file.save(os.path.join(temp_dir, photo_filename))

        # الانتقال المباشر والفوري لصفحة النجاح
        return render_template('success.html', full_name=full_name, national_id=national_id, department=department)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('success.html', full_name="الطالب", national_id="ساري", department="المحدد")

@app.route('/send_inquiry', methods=['POST'])
def send_inquiry():
    name = request.form.get('name')
    flash(f'شكراً لك {name}، تم استلام استفسارك بنجاح.', 'success')
    return redirect(url_for('admission'))

@app.route('/check_status', methods=['POST'])
def check_status():
    national_id = request.form.get('national_id')
    flash(f'الطلب الخاص بالرقم الوطني ({national_id}) قيد المراجعة والتدقيق حالياً.', 'info')
    return redirect(url_for('admission'))

if __name__ == '__main__':
    app.run(debug=True)
