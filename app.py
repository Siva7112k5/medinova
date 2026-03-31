from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'medinova-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_email = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    doctor = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== CREATE TABLES ====================
with app.app_context():
    db.create_all()
    # Create default admin if not exists
    admin = User.query.filter_by(email='admin@medinova.com').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@medinova.com',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

# ==================== CONTEXT PROCESSOR ====================
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}
# ==================== AUTH ROUTES ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            flash('Logged in successfully!', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


# ==================== MAIN ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/pricing')
def pricing():
    return render_template('price.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/blog-detail')
def blog_detail():
    return render_template('blog-detail.html')

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        department = request.form.get('department')
        doctor = request.form.get('doctor')
        name = request.form.get('name')
        email = request.form.get('email')
        date = request.form.get('date')
        time = request.form.get('time')
        
        if name and email and department and doctor and date and time:
            new_appointment = Appointment(
                patient_name=name,
                patient_email=email,
                department=department,
                doctor=doctor,
                date=date,
                time=time
            )
            if 'user_id' in session:
                new_appointment.user_id = session['user_id']
            db.session.add(new_appointment)
            db.session.commit()
            flash('Appointment booked successfully!', 'success')
        else:
            flash('Please fill all fields.', 'danger')
        return redirect(url_for('appointment'))
    return render_template('appointment.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if name and email and message:
            new_message = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            db.session.add(new_message)
            db.session.commit()
            flash('Your message has been sent successfully!', 'success')
        else:
            flash('Please fill all required fields.', 'danger')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    doctors_list = [
        {'name': 'Dr. Sarah Johnson', 'specialty': 'Cardiology Specialist', 'image': 'team-1.jpg', 'department': 'Cardiology'},
        {'name': 'Dr. Michael Chen', 'specialty': 'Neurology Specialist', 'image': 'team-2.jpg', 'department': 'Neurology'},
        {'name': 'Dr. Emily Davis', 'specialty': 'Pediatrics Specialist', 'image': 'team-3.jpg', 'department': 'Pediatrics'},
        {'name': 'Dr. James Wilson', 'specialty': 'Orthopedic Specialist', 'image': 'team-1.jpg', 'department': 'Orthopedic'},
        {'name': 'Dr. Maria Garcia', 'specialty': 'Dermatology Specialist', 'image': 'team-2.jpg', 'department': 'Dermatology'},
        {'name': 'Dr. Robert Brown', 'specialty': 'Psychiatry Specialist', 'image': 'team-3.jpg', 'department': 'Psychiatry'},
    ]
    
    search_results = doctors_list
    keyword = ''
    department = ''
    
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').lower()
        department = request.form.get('department', '')
        
        if department and department != 'Department':
            search_results = [d for d in doctors_list if d['department'] == department]
        if keyword:
            search_results = [d for d in search_results if keyword in d['name'].lower() or keyword in d['specialty'].lower()]
    
    return render_template('search.html', doctors=search_results, keyword=keyword, selected_dept=department)

# ==================== ADMIN ROUTES ====================
@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    total_users = User.query.count()
    total_appointments = Appointment.query.count()
    total_messages = ContactMessage.query.count()
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_appointments=total_appointments,
                         total_messages=total_messages,
                         recent_appointments=recent_appointments)

@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/delete/<int:user_id>')
def admin_delete_user(user_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    else:
        flash('Cannot delete admin user', 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/appointments')
def admin_appointments():
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return render_template('admin/appointments.html', appointments=appointments)

@app.route('/admin/appointment/delete/<int:appointment_id>')
def admin_delete_appointment(appointment_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted successfully', 'success')
    return redirect(url_for('admin_appointments'))

@app.route('/admin/messages')
def admin_messages():
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/message/delete/<int:message_id>')
def admin_delete_message(message_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully', 'success')
    return redirect(url_for('admin_messages'))

if __name__ == '__main__':
    app.run(debug=True)