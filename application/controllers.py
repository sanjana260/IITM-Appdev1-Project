from flask import Flask,request,redirect,url_for
from flask import render_template
from flask import current_app as app
from application.models import Blogs,User,Comments
from application.database import db
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
from application.forms import LoginForm, RegisterForm, CreateBlog, SearchForm, EditBlog, EditProfile,CommentForm
from flask_bcrypt import Bcrypt
from application.forms import photos
import datetime,os

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def time(p):
    return p.TimeStamp

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/",methods = ["GET"])
def welcome():
    if(current_user.is_authenticated):
        return redirect("/home")
    return render_template("welcome.html")

@app.route("/login",methods = ["GET","POST"])
def login():
    if(current_user.is_authenticated):
        return redirect("/home")
    form = LoginForm()
    
    if form.validate_on_submit():
        username= form.username.data
        password = form.password.data
        user = User.query.filter(User.Username == username).first()
        if user:
            if bcrypt.check_password_hash(user.Password,password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                form.password.errors.append("Password is incorrect")
        else:
            form.username.errors.append('Username does not exist')
    
    return render_template("login.html",form = form)

@app.route("/register",methods = ["GET","POST"])
def register():
    if(current_user.is_authenticated):
        return redirect("/home")
    form = RegisterForm()

    if form.validate_on_submit():
        print("registering..")
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(Username = form.username.data, Password = hashed_password,email = form.email.data,About = "")
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template("register.html",form = form)

@app.route("/profile",methods = ["GET"])
@login_required
def profile():
    bloglist = current_user.Blogs
    bloglist.sort(reverse = True, key = time)
    return render_template("profile.html",bloglist = bloglist)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('welcome'))

@app.route('/delete_account')
@login_required
def delete_account():
    db.session.delete(current_user)
    db.session.commit()
    return redirect("/")

@app.route("/home",methods = ["GET"])
@login_required
def home():
    form = SearchForm()
    following = [current_user.id]
    for user in current_user.Following:
        following.append(user.id)
    posts = Blogs.query.filter(Blogs.user_id.in_(following)).all()
    
    posts.sort(reverse = True, key = time)

    users = User.query.all()
    return render_template("home.html",posts = posts,users= users, form = form)

@app.route("/search", methods = ["GET","POST"])
def search():
    form = SearchForm()
    search_query = request.args.get("search")
    if not search_query:
        return redirect("/home")
    users = User.query.filter(User.Username.like('%'+search_query+'%')).all()
    return render_template('search_results.html',users=users,form = form,search_query=search_query)

@app.route("/blog/<int:blog_id>", methods = ["GET","POST"])
def blog(blog_id):
    form = CommentForm()
    blog = Blogs.query.get(int(blog_id))
    if not blog:
        return redirect("/home")
    
    if form.validate_on_submit():
        if not (current_user.is_authenticated):
            return redirect("/login")
        comment = Comments(comment = form.comment.data, user_id = current_user.id, blog_id = blog_id)
        db.session.add(comment)
        db.session.commit()
        return redirect("/blog/"+str(blog_id))

    return render_template('blog.html',blog = blog, form = form)

@app.route("/comment/delete/<int:comment_id>",methods = ["GET"])
@login_required
def delete_comment(comment_id):
    comment = Comments.query.get(int(comment_id))
    if not comment.user==current_user:
        return redirect("/home")
    blog_id = comment.blog_id
    db.session.delete(comment)
    db.session.commit()
    return redirect("/blog/"+str(blog_id))

@app.route("/blog/delete/<int:blog_id>",methods = ["GET"])
@login_required
def delete_blog(blog_id):
    blog = Blogs.query.get(int(blog_id))
    if current_user!=blog.user:
        return redirect("/home")
    if blog:
        path = os.getcwd()
        img_path = path+"/static/images/"+blog.ImageURL
        print(img_path)
        comments = Comments.query.filter(Comments.blog_id == blog_id).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.delete(blog)
        db.session.commit()

        if(os.path.exists(img_path)):
            os.remove(img_path)
            print("1 image deleted")
        else:
            print("Image not found")
    return redirect("/profile")

