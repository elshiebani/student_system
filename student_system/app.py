import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hist_suluq_secret_key_2026'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# التأكد من وجود مجلد التحميلات
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
@app.route('/admission')
def admission():
    return render_template('admission.html')

@app.route('/submit_admission', methods=['POST'])
def submit_admission():
    full_name = request.form.get('full_name')
    national_id = request.form.get('national_id')
    phone = request.form.get('phone')
    department = request.form.get('department')
    
    # حفظ الملفات المرفوعة
    cert_file = request.files.get('certificate_file')
    photo_file = request.files.get('photo_file')
    
    if cert_file and cert_file.filename != '':
        cert_filename = f"{national_id}_cert_{cert_file.filename}"
        cert_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cert_filename))
        
    if photo_file and photo_file.filename != '':
        photo_filename = f"{national_id}_photo_{photo_file.filename}"
        photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    return render_template('success.html', full_name=full_name, national_id=national_id, department=department)

@app.route('/send_inquiry', methods=['POST'])
def send_inquiry():
    name = request.form.get('name')
    flash(f'شكراً لك {name}، تم إرسال استفسارك بنجاح إلى قسم القبول والتسجيل.', 'success')
    return redirect(url_for('admission'))

@app.route('/check_status', methods=['POST'])
def check_status():
    national_id = request.form.get('national_id')
    flash(f'الطلب الخاص بالرقم الوطني ({national_id}) قيد المراجعة والتدقيق حالياً.', 'info')
    return redirect(url_for('admission'))

if __name__ == '__main__':
    app.run(debug=True)