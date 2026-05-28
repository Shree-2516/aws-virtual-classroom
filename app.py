import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database.db_connection import get_db_connection, load_env

# Load configurations from .env
load_env()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key-default-1234')

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB Max file upload limit
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'mp4', 'mkv', 'avi', 'webm'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has a valid extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =====================================================================
# MODULE 1: HOME PAGE ROUTE
# =====================================================================
@app.route('/')
def home():
    """Render home landing page"""
    return render_template('home.html')

# =====================================================================
# MODULE 2: REGISTRATION SYSTEM
# =====================================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new student or admin user"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    demo_allow_role_select = os.environ.get('DEMO_ALLOW_ROLE_SELECT', '1') == '1'
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student').strip()
        
        # Validations
        if not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'error')
            return render_template('register.html', demo_allow_role_select=demo_allow_role_select, username=username, email=email, role=role)
            
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html', demo_allow_role_select=demo_allow_role_select, username=username, email=email, role=role)
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html', demo_allow_role_select=demo_allow_role_select, username=username, email=email, role=role)
            
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again later.', 'error')
            return render_template('register.html', demo_allow_role_select=demo_allow_role_select, username=username, email=email, role=role)
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Username or Email already registered.', 'error')
                cursor.close()
                conn.close()
                return render_template('register.html', demo_allow_role_select=demo_allow_role_select, username=username, email=email, role=role)
                
            # Hash password
            password_hash = generate_password_hash(password)
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                (username, email, password_hash, role)
            )
            conn.commit()
            
            flash('Registration successful! Please login to continue.', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            if conn:
                conn.close()
                
    return render_template('register.html', demo_allow_role_select=demo_allow_role_select)

# =====================================================================
# MODULE 3: LOGIN SYSTEM
# =====================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate and log in an existing user"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()  # Can be username or email
        password = request.form.get('password')
        
        if not login_input or not password:
            flash('Please enter your credentials.', 'error')
            return render_template('login.html', login_input=login_input)
            
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again later.', 'error')
            return render_template('login.html', login_input=login_input)
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Retrieve user details by username or email
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (login_input, login_input))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                # Password verified, establish session
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                session['role'] = user['role']
                
                flash(f"Welcome back, {user['username']}! Logged in as {user['role'].capitalize()}.", 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Username/Email or Password.', 'error')
                cursor.close()
                conn.close()
                return render_template('login.html', login_input=login_input)
                
        except Exception as e:
            print(f"Error during login: {e}")
            flash('An error occurred during login. Please try again.', 'error')
            if conn:
                conn.close()
                
    return render_template('login.html')

# =====================================================================
# MODULE 4: DASHBOARD
# =====================================================================
@app.route('/dashboard')
def dashboard():
    """Display course materials (PDFs, Notes, Videos) categorized"""
    # Access control: Login required
    if 'user_id' not in session:
        flash('Please login to access your dashboard.', 'error')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    if not conn:
        flash('Failed to connect to the database. Dashboard resources could not be loaded.', 'error')
        return render_template('dashboard.html', courses=[], pdfs=[], notes=[], videos=[])
        
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Fetch available courses
        cursor.execute("SELECT * FROM courses ORDER BY course_name ASC")
        courses = cursor.fetchall()
        
        # 2. Fetch uploaded materials
        cursor.execute("""
            SELECT u.*, c.course_name 
            FROM uploads u 
            LEFT JOIN courses c ON u.course_id = c.id 
            ORDER BY u.created_at DESC
        """)
        uploads = cursor.fetchall()
        
        # Categorize uploaded materials
        pdfs = [u for u in uploads if u['file_type'] == 'pdf']
        notes = [u for u in uploads if u['file_type'] == 'note']
        videos = [u for u in uploads if u['file_type'] == 'video']
        
        cursor.close()
        conn.close()
        return render_template('dashboard.html', courses=courses, pdfs=pdfs, notes=notes, videos=videos)
        
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        flash('An error occurred loading dashboard materials.', 'error')
        if conn:
            conn.close()
        return render_template('dashboard.html', courses=[], pdfs=[], notes=[], videos=[])

# =====================================================================
# MODULE 5: ADMIN UPLOAD SYSTEM
# =====================================================================
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Admin-only page to upload local PDFs, Notes, and Videos"""
    # Access control: Login required
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
        
    # Access control: Admin only
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges are required to upload files.', 'error')
        return redirect(url_for('dashboard'))
        
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed. Unable to display upload page.', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, course_name FROM courses ORDER BY course_name ASC")
        courses = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching courses for upload list: {e}")
        courses = []
    finally:
        if conn:
            cursor.close()
            conn.close()
            
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        file_type = request.form.get('file_type', '').strip()  # 'pdf', 'note', 'video'
        course_id = request.form.get('course_id')
        
        # Validate inputs
        if not title or not file_type:
            flash('Title and File Type are required.', 'error')
            return render_template('upload.html', courses=courses, title=title, file_type=file_type)
            
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return render_template('upload.html', courses=courses, title=title, file_type=file_type)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return render_template('upload.html', courses=courses, title=title, file_type=file_type)
            
        if not allowed_file(file.filename):
            flash('Allowed file formats: PDF, TXT, DOC, DOCX, PNG, JPG, MP4, WEBM, MKV, AVI.', 'error')
            return render_template('upload.html', courses=courses, title=title, file_type=file_type)
            
        try:
            # Generate secure file name with timestamp prefix to prevent name collisions
            timestamp = str(int(time.time()))
            original_filename = secure_filename(file.filename)
            filename = f"{timestamp}_{original_filename}"
            
            # Save file locally
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Store in database
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            db_course_id = int(course_id) if course_id and course_id.isdigit() else None
            file_url = f"/uploads/{filename}"
            
            cursor.execute(
                """INSERT INTO uploads (title, file_type, file_url, uploaded_by, course_id) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (title, file_type, file_url, session['username'], db_course_id)
            )
            conn.commit()
            
            flash(f"Material '{title}' uploaded successfully!", 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"Error during file upload process: {e}")
            flash('An error occurred during the upload process. Please try again.', 'error')
            if conn:
                conn.close()
                
    return render_template('upload.html', courses=courses)

# =====================================================================
# SERVE UPLOADED FILES ROUTE
# =====================================================================
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve files uploaded locally in a secure manner"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# =====================================================================
# MODULE 6: LOGOUT ROUTE
# =====================================================================
@app.route('/logout')
def logout():
    """Destroy session data and redirect user to home"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Run server locally on port 5000 in debug mode
    app.run(host='127.0.0.1', port=5000, debug=True)
