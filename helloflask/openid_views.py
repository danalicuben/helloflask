import os

from flask import g, session, flash, request, render_template, url_for, redirect
from flaskext.openid import OpenID

from helloflask import app
import settings

DATA_DIR = os.path.join(os.path.expanduser('~'), 'data')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

oid = OpenID(app, DATA_DIR)

openid_urls = {'google': 'https://www.google.com/accounts/o8/id',
               'yahoo': 'https://yahoo.com'}

users = {}

@app.before_request
def lookup_current_user():
    g.user = None
    print 'session', session
    if 'openid' in session:
        g.user = users.get(session['openid'])


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            openid_url = openid_urls.get(openid)
            if openid_url:
                return oid.try_login(openid_url, ask_for=['email', 'fullname', 'nickname'])
    return render_template('login.html', next=oid.get_next_url(), error=oid.fetch_error())


@oid.after_login
def create_or_login(response):
    session['openid'] = response.identity_url
    user = users.get(response.identity_url)
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=response.fullname or response.nickname, email=response.email))


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            users[session['openid']] = {'name': name, 'email': email}
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())


@app.route('/logout')
def logout():
    session.pop('openid', None)
    g.user = None
    flash(u'You were signed out')
    return redirect(oid.get_next_url())

