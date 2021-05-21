from flask import Flask, render_template, redirect, session, flash
from flask.templating import render_template_string
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import PostForm, UserForm, LoginForm
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hellosecret1")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    """return restistration form or if loggerd in, user profile"""
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_user():
    if "user_id" in session:
        return redirect(f"/user/{session['user_id']}")
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
    user = User.query.get_or_404(id)
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    if user.id != session["user_id"]:
        flash("You don't have permission to view this profile.", "danger")
        return redirect("/")
    else:

        return render_template("user.html", user=user)


@app.route("/user/<int:id>/delete", methods=["POST"])
def delete_user(id):
    """Delete post"""
    user = User.query.get_or_404(id)
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")

    if user.id == session["user_id"]:
        db.session.delete(user)
        db.session.commit()
        session.pop("user_id")
        flash("Account deleted!", "info")
        return redirect("/register")
    flash("You don't have permission to do that!", "danger")
    return redirect("/")


@app.route("/user/<int:id>/feedback/add", methods=["GET", "POST"])
def add_feedback(id):
    """Render form to add new feedback (post)"""
    user = User.query.get_or_404(id)
    form = PostForm()
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    if user.id != session["user_id"]:
        flash("You don't have permission to do that!", "danger")
        return redirect("/")
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, user_id=session["user_id"])

        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/user/{user.id}")
    else:
        return render_template("post.html", form=form, user_id=user.id)


@app.route("/feedback/<int:id>/update", methods=["GET", "POST"])
def update_feedback_form(id):
    """Show edit feedback form and submit"""
    feedback = Feedback.query.get_or_404(id)
    form = PostForm(obj=feedback)
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    if feedback.user_id != session["user_id"]:

        print(feedback.user.user_id)
        flash("You don't have permission to do that!", "danger")
        return redirect("/")
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/user/{feedback.user_id}")
    else:
        return render_template("edit.html", form=form, feedback=feedback)


# @app.route("/feedback/<int:id>/update", methods=["POST"])
# def update_feedback(id):
#     """Edit feedback"""
#     form = PostForm()
#     if "user_id" not in session:
#         flash("Please login first!", "danger")
#         return redirect("/login")
#     feedback = Feedback.query.get_or_404(id)
#     if feedback.user_id == session["user_id"]:
#         if form.validate_on_submit():
#             feedback.title = form.title.data
#             feedback.content = form.content.data

#             db.session.commit()
#         return redirect(f"/user/{feedback.user_id}")
#     flash("You don't have permission to do that!", "danger")
#     return redirect("/")


@app.route("/feedback/<int:id>/delete", methods=["POST"])
def delete_feedback(id):
    """Delete feedback"""
    feedback = Feedback.query.get_or_404(id)
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")

    if feedback.user_id == session["user_id"]:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", "info")
        return redirect(f"/user/{feedback.user_id}")
    flash("You don't have permission to do that!", "danger")
    return redirect("/login")
