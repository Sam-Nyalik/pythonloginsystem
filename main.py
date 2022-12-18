# Packages importation
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'secret_key'

# Database connection details
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Caroltosh-44717101216200019'
app.config['MYSQL_DB'] = 'pythonlogin'

# Initialize MySQL
mysql = MySQL(app)

# Login route
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output a message if there's an error
    msg = ''
    
    # Check if 'username' and 'password' POST requests exist[User submitted form]
    if request.method == 'POST' and 'userName' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['userName']
        password = request.form['password']
        
        # Check if the account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # fetch one record and return the result
        account = cursor.fetchone()
        
        # If account exists in our accounts table in our database
        if account:
            # Create session data, We can access this data in other routes
            session['loggedIn'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        
        else:
            # Account doesn't exist or username/password is incorrect
            msg = 'Incorrect username/password!'
            
    
    return render_template('index.html', msg=msg)


# Logout route
@app.route('/pythonlogin/logout')
def logout():
    # remove the session data
    session.pop('loggedIn', None)
    session.pop('id', None)
    session.pop('username', None)
    
    # redirect to the login page
    return redirect(url_for('login'))

# Register route
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output a message if something goes wrong
    msg = ''
    
    # Check user input
    if request.method == 'POST' and 'userName' in request.form and 'password' in request.form and 'emailAddress' in request.form:
        # Create variables for easy access
        username = request.form['userName']
        password = request.form['password']
        email = request.form['emailAddress']
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        # If account exists, show errors and validation checks
        if account:
            msg = "Account already exists!"
            
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid email address!"
        
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = "Username must contain only characters and numbers!"
            
        elif not username or not password or not email:
            msg = "Please fill out the form!"
            
        else:
            # Account doesn't exist and the form data is valid, now insert the new account into the database
            cursor.execute('INSERT INTO accounts(username, password, email) VALUES(%s,%s,%s)', (username, password, email,))
            mysql.connection.commit()
            
            msg = "You have successfully registered!"
            
    elif request.method == 'POST':
        # Form is empty
        msg = 'Please fill out the form!'
        
    # Show the registration form with message(if any)
    return render_template('register.html', msg=msg)
        
# Home route
@app.route('/pythonlogin/home')
def home():
    # Check if the user is loggedIn
    if 'loggedIn' in session:
        # User is loggedIn, show them the home page
        return render_template('home.html', username=session['username'])
    # User is not logged in, redirect them to the login page
    return redirect(url_for('login'))

# Profile route
@app.route('/pythonlogin/profile')
def profile():
    # Check if the user is loggedIn
    if 'loggedIn' in session:
        # We'll need all the account info of the user to display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE id = %s", (session['id'],))
        account = cursor.fetchone()
        
        # Show the profile page with the account information
        return render_template('profile.html', account=account)
    
    # redirect user to the log in page if he/she isn't loggedin yet
    return redirect(url_for('login'))