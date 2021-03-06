import sys

import requests
from twilio.rest import TwilioRestClient
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
    subject = request.form.get('subject')
    from_ = request.form.get('from')
    stripped_text = request.form.get('stripped-text')

    r = requests.post('https://api.mailgun.net/v2/helloflask.mailgun.org/messages',
                       auth=('api', settings.MAILGUN_KEY),
                       data={'from': 'norepy <noreply@helloflask.mailgun.org>',
                             'to': [from_],
                             'subject': subject,
                             'text': stripped_text})
    print 'Email:', r.text

    parts = subject.split()
    if 'sms' in parts:
        try:
            twilio = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_AUTH)
            sms = twilio.sms.messages.create(to=parts[-1],
                                         from_='14254096111',
                                         body=stripped_text[:160])
            print 'SMS', sms.status
        except Exception as e:
            print e

    return ''

@app.route('/headers/accept')
def best_match_accept():
    mimetypes = request.accept_mimetypes
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return render_template('accept.html', mimetypes=str(mimetypes))