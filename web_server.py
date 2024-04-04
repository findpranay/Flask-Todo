from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import bcrypt
from bson import ObjectId
from flask import abort



app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/login'
mongo = PyMongo(app)
@app.route('/')
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']
    return render_template("index.html")

@app.route('/', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})
    if login_user and bcrypt.checkpw(request.form['pass'].encode('utf-8'), login_user['password']):
        session['username'] = request.form['username']
        return redirect(url_for('dashboard'))
    return "Invalid credentials"


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            
            # Use insert_one to insert a single document
            users.insert_one({'name': request.form['username'], 'password': hashpass})
            
            return redirect(url_for('dashboard'))

    # Add a return statement for cases where the request method is not 'POST'
    return render_template("register.html") 
# Dashboard route (protected route - user must be logged in to access)
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        students = mongo.db.students.find({'username': session['username']})
        return render_template('dashboard.html', username=session['username'], students=students)
    
    return redirect(url_for('index'))

# CRUD operations (example routes)
@app.route('/create', methods=['POST'])
def create():
    if 'username' in session:
        students = mongo.db.students
        new_student = {
            'username': session['username'],
            'name': request.form['name'],
            'grade': request.form['grade'],
            'marks': int(request.form['marks'])
        }
        students.insert_one(new_student)
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('index'))



@app.route('/update_page/<student_id>', methods=['GET', 'POST'])
def update_page(student_id):
    if 'username' in session:
        students = mongo.db.students
        student = students.find_one({'_id': ObjectId(student_id), 'username': session['username']})

        if student is None:
            # If the student is not found, return a 404 Not Found response
            abort(404)

        if request.method == 'POST':
            students.update_one(
                {'_id': ObjectId(student_id), 'username': session['username']},
                {'$set': {
                    'name': request.form['update_name'],
                    'grade': request.form['update_grade'],
                    'marks': int(request.form['update_marks'])
                }}
            )
            return redirect(url_for('dashboard'))

        # If the request method is 'GET', render the update form
        return render_template('update.html', student=student)
    
    return redirect(url_for('index'))

@app.route('/delete_page/<student_id>')
def delete_page(student_id):
    if 'username' in session:
        students = mongo.db.students
        students.delete_one({'_id': ObjectId(student_id), 'username': session['username']})
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('index'))

    

# Logout route
# Update the logout route in your Flask app
@app.route('/logout')
def logout():
    # Clear session data (customize as per your session management)
    session.clear()
    return redirect(url_for('index'))  # Redirect to your login page


if __name__ == '__main__':
    app.secret_key = 'secretivekeyagain'
    app.run(debug=True)