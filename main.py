from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#from sqlalchemy import Column, Integer, String, Boolean
#from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['DEBUG'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:sleepy@localhost:8889/blogz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:sleepy@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'yfd9uhlskdjkfymcjz&vzAIP'

# Define the Blog calss - (The Model portion of the app)
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_body = db.Column(db.String(2500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_date = db.Column(db.DateTime)
#   blogs = db.relationship('Blog', backref='owner_id')

    # The Blog class constructor, perform the following upon initialization
    def __init__(self, title, blog_body, owner, post_date=None):
        self.title = title
        self.blog_body = blog_body
        self.post_date = post_date
        self.owner = owner
        if post_date is None:
            post_date = datetime.utcnow()        

# Define the User class. - (Also the Model portion of the app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    # The User constructor, perform upon initialization
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Before request, set the allowed routes
@app.before_request
def blog_home():
#   allowed_routes = ['blog','newpost']
    allowed_routes = ['login','signup']
    if request.endpoint not in allowed_routes:
#       return redirect('/blog')
        return redirect('/login')

# Set the login route
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print('Username', username)
        print('Password', password)
        if username == "" or password == "":
            if password == "" and username == "":
                flash('Username and password cannot be empty','error')
            elif username == "":
                flash('Username cannot be empty.','error')
            else:
                flash('User password cannot be empty.','error')
            return redirect('/login')
        else:
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                # Todo - 'remember' that the user has logged in
                session['username'] = username
                flash('Logged in')
                #print(session)
    #           return redirect('/')
#               return redirect('/newpost')
                return render_template('newpost.html')
            else:
                # Todo = explain why the login failed
                # pass
                # flash('User password incorrect, or user does not exist','error')
                #return '<h1>Error!</h1>'

                if user == "":
                    flash('Username does not exist','error')
                elif user and user.password != password:
                    flash('Password is incorrect.','error')
                else:
                    flash('User password incorrect, or user does not exist','error')

    return render_template('login.html')
    
# Set the blog route
@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.method == 'GET':
        id = request.args.get("id")       ()                  # Get the id parameter
        blog_post = Blog.query.filter_by(id=id).all()       # Query by single post 
        #posts = Blog.query.all()                           # Query all posts when form is rendered
#       posts = Blog.query.order_by(Blog.id.desc()).limit(3).all()    # Query all posts when form is rendered
#       posts = Blog.query.order_by(Blog.id.desc()).all()    # Query all posts when form is rendered
        posts = Blog.query.order_by(Blog.post_date.desc()).all()    # Query all posts when form is rendered

        # Render the template and pass the parameters
        return render_template('blog.html',title="Build a Blog", blog_post=blog_post, posts=posts)

# Set the new post route
@app.route('/newpost', methods=['POST','GET'])
def newpost():

    # If the user enters values and attempts to submit validate the fields
    """
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        print(owner, owner.id)  
        return redirect("/")
    """

    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
#       username = session['username']
        title = request.form['blog_title']
        title = title.strip()
        blog_body = request.form['blog_body']
        blog_body = blog_body.strip()
        post_date = datetime.now()
        # TODO Add owner to link the owner to a post
        

        # If either field is empty send a message to the user        
        if title == "" or blog_body == "" or len(title) < 1 or len(blog_body) < 1:
            if title == "" and blog_body == "":
                flash('The title is empty, please enter a title.','error')
                flash('The blog message is empty, please enter a message.','error')
                return render_template('newpost.html',blog_title=title,blog_body=blog_body)
            if title == "":
                flash('The title is empty, please enter a title.','error')
                return render_template('newpost.html',blog_title=title,blog_body=blog_body)
        if blog_body == "":
                flash('The blog message is empty, please enter a message.','error')
                return render_template('newpost.html',blog_title=title,blog_body=blog_body)
        else:
            # Submit users entry into the database
            new_blog_entry = Blog(title, blog_body, owner.id, post_date)
            db.session.add(new_blog_entry)
            db.session.commit()
            blog_id = str(new_blog_entry.id)
            return redirect("/blog?id=" + blog_id)
    else:
        # If the method isn't post render the form
        return render_template('newpost.html')

# User signup path will validate the fields in the form and
# direct the user to the welcome confirmation message if
# all fields submitted are valid
#@app.route('/signup', methods=['GET','POST'])
@app.route("/signup", methods=['GET','POST'] )
def signup():
    user_name = request.form['username']
    password = request.form['password']
    verify_password = request.form['verify_password']
 #   email = request.form['email']
 #   email_esc = cgi.escape(email, quote=True)
    if request.method == 'GET':
        return redirect('/signup')

    if request.method == 'POST':
        # If all fields are empty
        if (user_name.strip() == "" and password.strip() == "" and verify_password.strip() == ""):
            error = "The username cannot be empty"
            error_type = "ALL"
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)       

        # Validate the username
        if (user_name.strip() == "") or (not user_name) :
            error = "Username cannnot be empty"
            error_type = "USER"

            # Clear password fields for security reasons
            password = ""
            verify_password = ""

            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
        elif " " in user_name.strip():
            user_name=""
            # Clear password fields for security reasons
            password = ""
            verify_password = ""
            error = "Username cannnot contain spaces"
            error_type = "USER"
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
        else:
            if (len(user_name.strip()) < 3) or (len(user_name.strip()) > 20):
                error = user_name + " is an invalid username, please enter a valid username" 
                user_name=""
                error_type = "USER"
                # Clear password fields for security reasons
                password = ""
                verify_password = ""
                return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)

        # Validae the password
        if (password.strip() == "" or  verify_password.strip() == ""):
            error = "Passwords and confirmation password cannot be empty"
            error_type = "PASSWORD"
            password = ""
            verify_password = ""
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
        elif (password.strip() != verify_password.strip()):
            error = "Passwords don't match"
            error_type = "PASSWORD"
            password = ""
            verify_password = ""
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
        elif (len(password.strip()) < 3) or (len(password.strip()) > 20):
            error = "The password is invalid"
            error_type = "PASSWORD"
            password = ""
            verify_password = ""
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
        elif (len(verify_password.strip()) < 3) or (len(verify_password.strip()) > 20):
            error = "The password is invalid"
            error_type = "PASSWORD"
            password = ""
            verify_password = ""
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
        else:
            if (" " in password.strip() or " " in verify_password.strip()):
                error = "Passwords cannot contain spaces"
                error_type = "PASSWORD"
                password = ""
                verify_password = ""
                return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
            
        # Validate email address
    #  if (email_esc.strip() == ""):
    #      error = ""
    #      error_type = ""
    #  else:
    #      if (email_esc.find('@') < 0): 
    #          error = "The email address is invalid."
    #          error_type = "EMAIL"
    #          email = ""
    #          password = ""
    #          verify_password = ""
    #          return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
    #      if (email_esc.find('.') < 0): 
    #          error = "The email address is invalid."
    #          error_type = "EMAIL"
    #          email = ""
    #          password = ""
    #          verify_password = ""
    #          return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
    #      elif " " in email_esc.strip():
    #          error = "Email cannot contain spaces."
    #          error_type = "EMAIL"
    #          email = ""
    #          password = ""
    #          verify_password = ""
    #          return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)
    #      else:
    #          if (len(email.strip()) < 3) or (len(email.strip()) > 20) and (email != ""):
    #              error = "The email address is invalid."
    #              error_type = "EMAIL"
    #              email = ""
    #              password = ""
    #              verify_password = ""
    #              return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password,email=email,error=error,error_type=error_type)    

        # Set the username once all tests for a valid username are met
        error = ""
        error_type = ""
        user_name_esc = cgi.escape(user_name, quote=True)     
        password_esc = cgi.escape(password, quote=True)
        verify_password_esc = cgi.escape(verify_password, quote=True)
    #    email_esc = cgi.escape(email, quote=True)

        # Render welcome page once all valid data criteria are met
    #   return render_template('welcome.html', title="Sign up", username=user_name_esc)
        return render_template('newpost.html', title="Sign up", username=user_name_esc)


# Set the home page route. In this application it's the blog page
@app.route('/',methods=['POST','GET'])
def index():
    # pocess the post method
    if request.method == 'POST':
        pass
    else:
        # Process get requests
#       posts = Blog.query.all()                        # Query all blogs
#       posts = Blog.query.order_by(Blog.id.desc()).limit(3).all()    # Query all posts when form is rendered
#       posts = Blog.query.order_by(Blog.id.desc()).all()    # Query all posts when form is rendered


        """
        posts = Blog.query.order_by(Blog.post_date.desc()).all()    # Query all posts when form is rendered
        id = request.args.get("id")                     # Get the blog id
        blog_post = Blog.query.filter_by(id=id).all()   # Get an individual blog
        """


#       return render_template('blog.html',title="Build a Blog", blog_post=blog_post, posts=posts)
        return render_template('login.html',title="Blogz")

# If app is called from main run
if __name__ == '__main__':
    app.run()