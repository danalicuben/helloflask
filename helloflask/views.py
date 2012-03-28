import sys
import urllib
import urllib2
import base64


from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError
from flask import url_for, request, render_template, Markup, abort
from helloflask import app

import settings

@app.before_request
def before_request1():
   print request.url

   
@app.before_request
def before_request2():
   print 'before 2'


@app.route('/')
def index():
   return render_template('index.html')


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

   
@app.route('/slash/')
def slash():
    return 'Slash'

   
@app.route('/arg/<name>')
def show_arg(name):
    return 'Show args %s - %s' % (name, request.args.get('foo', 'no arg foo'))

   
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'post_id: %d (%r)' % (post_id, type(1))

   
@app.route('/test_url_for')
def test_url_for():
    return url_for('show_arg', name='abc', foo='bar')

   
@app.route('/method', methods=['GET', 'POST'])
def methods():
    return 'request.method: %s' % request.method


@app.route('/safe')
def safe():
    return Markup('<strong>Hello %s!</strong>') % '<blink>Hacker</blink>'


@app.route('/maps/demo')
def map_demo_openlayers():
    return render_template('map_demo_openlayers.html')  


@app.route('/maps/london')
def map_london_openlayers():
    library = request.args.get('library')
    if library == 'openlayers':
        return render_template('map_london_openlayers.html')  
    if library == 'leaflet':
        return render_template('map_london_leaflet.html') 
    abort(404) 


@app.route('/versions')
def versions():
    import boto
    import flask
    import jinja2
    import werkzeug
    v = [('Python', sys.version.split()[0]),
         ('Flask', flask.__version__),
         ('Jinja2', jinja2.__version__),
         ('Werkzeug', werkzeug.__version__),
         ('Boto', boto.__version__)]
    return render_template('versions.html', versions=v)


@app.route('/dynamodb/<key>')
def set_dynamodb(key):
    method = request.args.get('_method')
  
    if request.method == 'PUT' or method == 'PUT':
        try:
            item = settings.DYNAMODB_TABLE_HELLOFLASK.get_item(key)
        except DynamoDBKeyNotFoundError:
            item = settings.DYNAMODB_TABLE_HELLOFLASK.new_item(key)

        for k, v in request.args.iteritems():
            if k != '_method':
                item[k] = v
        item.put()
        d = dict(item)
        del d['name']
        return 'SET item={}, {}'.format(key, d)
    elif request.method == 'DELETE' or method == 'DELETE':
        if key:
            try:
                item = settings.DYNAMODB_TABLE_HELLOFLASK.get_item(key)
            except DynamoDBKeyNotFoundError:
                return "Item '{}' not found".format(key)
            else:
                item.delete()
                return 'DELETED item={}'.format(key)
        else:
            abort(400)
    elif request.method == 'GET':
        if key:
            try:
                item = settings.DYNAMODB_TABLE_HELLOFLASK.get_item(key)
            except DynamoDBKeyNotFoundError:
                return "Item '{}' not found".format(key)
            else:
                d = dict(item)
                del d['name']
                return 'Item={}, {}'.format(key, d)
        else:
            abort(400)
    else:
        return '???'


@app.route('/mailbox/echo', methods=['POST'])
def mailbox_echo():
    data = urllib.urlencode({
                 "from": 'echo@helloflask.mailgun.org',
                 "to": request.form.get('from')
                 "subject": request.form.get('subject')
                 "text": request.form.get('stripped-text')
                 })

    request = urllib2.Request('https://api.mailgun.net/v2/helloflask.mailgun.org/messages')
    base64string = base64.encodestring('%s:%s' % ('api', settings.MAILGUN_KEY)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)  
    urllib2.urlopen(request, data).read()
    return ''
