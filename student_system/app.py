import os
import sqlite3
import io
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hist_suluq_secret_key_2026'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# تحديد مسار دائم لقاعدة البيانات لتفادي فقدان البيانات عند إعادة التشغيل
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'students.db')

ADMIN_USERNAME = "noura"
ADMIN_PASSWORD = "2241997"

def get_db():
    conn = sqlite3.connect(DATABASE, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                national_id TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                qualification TEXT,
                gpa TEXT,
                department TEXT,
                cert_filename TEXT,
                cert_data BLOB,
                cert_mimetype TEXT,
                photo_filename TEXT,
                photo_data BLOB,
                photo_mimetype TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

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

        cert_filename = cert_file.filename if cert_file else None
        cert_data = cert_file.read() if cert_file else None
        cert_mimetype = cert_file.content_type if cert_file else None

        photo_filename = photo_file.filename if photo_file else None
        photo_data = photo_file.read() if photo_file else None
        photo_mimetype = photo_file.content_type if photo_file else None

        with get_db() as conn:
            conn.execute('''
                INSERT INTO students 
                (full_name, national_id, phone, email, qualification, gpa, department, 
                 cert_filename, cert_data, cert_mimetype, 
                 photo_filename, photo_data, photo_mimetype)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (full_name, national_id, phone, email, qualification, gpa, department,
                  cert_filename, cert_data, cert_mimetype,
                  photo_filename, photo_data, photo_mimetype))
            conn.commit()

        return render_template('success.html', full_name=full_name, national_id=national_id, department=department)

    except Exception as e:
        print(f"Error saving student: {e}")
        return f"حدث خطأ أثناء حفظ البيانات: {str(e)}", 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    with get_db() as conn:
        students = conn.execute('SELECT id, full_name, national_id, phone, email, qualification, gpa, department, cert_filename, photo_filename, created_at FROM students ORDER BY id DESC').fetchall()
    
    return render_template('admin.html', students=students)

@app.route('/admin/file/<int:student_id>/<string:file_type>')
def get_file(student_id, file_type):
    if not session.get('admin_logged_in'):
        return "غير مصرح", 403

    with get_db() as conn:
        if file_type == 'cert':
            row = conn.execute('SELECT cert_filename, cert_data, cert_mimetype FROM students WHERE id = ?', (student_id,)).fetchone()
        else:
            row = conn.execute('SELECT photo_filename, photo_data, photo_mimetype FROM students WHERE id = ?', (student_id,)).fetchone()

    if not row or not row[1]:
        return "الملف غير موجود", 404

    filename, data, mimetype = row[0], row[1], row[2]

    return send_file(
        io.BytesIO(data),
        mimetype=mimetype or 'application/octet-stream',
        as_attachment=False,
        download_name=filename or f"{file_type}_{student_id}"
    )

@app.route('/admin/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    with get_db() as conn:
        conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
    flash('تم حذف سجل الطالب بنجاح', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/send_inquiry', methods=['POST'])
def send_inquiry():
    name = request.form.get('name')
    flash(f'شكراً لك {name}، تم استلام استفسارك بنجاح.', 'success')
    return redirect(url_for('admission'))

@app.route('/check_status', methods=['POST'])
def check_status():
    national_id = request.form.get('national_id')
    with get_db() as conn:
        student = conn.execute('SELECT full_name, department FROM students WHERE national_id = ?', (national_id,)).fetchone()
    if student:
        flash(f'مرحباً {student["full_name"]}، طلبك مسجل بنجاح في قسم ({student["department"]}) وهو قيد المراجعة والتدقيق حالياً.', 'success')
    else:
        flash(f'الرقم الوطني ({national_id}) غير مسجل في المنظومة حتى الآن.', 'warning')
    return redirect(url_for('admission'))

if __name__ == '__main__':
    app.run(debug=True)
