from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, abort
from app import app, db
from app.forms import (LoginFoodForm, LoginForm, RegistrationForm, 
                        UpdateAccountForm, ResetPasswordRequestForm, ResetPasswordForm)
from app.models import User, Recipe
from flask_login import current_user, login_user, logout_user, login_required
from app.utils import save_picture
from app.email import send_password_reset_email



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    posts = Recipe.query.order_by(Recipe.timestamp.desc())\
            .paginate(page=page, per_page=per_page)
    return render_template('index.html', posts=posts, title='Home')
   


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))   
        
    return render_template('login.html', title= 'Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'profile_pics')
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = Recipe.query.filter_by(author=current_user)\
        .order_by(Recipe.timestamp.desc())\
        .paginate(page=page, per_page=per_page)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form, posts=posts, user=user)




@app.route('/post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = LoginFoodForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'post_pics')
        title = Recipe(title=form.title.data, time=form.time.data, 
                       temperature=form.temp.data, recipe=form.recipe.data, 
                       author=current_user, image_file=picture_file)
        db.session.add(title)
        db.session.commit()
        flash('New Post created!')
        return redirect(url_for('index'))
    return render_template('new_post.html', title='New Recipes', form=form)


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    user = User.query.filter_by(username=username).first_or_404()
    posts = Recipe.query.filter_by(author=user)\
        .order_by(Recipe.timestamp.desc())\
        .paginate(page=page, per_page=per_page)
    return render_template('user_posts.html', posts=posts, user=user)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Recipe.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

 
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Recipe.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = LoginFoodForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.recipe = form.recipe.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.recipe.data = post.recipe
    return render_template('new_post.html', title='Update Post',
                           form=form, legend='Update Post', post=post)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Recipe.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))