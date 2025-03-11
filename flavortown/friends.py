from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flavortown.auth import login_required
from flavortown.database import get_db
from datetime import datetime
import calendar

bp = Blueprint('friends', __name__,url_prefix='/friends')

@bp.route('/')
def index():
    db = get_db()
    friends = db.execute(
        'SELECT f.name,f.birthday,f.id'
        ' FROM friends f '
    ).fetchall()
    return render_template('friends/index.html', friends=friends)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        if request.form:
            print(request.form)
            name = request.form['name']
            birthday = request.form['birthday']
            error = None

        if not name:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO friends (name, birthday)'
                ' VALUES (?, ?)',
                (name,birthday)
            )
            db.commit()
            return redirect(url_for('friends.index'))

    return render_template('friends/create.html')

def get_friend(id):
    friend = get_db().execute(
        'SELECT f.name,f.birthday,id FROM friends f'
        ' WHERE f.id = ?',
        (id,)
    ).fetchone()

    if friend is None:
        abort(404, f"Friend doesn't exist.")

    return friend

@bp.route('/<int:id>', methods=('GET', 'POST'))
@login_required
def accessFriend(id):
    now = datetime.now()
    year = now.year
    month = now.month
    highlighted_dates =[2,6,10]
    # Generate the HTML calendar
    cal = HighlightedHTMLCalendar(highlighted_dates)
    calendar_html = cal.formatmonth(year, month)
    friend = get_friend(id)

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
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('friends.index'))

    return render_template('friends/friend.html', friend=friend,calendar_html=calendar_html,now=now)

class HighlightedHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, highlighted_dates):
        super().__init__()
        self.highlighted_dates = highlighted_dates

    def formatday(self, day, weekday):
        if day != 0:
            if day in self.highlighted_dates:
                return f'<td class="highlight">{day}</td>'
            return f'<td>{day}</td>'
        return '<td></td>'