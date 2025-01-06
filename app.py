from flask import Flask, render_template, request, redirect, url_for, session
import os
import json

app = Flask(__name__)

# Secret Key for Sessions
app.secret_key = 'your_secret_key_here'

# Admin credentials
ADMIN_CREDENTIALS = {
    "admin1": "password123",
    "admin2": "securepass",
}

# JSON File Paths
DATA_FILE = 'data.json'

# Helper function to load and save data
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "projects": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        languages = request.form['languages']
        age = request.form['age']

        # Save user to JSON file
        data = load_data()
        data['users'].append({
            "email": email,
            "username": username,
            "password": password,
            "languages": languages,
            "age": age,
        })
        save_data(data)

        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Authenticate user
        data = load_data()
        user = next((u for u in data['users'] if u['email'] == email and u['password'] == password), None)
        if user:
            session['user_email'] = user['email']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid email or password")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect('/login')
    
    data = load_data()
    user = next((u for u in data['users'] if u['email'] == session['user_email']), None)
    projects = [p for p in data['projects'] if p['email'] == session['user_email']]
    
    return render_template('dashboard.html', user=user, projects=projects)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_email' not in session:
        return redirect('/login')
    if request.method == 'POST':
        print("Form data received:", request.form)  # Log form data
        print("Files received:", request.files)    # Log uploaded files

        # Attempt to retrieve fields
        try:
            title = request.form['title']
            description = request.form['description']
            file = request.files['file']
            file_name = file.filename
            user_email = session['user_email']

            # Save the uploaded file
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            file.save(os.path.join(uploads_dir, file_name))

            # Save project to JSON file
            data = load_data()
            data['projects'].append({
                "title": title,
                "description": description,
                "file_name": file_name,
                "email": user_email
            })
            save_data(data)

            return redirect('/dashboard')
        except KeyError as e:
            print(f"KeyError: {e}")
            return "Bad Request: Missing form data", 400
    return render_template('upload.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate admin credentials
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', error="Invalid credentials")
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return redirect('/admin/dashboard')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        data = load_data()
        return render_template('admin.html', users=data['users'], projects=data['projects'])
    else:
        return redirect('/admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect('/')

if __name__ == '__main__':
    # Create the data.json file if it doesn't exist
    if not os.path.exists(DATA_FILE):
        save_data({"users": [], "projects": []})
    app.run(debug=True)
