from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginFoodForm, LoginForm, RegistrationForm, UpdateAccountForm
from app.models import User, Recipe
from flask_login import current_user, login_user, logout_user, login_required
from app.utils import save_picture




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
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


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
    return render_template('post.html', title='New Recipes', form=form)


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    user = User.query.filter_by(username=username).first_or_404()
    posts = Recipe.query.filter_by(author=user)\
        .order_by(Recipe.timestamp.desc())\
        .paginate(page=page, per_page=per_page)
    return render_template('user_posts.html', posts=posts, user=user)


