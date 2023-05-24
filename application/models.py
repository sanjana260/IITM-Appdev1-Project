from application.database import db
from flask_login import UserMixin

follows = db.Table(
    'follows',
    db.Column('followed_id',db.Integer, db.ForeignKey('User.id'), nullable = False,primary_key = True),
    db.Column('follower_id',db.Integer, db.ForeignKey('User.id'), nullable = False, primary_key =True)
)

likes = db.Table(
    'likes',
    db.Column('blog_id',db.ForeignKey('Blogs.id'),primary_key = True),
    db.Column('user_id',db.ForeignKey('User.id'),primary_key = True)
)

class Comments(db.Model):
    __tablename__ = 'Comments'
    id = db.Column(db.Integer,autoincrement = True,primary_key = True)
    comment = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer,db.ForeignKey('User.id'), nullable = False)
    blog_id = db.Column(db.Integer,db.ForeignKey('Blogs.id'),nullable = False)
    user = db.relationship('User')
    
class User(db.Model,UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    Username = db.Column(db.String, unique = True, nullable = False)
    Password = db.Column(db.String, nullable = False)
    email = db.Column(db.String, unique = True)
    About = db.Column(db.String)
    Blogs = db.relationship('Blogs',backref = 'user')
    Followers = db.relationship(
        'User',
        secondary = follows,
        primaryjoin = id==follows.c.followed_id,
        secondaryjoin= follows.c.follower_id==id,
        backref = 'Following'
    )
    likes = db.relationship('Blogs',secondary = likes,back_populates = 'liked_by')

class Blogs(db.Model):
    __tablename__ = 'Blogs'
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    Title = db.Column(db.String, nullable = False)
    Caption = db.Column(db.String)
    ImageURL = db.Column(db.String, nullable = False)
    TimeStamp = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'),nullable = False)
    liked_by = db.relationship('User',secondary = likes,back_populates = 'likes')
    comments = db.relationship('Comments')