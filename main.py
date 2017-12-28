from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#from sqlalchemy import Column, Integer, String, Boolean
#from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['DEBUG'] = True
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
        self.owner_id = owner
        self.post_date = post_date
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
#   allowed_routes = ['login','index','signup','blog','newpost','logout']  (Working)
    allowed_routes = ['/','index','login','signup','blog','newpost','logout']
#   allowed_routes = ['/','index','login','signup','blog','newpost']
    # Check to see if the user is logged in. If not redirect to the login page

    current_user = session.get('username') 
    print("Entering the @app.before_request route")
    if request.endpoint not in allowed_routes:
#       return redirect('/blog')
#       return render_template('index.html')
        return redirect('/')

    """
    if request.endpoint == 'newpost':
        if not current_user:
            return redirect('/login')
        else:
            return render_template("newpost.html")
    else:        
        if request.endpoint not in allowed_routes:
            return redirect('/blog')
    """

#            if current_user:
#                render_template("newpost.html")
#            else:
#                return redirect('/blog')
#        return redirect('/login')

"""
    if request.endpoint not in allowed_routes:
        c_user = current_user 

         # Check to see if the user is logged in. If not redirect to the login page
        if current_user == "" or current_user == None:
            return redirect('/login')
        else:
        #        return redirect('/blog')
            return redirect('/blog')
"""

#   allowed_routes = ['login','index','signup','blog','newpost']

# Set the login route
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print('The username from the form is:', username)
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
#           return render_template('login.html')
        else:
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                # Todo - 'remember' that the user has logged in
                session['username'] = username
                u_session = session['username']
                flash('Logged in')
                
                print("Should be redirected to /newpost at this point")
                #return redirect('/newpost')
                #return render_template("newpost.html")
                return redirect('/newpost')
            else:
#               print("User should be empty at this point", user.id)
                # If the user isn't found in the database
                if user == "" or user == None:
                    flash('Username does not exist','error')
                elif user and user.password != password:
                    flash('Password is incorrect.','error')
                else:
                    flash('User password incorrect, or user does not exist','error')
                    return redirect('/login')

        # Redirect if login is successful
        return redirect('/newpost')
#       return render_template('newpost.html')
    else:
        return render_template('login.html')

#       return redirect('/login')    
# Set the blog route
@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.method == 'GET':
        id = request.args.get("id")                                             # Get the id parameter
        blog_user = request.args.get("user")                                    # Get the blogger username

        # Process if there is a blog id returned
        if id:
            posts = []                                                          # If there is an id, there should not be multiple posts
            blog_post = Blog.query.filter_by(id=id).first()                     # Query by single post 
#           print("The post is:", blog_post)
            blog_user_id = blog_post.owner_id
#           print("The post blogger user id is:", blog_user_id)
            blogger = User.query.filter_by(id=blog_user_id).first()
            blog_user = blogger.username
            print("The post is:", blog_post)
            print("The post blogger username is:", blog_user)
            return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts,written_by=blog_user)
        elif blog_user:
            blog_post = []
            user_id = User.query.filter_by(username=blog_user).first()

            post_blogger = User.query.filter_by(id=user_id.id).first()
#           print("The post blogger is:", post_blogger.username)
            posts = post_blogger.blogs
#           print("The posts are:", post_blogger.blogs)            
#           print("The post username is :", post_blogger.username)            
#           print("The posts are:", posts)
        
#           for post in posts:
#               print("The individual post is ", post)
#               for element in post:
#                   print("The post element is ", element)
                    
#           print("The posts are user is:", posts.owner)


#       return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)

#           return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)
            return render_template('singleUser.html',title="Blogz", blog_post=blog_post, posts=posts,written_by=post_blogger.username)
        else:    
            blog_post=[]
#           blog_post = Blog.query.filter_by(id=id).all()       # Query by single post 
            """
            user_id = User.query.filter_by(username=blog_user).first()
            post_blogger = User.query.filter_by(id=user_id.id).first()
            print("The post blogger is:", post_blogger.username)
            posts = post_blogger.blogs
            print("The posts are:", posts)
            return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)
            """

            blog_post = Blog.query.filter_by(id=id).all()       # Query by single post 
#           posts = Blog.query.order_by(Blog.post_date.desc()).all()    # Query all posts when form is rendered
#           post_blogger = User.query.filter_by(id=user_id.id).first()
            posts = User.query.all()
 #          for post in posts:
 #              print("The post is ", post.username)
 #              for blog in post.blogs:
 #                  print("The blog post is ", post.blogs)
            return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)
#       id = 1
#       print("The blog id is:", id)
        
#        blog_user = request.args.get("user")
#        user_id = User.query.filter_by(username=blog_user).first()

#       user_id = request.args.get("user")
#        print("The user_id is:", user_id.id)

 #      written_by = request.args.get("blog_user")
#       print("The blogger is:", written_by)
#        print("The blogger is:", blog_user)

