__author__ = 'tresback'

import json
from flask import Blueprint, render_template, send_from_directory, request
from pymongo.objectid import ObjectId
from scribble import db
from scribble.storage.models import Scribble
from scribble.wrapper.store_wrappers import make_soup


scribs = Blueprint('scribble_pages', __name__,
        template_folder='templates', static_folder='static')

@scribs.route('/<user_id>', methods=['POST'])
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

@scribs.route('/static/<path:filename>')
def send_foo_file(filename):
    return send_from_directory('wsgi/scribble/static', filename)

@scribs.route('/<user_id>')
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

@scribs.route('/<user_id>/<scribble_id>')
def one_scribble(user_id, scribble_id):
    scribble = Scribble.query.filter(
                Scribble.user_id == user_id,
                Scribble.mongo_id == ObjectId(scribble_id)
                ).one()
    return render_template('one_scribble.html',
            scrib=scribble.filter_out_fields(['mongo_id']))

@scribs.route('/page/<page_name>')
def return_overlay(page_name):
    # home = 'https://scrib-tresback.rhcloud.com'
    page_width = request.args.get('width')
    page_height = request.args.get('height')
    return render_template(page_name, home='https://scrib-tresback.rhcloud.com', 
            page_width=page_width, page_height=page_height)