@app.route("/user/<int:user_id>",methods = ["GET"])
def userpage(user_id):
    user = User.query.filter(User.id == user_id).first()
    bloglist = user.Blogs
    bloglist.sort(reverse = True, key = time)
    if(user):
        following = False
        if current_user.is_authenticated:
            if(user_id==current_user.id):
                return redirect("/profile")
            if user in current_user.Following:  
                following = True
        return render_template("userpage.html",user=user,following = following,bloglist=bloglist)
    return redirect('/home')

@app.route("/follow/<int:user_id>",methods = ["GET"])
@login_required
def follow_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect("/home")
    if user!=current_user and user not in current_user.Following:
        user.Followers.append(current_user)
        print(user,len(user.Followers),user.Following)
        db.session.add(user)
        db.session.commit()
        return redirect(request.args.get('redirect'))
    return redirect('/home')

@app.route("/unfollow/<int:user_id>",methods = ["GET"])
@login_required
def unfollow_user(user_id):
    user = User.query.get(int(user_id))
    if not user:
        return redirect("/home")
    if user!=current_user and user in current_user.Following:
        current_user.Following.remove(user)
        db.session.add(current_user)
        db.session.commit()
        return redirect(request.args.get('redirect'))
    return redirect('/home')

@app.route("/create_blog",methods = ["GET","POST"])
@login_required
def create_blog():
    form = CreateBlog()

    if form.validate_on_submit():
        title = form.title.data 
        caption = form.caption.data
        filename = photos.save(form.image.data)
        timestamp = datetime.datetime.now()

        # creating new blog object
        new_blog = Blogs(Title = title, Caption = caption, ImageURL = filename, TimeStamp = timestamp, user_id = current_user.id)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/profile')
    return render_template('create_blog.html',form = form)

@app.route("/blog/edit/<int:blog_id>",methods = ["GET","POST"])
@login_required
def edit_blog(blog_id):
    blog = Blogs.query.get(int(blog_id))
    if not blog:
        return redirect("/home")
    if current_user!=blog.user:
        return redirect("/home")
    form = EditBlog()
    if request.method=='GET':
        form.caption.data=blog.Caption

    if form.validate_on_submit():
        blog.Title = form.title.data 
        blog.Caption = form.caption.data
        print(form.caption.data)
        try:
            # saving new image
            filename = photos.save(form.image.data)
            print("filename: ",filename)

            # deleting the old image
            path = os.getcwd()
            img_path = path+"/static/images/"+blog.ImageURL
            if(os.path.exists(img_path)):
                os.remove(img_path)
                print("Old image deleted")
            else:
                print("Old image not found")
            
            blog.ImageURL = filename
        except:
            print("Image not changed")
        
        db.session.add(blog)
        db.session.commit()

        return redirect('/profile')
    return render_template('edit_blog.html',form = form,blog = blog)

@app.route('/post/like/<int:post_id>',methods = ["GET"])
@login_required
def like_post(post_id):
    blog = Blogs.query.get(int(post_id))
    if not blog:
        return redirect("/home")
    if current_user not in blog.liked_by:
        blog.liked_by.append(current_user)
        db.session.add(blog)
        db.session.commit()
    return redirect(request.args.get('redirect'))

@app.route('/post/unlike/<int:post_id>',methods = ["GET"])
@login_required
def unlike_post(post_id):
    blog = Blogs.query.get(int(post_id))
    if not blog:
        return redirect("/home")
    if current_user in blog.liked_by:
        blog.liked_by.remove(current_user)
        db.session.add(blog)
        db.session.commit()
    return redirect(request.args.get('redirect'))

@app.route("/edit_profile",methods= ["GET","POST"])
@login_required
def edit_profile():
    form = EditProfile()

    if form.validate_on_submit():
        current_user.Username = form.username.data 
        current_user.About = form.about.data 
        db.session.add(current_user)
        db.session.commit()
        return redirect("/profile")

    return render_template('edit_profile.html',form=form)

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response





