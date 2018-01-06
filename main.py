from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashing import hash_pwd, check_hash_pwd 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:sleepy@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'yfd9uhlskdjkfymcjz&vzAIP'

# Define the Blog class - (The Model portion of the app)
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)                                # The blog id
    title = db.Column(db.String(120))                                           # The blog title
    blog_body = db.Column(db.String(2500))                                      # The blog body
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))                  # Create the relationship with the blogger
    post_date = db.Column(db.DateTime)                                          # The date the blogger creates a post

    # The Blog class constructor, perform the following upon initialization
    def __init__(self, title, blog_body, owner, post_date=None):
        self.title = title
        self.blog_body = blog_body
        self.owner_id = owner
        self.post_date = post_date
        if post_date is None:
            post_date = datetime.utcnow()        

# Define the User class. - (Also the Model portion of the app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)                                # The blogger id
    username = db.Column(db.String(120), unique=True)                           # The blogger username
    hashed_password = db.Column(db.String(120))                                 # The blogger password
    blogs = db.relationship('Blog', backref='owner')                            # The blog posts related to the blogger

    # The User constructor, perform upon initialization
    def __init__(self, username, password):
        self.username = username
        self.hashed_password = hash_pwd(password)                                      # Hash the password to store in the database

# The following would be the controller portion of the application
# Before request, set the allowed routes
@app.before_request
def blog_home():
    allowed_routes = ['/','index','login','signup','blog','logout']
    # Check to see if the user is logged in. If not redirect to the login page
    current_user = session.get('username')                                     # Get the username from the session 
    # Handle whenever a route isn't in the allowed routes
    if request.endpoint not in allowed_routes and request.endpoint != 'newpost':   
        return redirect('/')                                                   # Redirect to the home page
                                                                                    
# Set the login route
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']                                     # Get the username and password from
        password = request.form['password']                                     # the login form

        # Handle if the username or password is blank
        if username == "" or password == "":
            if password == "" and username == "":
                flash('Username or password cannot be empty','error')
            elif username == "":
                flash('Username cannot be empty.','error')
            elif username != "" and password != "":
                flash('Username cannot be empty.','error')
            else:
                flash('User password cannot be empty.','error')
            return redirect('/login')
        else:
            # Once the username and password are filled out validate the user
            # in the database.
            user = User.query.filter_by(username=username).first()              # Get the username from the database
            # If the username is valied and the password match what's in the database
            if user and check_hash_pwd(password,user.hashed_password):
                session['username'] = username                                  # Add the user to the session
                # Optional flash message welcoming user
                #flash('Welcome ' +  username)
                
                return redirect('/newpost')                                     # Redirect to the new post page upon login
            else:
                # If the user isn't found in the database
                if user == "" or user == None:
                    flash('Username does not exist','error')
                elif user and not check_hash_pwd(password,user.hashed_password):
                    flash('Password is incorrect.','error')
                else:
                    flash('User password incorrect, or user does not exist','error')
                    return redirect('/login')

        # Redirect if login is successful
        return redirect('/newpost')
    else:
        # If anything else goes wrong redirect to the login page
        return render_template('login.html')

# Set the blog route
@app.route('/blog', methods=['POST','GET'])
def blog():
    page=1
    per_page=5
    if request.method == 'GET':
        id = request.args.get("id")                                             # Get the id parameter
        blog_user = request.args.get("user")                                    # Get the blogger username

        # Process if there is a blog id returned (view a single post)
        if id:
            posts = []                                                          # If there is an id, there should not be multiple posts
            blog_post = Blog.query.filter_by(id=id).first()                     # Query by single post 
            blog_user_id = blog_post.owner_id
            blogger = User.query.filter_by(id=blog_user_id).first()             # Get the blogger info
            blog_user = blogger.username                                        # and render the single blog entry
            return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts,written_by=blog_user)
        elif blog_user:
            # Handle whenever the username is entered (view all posts by a single blogger)
            blog_post = []
            user_id = User.query.filter_by(username=blog_user).first()          # Get the blogger id          
            post_blogger = User.query.filter_by(id=user_id.id).first()          # Get the info by blogger id
            posts = post_blogger.blogs                                          # Get all of the blogger's posts
            # Display all of the posts for the individual blogger
            return render_template('singleUser.html',title="Blogz", blog_post=blog_post, posts=posts,written_by=post_blogger.username)
        else:
            # Display all blogs    
            blog_post=[]
            blog_post = Blog.query.filter_by(id=id).all()                       # Query by single post, this will be empty 
            posts = User.query.all()                                            # Get all blogger info. This also includes
                                                                                # all posts
            # Display all posts. By querying by bloggers, the blogger info is also included
            return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)
    else:

        # This will display all posts as a default
        blog_post = Blog.query.filter_by(id=id).all()                           # Query by single post, this will be empty 
        posts = User.query.all()                                                # Get all blogger info. This also includes
        
    return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)

