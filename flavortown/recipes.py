from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from flavortown.database import get_db

bp = Blueprint('recipes', __name__,url_prefix='/recipes')

@bp.route('/list')
def recipes():
    db = get_db()
    # recipes = db.execute(
    #     SELECT 

    # )
    return render_template('recipes/index.html')

@bp.route('/add',methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('home.index'))

    return render_template('blog/create.html')
    