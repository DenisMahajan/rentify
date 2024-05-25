from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import os
from flask_mail import Mail, Message
import random
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = os.environ.get('localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'your_secret_key'

mysql = MySQL(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# File Upload Configuration
UPLOAD_FOLDER = 'static/assets/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to ensure user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Display the homepage with properties and user information."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM properties")
    properties = cur.fetchall()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    
    user_dict = {user['id']: user['name'] for user in users}
    for property in properties:
        property['user_name'] = user_dict.get(property['user_id'], 'Unknown')
    return render_template('index.html', properties=properties)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login and signup."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        action = request.form.get('action')

        cur = mysql.connection.cursor()

        if action == '/signin':
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                return render_template('login.html')

        elif action == '/signup':
            name = request.form['name']
            mobile = request.form['mobile']
            password = generate_password_hash(password, method='pbkdf2:sha256')
            cur.execute("INSERT INTO users (name, email, mobile, password) VALUES (%s, %s, %s, %s)",
                        (name, email, mobile, password))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/post_property', methods=['GET', 'POST'])
@login_required
def post_property():
    """Handle posting a new property."""
    if request.method == 'POST':
        app_name = request.form['app_name']
        bhk_type = request.form['bhk_type']
        floor = request.form['floor']
        total_floor = request.form['total_floor']
        area = request.form['area']
        expected_rent = request.form['expected_rent']
        preferred_tenants = request.form['preferred_tenants']
        add = request.form['add']
        city = request.form['city']
        description = request.form['description']

        #   Handle image upload
        if 'property_image' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['property_image']
        if file.filename == '':
            filename = None
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Allowed image types are - png, jpg, jpeg, gif', 'danger')
            return redirect(request.url)

        cur = mysql.connection.cursor()
        query = """
            INSERT INTO properties (user_id, app_name, bhk_type, floor, total_floor, area, expected_rent, preferred_tenants, image_filename, `add`, city, description) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (session['user_id'], app_name, bhk_type, floor, total_floor, area, expected_rent, preferred_tenants, filename, add, city, description)
        cur.execute(query, values)
        mysql.connection.commit()
        cur.close()
        return redirect('/')

    return render_template('post_property.html')

@app.route('/properties')
def properties():
    """Display the list of properties."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM properties")
    properties = cur.fetchall()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    
    user_dict = {user['id']: user['name'] for user in users}
    for property in properties:
        property['user_name'] = user_dict.get(property['user_id'], 'Unknown')
    
    return render_template('properties.html', properties=properties)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Display and update user profile."""
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("USE rentify_db")
        cur.execute("SELECT * FROM users WHERE id = %s",(user_id,))
        user = cur.fetchall()
        cur.close()
        return render_template('profile.html', user = user)

@app.route('/send_otp', methods=['POST'])
def send_otp():
    """Send OTP to user's email."""
    user_email = request.form['email']
    property_id = request.form['property_id']
    otp = random.randint(100000, 999999)
    session['otp'] = otp
    session['user_email'] = user_email
    session['property_id'] = property_id

    msg = Message('Your OTP Code', recipients=[user_email])
    msg.body = f'Your OTP code is {otp}'
    mail.send(msg)

    flash('OTP sent to your email.', 'success')
    return render_template('verify_otp.html')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    """Verify OTP and send property owner details."""
    entered_otp = request.form['otp']
    if int(entered_otp) == session.get('otp'):
        user_email = session.get('user_email')
        property_id = session.get('property_id')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM properties WHERE id = %s", (property_id,))
        property = cur.fetchone()
        cur.execute("SELECT * FROM users WHERE id = %s", (property['user_id'],))
        owner_details = cur.fetchone()
        cur.close()

        msg = Message('Owner Details', recipients=[user_email])
        msg.body = f"Hello,\n\nHere are the details of the property owner:\n\nOwner Name: {owner_details['name']}\nPhone: {owner_details['mobile']}\nEmail: {owner_details['email']}\n\n---\n\nThis message and any attachments are confidential and may be privileged or otherwise protected from disclosure. If you are not the intended recipient, please delete this message and any attachment."
        mail.send(msg)

        flash('Owner details sent to your email address.', 'success')
        return redirect(url_for('properties'))
    else:
        flash('Invalid OTP. Please try again.', 'danger')
        return render_template('verify_otp.html')

@app.route('/logout')
def logout():
    """Logout the user."""
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