# Set the new post route
@app.route('/newpost', methods=['GET','POST'])
def newpost():

    current_user = session.get('username')                                      # Get the username from the session 

    # If the user isn't logged in redirect to the login page else render the new post page
    if request.method == 'GET':
        if not current_user:
            return redirect('/login')
        else:
            return render_template('newpost.html')
    else:

        # Handle a new blog post entry
        if request.method == 'POST':
            user = session.get('username')                                      # Get the post info from the form
            title = request.form['blog_title']
            title = title.strip()
            blog_body = request.form['blog_body']
            blog_body = blog_body.strip()
            post_date = datetime.now()

        # If either field is empty send a message to the user        
            if title == "" or blog_body == "" or len(title) < 1 or len(blog_body) < 1:
                if title == "" and blog_body == "":
                    flash('The title is empty, please enter a title.','new_post_error')
                    flash('The blog message is empty, please enter a message.','new_post_error')
                    return render_template('newpost.html',blog_title=title,blog_body=blog_body)
                if title == "":
                    flash('The title is empty, please enter a title.','new_post_error')
                    return render_template('newpost.html',blog_title=title,blog_body=blog_body)
            if blog_body == "":
                flash('The blog message is empty, please enter a message.','new_post_error')
                return render_template('newpost.html',blog_title=title,blog_body=blog_body)
            else:
                # Submit users entry into the database and display the new blog entry
                blog_owner = User.query.filter_by(username=user).first()       # Query to get the user id 
                
                owner_id = blog_owner.id

                new_blog_entry = Blog(title, blog_body, owner_id, post_date)
                db.session.add(new_blog_entry)
                db.session.commit()
                blog_id = str(new_blog_entry.id)

            return redirect("/blog?id=" + blog_id)

        else:
            # If anything else goes wrong go to the new post page
            return redirect('/newpost')

# User signup path will validate the fields in the form and
# direct the user to the welcome confirmation message if
# all fields submitted are valid
@app.route("/signup", methods=['GET','POST'] )
def signup():

    if request.method == 'POST':
        user_name = request.form['username']                                    # Get the info from the form
        password = request.form['password']
        verify_password = request.form['verify_password']

        # If all fields are empty
        if (user_name.strip() == "" and password.strip() == "" and verify_password.strip() == ""):
            error = "The username cannot be empty"
            error_type = "ALL"
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,error=error,error_type=error_type)       
         # Validate the username
        if (user_name.strip() == "") or (not user_name) :
            error = "Username cannnot be empty"
            error_type = "USER"

            # Clear password fields for security reasons
            password = ""
            verify_password = ""

            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password, error=error,error_type=error_type)
        elif " " in user_name.strip():
            user_name=""
            # Clear password fields for security reasons
            password = ""
            verify_password = ""
            error = "Username cannnot contain spaces"
            error_type = "USER"
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,error=error,error_type=error_type)
        else:
            if (len(user_name.strip()) < 3) or (len(user_name.strip()) > 20):
                error = user_name + " is an invalid username, please enter a valid username" 
                user_name=""
                error_type = "USER"
                # Clear password fields for security reasons
                password = ""
                verify_password = ""
                return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,error=error,error_type=error_type)

        # Validae the password
        if (password.strip() == "" or  verify_password.strip() == ""):
            error = "Passwords and confirmation password cannot be empty"
            error_type = "PASSWORD"
            password = ""
            verify_password = ""
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,error=error,error_type=error_type)
        elif (password.strip() != verify_password.strip()):
            error = "Passwords don't match"
            error_type = "PASSWORD"
            password = ""
            verify_password = ""
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,error=error,error_type=error_type)
        elif (len(password.strip()) < 3) or (len(password.strip()) > 20):
            error = "The password is invalid"
            error_type = "PASSWORD"
            password = ""
            verify_password = ""
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,error=error,error_type=error_type)
        elif (len(verify_password.strip()) < 3) or (len(verify_password.strip()) > 20):
            error = "The password is invalid"
            error_type = "PASSWORD"
            password = ""
            verify_password = ""
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,error=error,error_type=error_type)
        else:
            if (" " in password.strip() or " " in verify_password.strip()):
                error = "Passwords cannot contain spaces"
                error_type = "PASSWORD"
                password = ""
                verify_password = ""
                return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,error=error,error_type=error_type)

        # Once the username and password are validated check to make sure username doesn't already exist in the 
        # database and allert the user if the password already exsits
        user = User.query.filter_by(username=user_name).first()

        # Create new user once the username and password are validated and the 
        # user doesn't exist in the database and display the new post form
        if User == "" or user == None:
            session['username'] = user_name
            new_user = User(user_name, password)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/newpost')
        else:
            # Handle the case if the user already exists in the database
            password = ""
            verify_password = ""
            flash('The user already exists in the database. Please select a different name.','error')            
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password)
            
    else:
        # Default return to the signup page
        return render_template('signup.html')

# Set the logout path
@app.route('/logout', methods=['GET','POST'])
def logout():
    logged_in_user = session.get('username')
    if logged_in_user:
        del session['username']
#   return redirect('/index')
    return redirect('/index')

# Set the home page route. In this application it's the blog page
@app.route('/',methods=['GET','POST'])
def index():
    bloggers = User.query.all()                                                 # Query all bloggers
    return render_template('index.html',title="Blogz",bloggers=bloggers)


# If app is called from main run
if __name__ == '__main__':
    app.run()