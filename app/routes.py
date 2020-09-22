"""
The routes are the different URLs that the application implements
"""
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginFoodForm


@app.route('/')
@app.route('/index')
def index():
    posts = [
        {
            'food': 'Meatballs',
            'time': 20,
            'temp': 190
        },
        {
            'food': 'Salmon Fillet',
            'time': 15,
            'temp': 185
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/post', methods=['GET', 'POST'])
def create_post():
    form = LoginFoodForm()
    if form.validate_on_submit():
        flash('New Post created!')
        return redirect(url_for('index'))
    return render_template('post.html', title='New Recipes', form=form)