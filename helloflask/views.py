from flask import url_for, request, render_template, Markup
from helloflask import app

@app.before_request
def before_request1():
   print request.url
   
@app.before_request
def before_request2():
   print 'before 2'


@app.route('/')
def index():
   return 'Index page'


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
   
@app.route('/slash/')
def slash():
    return 'Slash'
   
@app.route('/user/<username>')
def show_user_profile(username):
    return 'Show User Profile %s - %s' % (username, request.args.get('foo', 'no arg foo'))
   
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'post_id: %d (%r)' % (post_id, type(1))
   
@app.route('/test_url_for')
def test_url_for():
    return url_for('show_user_profile', username='Bryan', foo='bar')
   
@app.route('/method', methods=['GET', 'POST'])
def methods():
   return 'request.method: %s' % request.method

@app.route('/safe')
def safe():
   return Markup('<strong>Hello %s!</strong>') % '<blink>Hacker</blink>'

    
