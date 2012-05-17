from bs4 import BeautifulSoup, Comment, Tag
from copy import copy
import json
import re
import os
import urlparse
import uuid
from flask import Flask, request, url_for, session, flash,\
    render_template
from flask.ext.oauth import OAuth
from flaskext.mongoalchemy import MongoAlchemy
from mongoalchemy.document import Index
from pymongo.objectid import ObjectId

app = Flask(__name__, static_path='/static')

app.debug = True
app.secret_key = str(uuid.uuid1())

env_url = os.environ.get('MONGOLAB_URI')

host ='flame.mongohq.com'
port = 27086
database_name = 'app4322516'

app.config['MONGOALCHEMY_DATABASE'] = 'scribble'
db = MongoAlchemy(app)

class ScribData(db.Document):
    def filter_out_fields(self, remove_keys):
        return dict([(key_, getattr(self, key_)) for key_ in self.get_fields().iterkeys() if key_ not in remove_keys and hasattr(self, key_)])

class Scruser(ScribData):
    user_id = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    email = db.StringField()
    id_index = Index().ascending('user_id')

class Scribble(ScribData):
    user_id = db.StringField()
    canvas_data = db.ListField(db.TupleField(db.TupleField(
                    db.IntField(), db.IntField()), 
                    db.IntField(), db.IntField(), 
                    db.IntField(), db.IntField()), 
                    allow_none=True)
    marks_points = db.ListField(db.TupleField(db.TupleField(db.IntField(), db.IntField()), db.StringField()))
    tags = db.ListField(db.StringField(), allow_none=True)
    base_html = db.StringField()
    base_url = db.StringField()
    image_data = db.StringField()
    original_width = db.IntField()
    user_index = Index().ascending('user_id')
    tags_index = Index().ascending('tags')
    

tester = Scruser.query.filter(
    Scruser.first_name == 'Test_user').first()
if tester is None:
    tester = Scruser(user_id=str(uuid.uuid4()),
                    first_name='Test_user',
                    last_name='testuser',
                    email='test@email.com')
    tester.save()

    

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='305702342839641',
    consumer_secret='43534fcacd8e1fda402ab611e913ae27'
)


@app.before_request
def convert_json():
    if request.data and request.data is not None:
        request.data = json.loads(request.data)

@app.after_request
def add_headers(response):
    if isinstance(response.data, dict) or isinstance(response.data, list):
        response.headers['Content-Type'] = 'application/json'
    response.headers.add_header('Access-Control-Allow-Origin', '*')
    response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type')
    return response

def find_all_ref_tags(tag):
     tag_val = tag.get('src', tag.get('href', tag.get('style')))
     return tag_val is not None

def modify_path(path, tag_path):
    append_list = [res for res in tag_path.split('/') 
                   if res and res != '..' 
                        and res != '.']
    path.extend(append_list)
    return path


def modify_rels(tag, base_url):
    parsed = urlparse.urlparse(base_url)                    
    path = [res for res in parsed.path.split('/') if res]
    # Attrs that would have a relative path
    tag_attr = dict(img='src', script='src', a='href',
                    link='href')
    attr = tag_attr.get(tag.name)
    if attr is not None:
        tag_val = tag.get(attr)
        new_path = parse_path(path, tag_val)
        new_url = urlparse.urlunsplit((parsed.scheme, 
                                       parsed.netloc,
                                       '/'.join(new_path), '', ''))
        tag[attr] = str(new_url)
    if tag.get('style') is not None:
        # Must be something with a url() style reference
        def style_callb(match):
            rel_path = match.group(1).lstrip("'").rstrip("'")
            new_path = parse_path(path, rel_path)
            return "url('%s')" % urlparse.urlunsplit((parsed.scheme, 
                                           parsed.netloc,
                                           '/'.join(new_path), '', ''))
        style_links = re.sub('url\((.*?)\)', style_callb,
                             tag.get('style'))
        tag['style'] = style_links
    return tag


def parse_path(path, tag_val):
    up_dirs = re.findall('\.\.\/', tag_val)
    if up_dirs:
        for up in up_dirs:
            path.pop()
        path = modify_path(path, tag_val)
    elif re.findall('\.\/', tag_val) or \
         re.findall(r'^(?!http://)', tag_val):
        path = modify_path(path, tag_val)
    return path

def remove_scribble_elements(scribble_tag):
    for tag in scribble_tag:
        tag.extract()

def make_soup(base_html, base_url):
    soup = BeautifulSoup(base_html, "lxml")    
    ref_tags = [modify_rels(tag, base_url) 
                    for tag  in soup.find_all() 
                        if find_all_ref_tags(tag)]
    remove_scribble_elements(soup.find_all(id=
                                'scribble_overlay'))
    remove_scribble_elements(soup.find_all('script')) 
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    new_script = Tag(soup, name="script")
    body_css =  """
            html { zoom: .01 
                -moz-transform: scale(0.75);
                    -moz-transform-origin: 0 0;
                        -o-transform: scale(0.75);
                            -o-transform-origin: 0 0;
                                -webkit-transform: scale(0.75);
                                    -webkit-transform-origin: 0 0;
            }
    """
    new_script.insert(0, body_css)
    new_script['type'] = 'text/css'
    soup.body.insert(0, new_script)
    return unicode(soup)

@app.route('/<user_id>', methods=['POST'])
def new_scribble(user_id):
    base_html = request.data['base_html']
    base_url = request.data['base_url']
    base_html = make_soup(base_html, base_url)
    scribble = Scribble(user_id=user_id, 
                        canvas_data=request.data.get('canvas_data'), 
                        marks_points=request.data.get('marks_data'), 
                        tags=request.data.get('tags'), 
                        base_html=base_html, base_url=base_url,
                        image_data=request.data.get('image_data'),
                        original_width=request.data.get('original_width'))
    scribble.save()
    scribble = scribble.filter_out_fields([])
    scribble['mongo_id'] = str(scribble['mongo_id'])
    return json.dumps(scribble)

@app.route('/static/<path:filename>')
def send_foo_file(filename):
    return send_from_directory('static', filename)

@app.route('/<user_id>')
def my_scribbles(user_id):
    scribbles = Scribble.query.filter(Scribble.user_id == user_id).all()
    scrib_list = list()
    for index, scribble in enumerate(scribbles):
        scribble = scribble.filter_out_fields([])
        scribble['mongo_id'] = str(scribble['mongo_id'])
        scribble['base_html'] = scribble['base_html']
        scrib_list.append(scribble)
    return render_template('all_scribbles.html', 
                           scribbles=scrib_list)

@app.route('/<user_id>/<scribble_id>')
def one_scribble(user_id, scribble_id):
    scribble = Scribble.query.filter(
                Scribble.user_id == user_id,
                Scribble.mongo_id == ObjectId(scribble_id)
                ).one()
    return render_template('one_scribble.html',
            scrib=scribble.filter_out_fields(['mongo_id']))


@app.route('/login')
def login():
    return facebook.authorize(
        callback=url_for('facebook_authorized',
            next=request.args.get('next') or 
            request.referrer or None,
            _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        flash('You were denied')
        return '401 Unauthorized'


    me = facebook.get('/me')
    flash('Successfully logged in')
    return str(me.data)

if __name__ == '__main__':
    app.run('0.0.0.0')
