from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database Configuration
# MySQL connection using PyMySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:cdac@localhost/aws_deployment'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Route for the home page (index)
@app.route('/')
def index():
    return render_template('index.html')

# Route for the About page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for the Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the user already exists
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            # Pass the user_exists flag as True if the user already exists
            return render_template('register.html', user_exists=True)

        # If user does not exist, create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('signin'))

    # Always pass user_exists to the template (default to False)
    return render_template('register.html', user_exists=False)


# Route for the Sign In page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # If login is successful, store the username in the session
            session['user'] = user.username
            return redirect(url_for('dashboard'))
        else:
            # If login fails, reload the signin page with an error message
            return render_template('signin.html', login_failed=True)

    return render_template('signin.html')

# Route for the Dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    else:
        return redirect(url_for('signin'))

# Route to log out the user
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
