from application.models import User
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FileField,TextAreaField,EmailField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from flask_wtf.file import FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES
from flask_login import current_user

# flask uploads upload set
photos = UploadSet('photos',extensions=('png','jpg','jpeg'))

# validation functions
def validate_username_edit(self,username):
    if(username.data!=current_user.Username):
        existing_user = User.query.filter(User.Username == username.data).first()
        if(existing_user):
            print("Validation error: username already exists")
            raise ValidationError("This username already exists. Try something else!")

def validate_username(self,username):
    existing_user = User.query.filter(User.Username == username.data).first()
    if(existing_user):
        raise ValidationError("This username already exists. Try something else!")

def validate_email(self,email):
    email = email.data
    existing_user_email = User.query.filter(User.email == email).first()
    if existing_user_email:
        raise ValidationError("An account with this email already exists! Maybe try logging in!")

# form classes to be exported
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=5,max=100),validate_username],render_kw={'placeholder':'Username'})
    email = EmailField(validators=[InputRequired(),Length(min=5,max=100),Email(),validate_email],render_kw={'placeholder':'Email'})
    password = PasswordField(validators=[InputRequired(),Length(min=8,max=100)],render_kw={'placeholder':'Password'})
    submit = SubmitField("Register")
    

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=5,max=100)],render_kw={'placeholder':'Username'})
    password = PasswordField(validators=[InputRequired(),Length(min=8,max=100)],render_kw={'placeholder':'Password'})
    submit = SubmitField("Login")


class CreateBlog(FlaskForm):
    title = StringField(validators=[InputRequired(),Length(min=3)],render_kw={'placeholder':'Title'})
    caption = TextAreaField(render_kw={'placeholder':'Description'})
    image = FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired("Please upload an image!")])
    submit = SubmitField("Create")

class EditBlog(FlaskForm):
    title = StringField(validators=[InputRequired(),Length(min=3)],render_kw={'placeholder':'Title'})
    caption = TextAreaField(render_kw={'placeholder':'Description'})
    image = FileField(validators=[FileAllowed(photos, 'Image only!')])
    submit = SubmitField("Save Changes")

class EditProfile(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=5,max=100),validate_username_edit],render_kw={'placeholder':'Username'})
    about = StringField(render_kw={'placeholder':'About you..'})
    submit = SubmitField("Save Changes")

class SearchForm(FlaskForm):
    search = StringField(validators=[InputRequired()],render_kw={'placeholder':'Search users..'})
    submit = SubmitField("Search")

class CommentForm(FlaskForm):
    comment = StringField(validators=[InputRequired()],render_kw={'placeholder':'Tell them what you think..'})
    submit = SubmitField("Post")