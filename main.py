from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
import requests
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = './static/pics'
WTF_KEY = os.environ.get("WTF_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = WTF_KEY
Bootstrap(app)


# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books_2021.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CREATE TABLE
class BookTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    author = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    pages = db.Column(db.Integer, nullable=False)


db.create_all()


# CREATE ADD FORM
class AddBookForm(FlaskForm):
    number = IntegerField(label="Number", validators=[NumberRange(0,100)])
    title = StringField(label="Title", validators=[DataRequired()])
    author = StringField(label="Author", validators=[DataRequired()])
    year = IntegerField(label="Year", validators=[NumberRange(0,2021)])
    pages = IntegerField(label="Pages", validators=[NumberRange(0,5000)])
    submit = SubmitField(label="Upload")

#
# # CREATE EDIT FORM
# class AddForm(FlaskForm):
#     title = StringField("Title", validators=[DataRequired()])
#     author = StringField("Author", validators=[DataRequired()])
#     year = StringField("Year", validators=[DataRequired()])
#     pages = StringField("Pages", validators=[DataRequired()])
#     submit = SubmitField("Upload")


@app.route("/")
def home():
    files = os.listdir('static/pics')
    pics = ['pics/' + file for file in files]
    return render_template("index.html", pics=pics)


# Photo upload
@app.route("/up", methods = ['GET','POST'])
def upload_file():
    if request.method =='POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            return redirect(url_for('home'))
    return render_template('upload.html')


# Add book
@app.route("/add", methods=["GET", "POST"])
def add_book():
    # GET request
    form = AddBookForm()
    # POST request
    if form.validate_on_submit():
        book_number = form.number.data
        book_title = form.title.data
        book_author = form.author.data
        book_year = form.year.data
        book_pages = form.pages.data
        new_book = BookTable(number=book_number, title=book_title, author=book_author, year=book_year, pages=book_pages)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('show_list'))
    return render_template("add.html", form=form)


@app.route("/list")
def show_list():
    all_books = BookTable.query.order_by(BookTable.number).all()
    return render_template("list.html", books=all_books)


@app.route("/delete")
def delete():
    # book_id_to_delete comes from list.html with the get request
    book_id = request.args.get('book_id_to_delete')
    book_selected = BookTable.query.get(book_id)
    db.session.delete(book_selected)
    db.session.commit()
    return redirect(url_for('show_list'))


@app.route("/edit", methods=["GET", "POST"])
def edit():

    # GET request
    # >>> we create a form object from the form class
    edit_form = AddBookForm()
    # >>> book_id_to_edit comes from list.html (edit)
    book_id = request.args.get('book_id_to_edit')
    book_selected = BookTable.query.get(book_id)

    # POST request - we already know from get request which movie is selected
    if edit_form.validate_on_submit():
        # >>> update data of the selected book
        book_selected.title = edit_form.title.data
        book_selected.author = edit_form.author.data
        book_selected.year = edit_form.year.data
        book_selected.pages = edit_form.pages.data
        db.session.commit()
        return redirect(url_for('show_list'))

    # >>> render the edit.html + send the form object + the movie we wanna edit
    return render_template("add.html", form=edit_form, edit_this_book=book_selected)


if __name__ == '__main__':
    app.run(debug=True)

