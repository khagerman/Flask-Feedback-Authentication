from flask import Flask, render_template, redirect, session, flash
from flask.templating import render_template_string
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import UserForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken.  Please pick another")
            return render_template("register.html", form=form)
        session["user_id"] = new_user.id
        flash("Welcome! Successfully Created Your Account!", "success")
        return redirect(f"/user/{new_user.id}")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session["user_id"] = user.id
            return redirect(f"/user/{user.id}")
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template("login.html", form=form)


@app.route("/logout")
def logout_user():
    session.pop("user_id")
    flash("Goodbye!", "info")
    return redirect("/")


# @app.route("/secret")
# def show_secret():
#     if "user_id" not in session:
#         flash("Please login first!", "danger")
#         return redirect("/login")
#     else:
#         return render_template_string("WELCOME")


@app.route("/user/<int:id>")
def show_user(id):
    if "user_id" not in session or id != session["user_id"]:
        flash("Please login first!", "danger")
        return redirect("/login")
    else:
        user = User.query.get(id)
        return render_template("user.html", user=user)


# @app.route("/tweets", methods=["GET", "POST"])
# def show_tweets():
#     if "user_id" not in session:
#         flash("Please login first!", "danger")
#         return redirect("/")
#     form = TweetForm()
#     all_tweets = Tweet.query.all()
#     if form.validate_on_submit():
#         text = form.text.data
#         new_tweet = Tweet(text=text, user_id=session["user_id"])
#         db.session.add(new_tweet)
#         db.session.commit()
#         flash("Tweet Created!", "success")
#         return redirect("/tweets")

#     return render_template("tweets.html", form=form, tweets=all_tweets)


# @app.route("/tweets/<int:id>", methods=["POST"])
# def delete_tweet(id):
#     """Delete tweet"""
#     if "user_id" not in session:
#         flash("Please login first!", "danger")
#         return redirect("/login")
#     tweet = Tweet.query.get_or_404(id)
#     if tweet.user_id == session["user_id"]:
#         db.session.delete(tweet)
#         db.session.commit()
#         flash("Tweet deleted!", "info")
#         return redirect("/tweets")
#     flash("You don't have permission to do that!", "danger")
#     return redirect("/tweets")


# @app.route("/register", methods=["GET", "POST"])
# def register_user():
#     form = UserForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data
#         new_user = User.register(username, password)

#         db.session.add(new_user)
#         try:
#             db.session.commit()
#         except IntegrityError:
#             form.username.errors.append("Username taken.  Please pick another")
#             return render_template("register.html", form=form)
#         session["user_id"] = new_user.id
#         flash("Welcome! Successfully Created Your Account!", "success")
#         return redirect("/tweets")

#     return render_template("register.html", form=form)


# @app.route("/login", methods=["GET", "POST"])
# def login_user():
#     form = UserForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data

#         user = User.authenticate(username, password)
#         if user:
#             flash(f"Welcome Back, {user.username}!", "primary")
#             session["user_id"] = user.id
#             return redirect("/tweets")
#         else:
#             form.username.errors = ["Invalid username/password."]

#     return render_template("login.html", form=form)


# @app.route("/logout")
# def logout_user():
#     session.pop("user_id")
#     flash("Goodbye!", "info")
#     return redirect("/")
