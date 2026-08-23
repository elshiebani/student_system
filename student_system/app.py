from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Student

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# هنا باقي إعدادات قاعدة البيانات الخاصة بكِ...

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

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        students = Student.query.all()
        total_students = len(students)
        it_students = sum(1 for s in students if s.department and ('تقنية' in s.department or 'IT' in s.department))
        energy_students = sum(1 for s in students if s.department and 'الطاقات' in s.department)
    except Exception as e:
        students = []
        total_students = 0
        it_students = 0
        energy_students = 0
        flash('حدث خطأ أثناء تحميل البيانات من قاعدة البيانات.', 'danger')

    return render_template('admin.html', 
                           students=students, 
                           total_students=total_students,
                           it_students=it_students,
                           energy_students=energy_students)

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        flash('تم حذف الطالب بنجاح.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء محاولة الحذف.', 'danger')
        
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