#        blog_post = Blog.query.filter_by(id=id).all()       # Query by single post 
#        print("The blog_post is:", blog_post)
#        #userList = users.query.join(friendships, users.id==friendships.user_id).add_columns(users.userId, users.name, users.email, friends.userId, friendId).filter(users.id == friendships.friend_id).filter(friendships.user_id == userID).paginate(page, 1, False)

#       posts = Blog.query.join(User, Blog.owner_id==User.id).add_columns(User.id, User.username, Blog.id, Blog.title, Blog.blog_body, Blog.owner_id, Blog.post_date)
#       posts = Blog.query.join(User, Blog.owner_id==User.id).add_columns(User.id, User.username, Blog.id, Blog.title, Blog.blog_body, Blog.owner_id, Blog.post_date).filter(User.id == Blog.owner_id)
#       posts = Blog.query.join(User, Blog.owner_id=User.id).add_columns(User.id, User.username, Blog.id, Blog.title, Blog.blog_body, Blog.owner_id, Blog.post_date)
#        post_blogger = User.query.filter_by(id=user_id.id).first()
#        print("The post blogger is:", post_blogger)
#        posts = post_blogger.blogs
#        print("The posts are:", posts)


#       return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)
    else:
        blog_post = Blog.query.filter_by(id=id).all()       # Query by single post 
        posts = Blog.query.order_by(Blog.post_date.desc()).all()    # Query all posts when form is rendered
        
    return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)



# Set the new post route
#@app.route('/newpost', methods=['POST','GET'])
@app.route('/newpost', methods=['GET','POST'])
def newpost():
    current_user = session.get('username') 
    #current_user = current_user.strip()
    if request.method == 'GET':
        if not current_user:
            return redirect('/login')
        else:
            return render_template('newpost.html')
    else:

        # Check to see if the user is logged in. If not redirect to the login page
    #    print("Outside get/post. If the user has logged out, the user is empty", current_user)
        if request.method == 'POST':
            user = session.get('username')
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
                # Submit users entry into the database
                blog_owner = User.query.filter_by(username=user).first()       # Query to get the user id 
                
                owner_id = blog_owner.id

    #           p_date = str(post_date)
                new_blog_entry = Blog(title, blog_body, owner_id, post_date)
    #           new_blog_entry = Blog(title, blog_body, ownerID, post_date)
                db.session.add(new_blog_entry)
                db.session.commit()
                blog_id = str(new_blog_entry.id)

            return redirect("/blog?id=" + blog_id)

    #    if current_user == "" or current_user == None:
    ##       return redirect('/login')
    #        return render_template('login.html')
        else:
    #       return render_template('newpost.html')
            return redirect('/newpost')


# User signup path will validate the fields in the form and
# direct the user to the welcome confirmation message if
# all fields submitted are valid
#@app.route('/signup', methods=['GET','POST'])
@app.route("/signup", methods=['GET','POST'] )
def signup():
    if request.method == 'POST':
        user_name = request.form['username']
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
        # user doesn't exist in the database
        if User == "" or user == None:
            session['username'] = user_name
            new_user = User(user_name, password)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/newpost')
#           return render_template('newpost.html')
        else:
            password = ""
            verify_password = ""
            flash('The user already exists in the database. Please select a different name.','error')            
            return render_template("signup.html",title="Signup", username=user_name,password=password,verify_password=verify_password)
            

#       return render_template('newpost.html')
    else:
        return render_template('signup.html')

# Set the logout path
@app.route('/logout', methods=['GET','POST'])
def logout():
    logged_in_user = session.get('username')
    if logged_in_user:
        del session['username']
#   return redirect('/blog')
    return redirect('/index')

# Set the home page route. In this application it's the blog page
@app.route('/',methods=['GET','POST'])
def index():
    bloggers = User.query.all()    # Query all bloggers
    return render_template('index.html',title="Blogz",bloggers=bloggers)

    """
    # pocess the post method
    if request.method == 'POST':
        return render_template('index.html',title="Blogz",bloggers=bloggers)

#       return render_template('login.html',title="Blogz")
#       return redirect('/blog')
#       return redirect('/index')
    else:
        # Process get requests
 #      bloggers = User.query.all()    # Query all bloggers
        return render_template('index.html',title="Blogz",bloggers=bloggers)
#       return redirect('/index')
#       posts = Blog.query.all()                        # Query all blogs
#       posts = Blog.query.order_by(Blog.id.desc()).limit(3).all()    # Query all posts when form is rendered
#       posts = Blog.query.order_by(Blog.id.desc()).all()    # Query all posts when form is rendered
#        posts = Blog.query.order_by(Blog.post_date.desc()).all()    # Query all posts when form is rendered
#        id = request.args.get("id")                     # Get the blog id
 #       blog_post = Blog.query.filter_by(id=id).all()   # Get an individual blog
#        return render_template('index.html')
#        return render_template('blog.html',title="Blogz", blog_post=blog_post, posts=posts)
#        return render_template('Blog.html',title="Blogz")
#        return redirect('/blog')
    """

# If app is called from main run
if __name__ == '__main__':
    app.run()