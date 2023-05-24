from curses.ascii import US
from distutils.log import error
import werkzeug
from flask import send_file
import uuid,os,datetime
from venv import create
from flask_restful import Resource,reqparse
from application.database import db
from application.models import Blogs, User, Comments
from flask_restful import fields,marshal_with
from application.validation import RaiseError,BusinessValidationError
from application.controllers import bcrypt

# creating parser to receive user input from request
user_parser = reqparse.RequestParser()
user_parser.add_argument('Username')
user_parser.add_argument('Password')
user_parser.add_argument('email')
user_parser.add_argument('About')

# marshal to format output
user_marshal = {
    "id" : fields.Integer,
    "Username": fields.String,
    "About": fields.String,
    "email": fields.String
}

# user api that has CRUD functionality for user
class UserAPI(Resource):

    # basic user information
    @marshal_with(user_marshal)
    def get(self, user_id):
        try:
            user = db.session.query(User).filter(User.id == user_id).first()
        except:
            raise RaiseError(500)

        if user: 
            return user
        else:
            raise RaiseError(404)

    # edit user information
    @marshal_with(user_marshal)
    def put(self, user_id):

        args = user_parser.parse_args()
        email = args.get("email",None)
        About = args.get('About',None)
        Username = args.get("Username",None)
        Password = args.get("Password",None)

        # Check if the user exists
        user = User.query.filter(User.id==user_id).first()
        if(not user):
            raise RaiseError(404)
        
        if(email != None):
            existing_email = User.query.filter(User.email == email).first()
            if existing_email:
                raise BusinessValidationError(statuscode=400,error="USER02",error_message="Email already exists")
            user.email = email

        if Username != None:
            existing_username = User.query.filter(User.Username == Username).first()
            if existing_username:
                raise BusinessValidationError(statuscode=400,error="USER01",error_message="Username already exists")
            if len(Username)<5:
                raise BusinessValidationError(statuscode=400,error="USER05",error_message="Username is too short")
            user.Username = Username
        
        if Password != None:
            if len(Password)<8:
                raise BusinessValidationError(statuscode=400,error="USER06",error_message="Password is too short")
            hashed_password = bcrypt.generate_password_hash(Password)
            user.Password = hashed_password
        
        if About != None:
            user.About = About
        
        db.session.add(user)
        db.session.commit()

        return user,200
    
    def delete(self, user_id):
        # Check if the user exists
        user = User.query.filter(User.id==user_id).first()
        if(not user):
            raise RaiseError(404)

        # Check if there are articles for the users
        blogs = Blogs.query.filter(Blogs.user_id == user_id).all()
        for blog in blogs:
            db.session.delete(blog)

        # Delete
        db.session.delete(user)
        db.session.commit()

        return "Successfully Deleted",201
    
    @marshal_with(user_marshal)
    def post(self):
        args = user_parser.parse_args()
        email = args.get("email",None)
        About = args.get('About',None)
        Username = args.get("Username",None)
        Password = args.get("Password",None)

        user = User()
        
        if(email != None):
            existing_email = User.query.filter(User.email == email).first()
            if existing_email:
                raise BusinessValidationError(statuscode=400,error="USER02",error_message="Email already exists")
            user.email = email
        else:
            raise BusinessValidationError(statuscode=400,error="USER04",error_message="Email is required")

        if Username != None:
            existing_username = User.query.filter(User.Username == Username).first()
            if existing_username:
                raise BusinessValidationError(statuscode=400,error="USER01",error_message="Username already exists")
            if len(Username)<5:
                raise BusinessValidationError(statuscode=400,error="USER05",error_message="Username is too short")
            user.Username = Username
        else:
            raise BusinessValidationError(statuscode=400,error="USER03",error_message="Username is required")
        
        if Password != None:
            if len(Password)<8:
                raise BusinessValidationError(statuscode=400,error="USER06",error_message="Password is too short")
            hashed_password = bcrypt.generate_password_hash(Password)
            user.Password = hashed_password
        else:
            raise BusinessValidationError(statuscode=400,error="USER07",error_message="Password is required")
        
        if About != None:
            user.About = About
        
        db.session.add(user)
        db.session.commit()

        return user,201

