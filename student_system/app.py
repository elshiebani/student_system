import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'suluq_secret_key_2026')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    national_id = db.Column(db.String(12), unique=True, nullable=False)
    parent_phone = db.Column(db.String(20), nullable=False)  # هاتف ولي الأمر
    department = db.Column(db.String(100), nullable=False)
    
    # صورة المؤهل العلمي (بدلاً من الصورة الشخصية)
    qualifier_filename = db.Column(db.String(200))
    qualifier_data = db.Column(db.LargeBinary)
    
    # الشهادة المرفقة
    cert_filename = db.Column(db.String(200))
    cert_data = db.Column(db.LargeBinary)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    full_name = request.form.get('full_name', '').strip()
    national_id = request.form.get('national_id', '').strip()
    parent_phone = request.form.get('parent_phone', '').strip()
    department = request.form.get('department', '').strip()
    
    # التحقق من الرقم الوطني (12 خانة ويبدأ بـ 1 أو 2)
    if not re.match(r'^[12]\d{11}$', national_id):
        flash('خطأ: الرقم الوطني يجب أن يتكون من 12 رقماً ويبدأ بالرقم 1 أو 2.', 'danger')
        return redirect(url_for('index'))
    
    qualifier_file = request.files.get('qualifier_image')
    cert_file = request.files.get('cert_file')
    
    qualifier_filename = qualifier_file.filename if qualifier_file else None
    qualifier_data = qualifier_file.read() if qualifier_file else None
    
    cert_filename = cert_file.filename if cert_file else None
    cert_data = cert_file.read() if cert_file else None
    
    try:
        new_student = Student(
            full_name=full_name,
            national_id=national_id,
            parent_phone=parent_phone,
            department=department,
            qualifier_filename=qualifier_filename,
            qualifier_data=qualifier_data,
            cert_filename=cert_filename,
            cert_data=cert_data
        )
        db.session.add(new_student)
        db.session.commit()
        flash('تم تسجيل بياناتك بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء حفظ البيانات، قد يكون الرقم الوطني مسجلاً مسبقاً.', 'danger')
        
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'noura' and password == '2241997':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('بيانات الدخول غير صحيحة', 'danger')
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    students = Student.query.all()
    return render_template('admin.html', students=students)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/file/qualifier/<int:student_id>')
def get_qualifier(student_id):
    student = Student.query.get_or_404(student_id)
    if student.qualifier_data:
        response = make_response(student.qualifier_data)
        response.headers['Content-Disposition'] = f'inline; filename={student.qualifier_filename}'
        return response
    return "الملف غير موجود", 404

@app.route('/file/cert/<int:student_id>')
def get_cert(student_id):
    student = Student.query.get_or_404(student_id)
    if student.cert_data:
        response = make_response(student.cert_data)
        response.headers['Content-Disposition'] = f'inline; filename={student.cert_filename}'
        return response
    return "الملف غير موجود", 404

if __name__ == '__main__':
    app.run(debug=True)