blog_marshal = {
    "id" : fields.Integer,
    "Title": fields.String,
    "Caption": fields.String,
    "ImageURL": fields.String,
    "user_id": fields.String
}

class BlogAPI(Resource):

    @marshal_with(blog_marshal)
    def get(self,blog_id):
        blog = Blogs.query.get(int(blog_id))
        if blog:
            return blog,201
        raise RaiseError(404)

    
    @marshal_with(blog_marshal)
    def put(self,blog_id):
        blog = Blogs.query.get(int(blog_id))
        if not blog:
            raise RaiseError(404)
        blog_parser = reqparse.RequestParser()
        blog_parser.add_argument('Title',location ='form')
        blog_parser.add_argument('Caption',location = 'form')
        blog_parser.add_argument('Image', type=werkzeug.datastructures.FileStorage, location='files')
        args = blog_parser.parse_args()
        if(args.get('Title',None)):
            blog.Title = args.get('Title',None)
        if(args.get('Caption',None)):
            blog.Caption = args.get('Caption',None)
        if(args['Image']):
            # deleting the old image
            path = os.getcwd()
            img_path = path+"/static/images/"+blog.ImageURL
            if(os.path.exists(img_path)):
                os.remove(img_path)
                print("Old image deleted")
            else:
                print("Old image not found")

            path = os.getcwd()
            blog.ImageURL = args["Image"].filename
            filename = path+"/static/images/"+args["Image"].filename
            print(filename)
            args['Image'].save(filename)
        print(blog)
        db.session.add(blog)
        db.session.commit()
        return blog,200
    
    def delete(self,blog_id):
        blog = Blogs.query.get(int(blog_id))
        if not blog:
            raise RaiseError(404)
        # deleting the old image
        path = os.getcwd()
        img_path = path+"/static/images/"+blog.ImageURL
        if(os.path.exists(img_path)):
            os.remove(img_path)
            print("Image deleted")
        else:
            print("Image not found")
        comments = Comments.query.filter(Comments.blog_id == blog_id).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.delete(blog)
        db.session.commit()
        return "Successfully Deleted",200
    
    @marshal_with(blog_marshal)
    def post(self):
        blog_parser = reqparse.RequestParser()
        blog_parser.add_argument('id',location = 'form')
        blog_parser.add_argument('Title',location ='form')
        blog_parser.add_argument('Caption',location = 'form')
        blog_parser.add_argument('user_id',location = 'form')
        blog_parser.add_argument('Image', type=werkzeug.datastructures.FileStorage, location='files')
        args = blog_parser.parse_args()
        blog = Blogs()
            
        # title
        if not (args.get('Title',None)):
            raise BusinessValidationError(statuscode=400,error='BLOG01',error_message='Blog Title is required')
        else:
            blog.Title = args.get('Title',None)

        # caption
        if (args.get('Caption',None)):
            blog.Caption = args.get('Caption',None)
        else:
            blog.Caption = ''
        
        # image
        if(args['Image']):
            path = os.getcwd()
            blog.ImageURL = args["Image"].filename
            filename = path+"/static/images/"+args["Image"].filename
            print(filename)
            args['Image'].save(filename)
        else:
            raise BusinessValidationError(statuscode=400,error='BLOG02',error_message='Blog Image is required')

        if(args['user_id']):
            user_id = args['user_id']
            user = User.query.get(int(user_id))
            if not user:
                raise BusinessValidationError(statuscode=400,error='BLOG04',error_message='User does not exist')
            blog.user_id = user_id 
        else:
            raise BusinessValidationError(statuscode=400, error='BLOG03',error_message='User ID is required')
        
        blog.TimeStamp = datetime.datetime.now()
        db.session.add(blog)
        db.session.commit()
        return blog,201

# api to view the image file sent by the blog api
class ImageAPI(Resource):
    def get(self,ImageURL):
        path = os.getcwd()
        img_path = path+"/static/images/"+ImageURL
        try:
            return send_file(img_path)
        except:
            raise RaiseError(404)
