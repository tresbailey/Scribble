__author__ = 'tresback'

import json
import os
from flask import Blueprint, render_template, send_from_directory, request, jsonify, url_for
from gridfs import NoFile
from pymongo.objectid import ObjectId
from PIL import Image
from selenium import webdriver
from scribble import db, scrib_grid, celery
from scribble.storage.models import Scribble
from scribble.wrapper.store_wrappers import make_soup

scribs = Blueprint('scribble_pages', __name__,
        template_folder='scribble/templates', static_folder='static')

HOME_URL = os.getenv('OPENSHIFT_GEAR_DNS', 'http://localhost')
PHANTOM_HOME = os.getenv('OPENSHIFT_PHANTOM_DIR', '/home/tres/phantom/phantomjs-1.9.1-linux-x86_64/')

def request_for_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


@celery.task
def create_capture(capture_id, scribble_id, args, kwargs):
    #scribble_url = url_for(*args, **kwargs)
    print "capture: %s " % capture_id
    scribble_url = 'https://' + HOME_URL +'/'+ kwargs['user_id'] +'/'+ kwargs['scribble_id']
    driver = webdriver.PhantomJS( PHANTOM_HOME + "bin/phantomjs")
    driver.get(scribble_url)
    scribble = Scribble.query.filter(
                Scribble.mongo_id == ObjectId(scribble_id)
                ).one()
    
    with open("scribble/static/js/scribble_frame.js") as scribjs:
        with open("scribble/static/js/load_scripts.js") as loaderjs:
            driver.execute_script(loaderjs.read())
    driver.save_screenshot("scribble.png")
    thumb = Image.open("scribble.png")
    thumb.thumbnail((500, 2000), Image.ANTIALIAS)
    thumb.save("scribble.png", "PNG")
    with open("scribble.png") as scrib_shot:
        oid = scrib_grid.put(scrib_shot, _id=capture_id, content_type="image/png", filename="scribble")
        return oid


@scribs.route('/<user_id>', methods=['POST'])
def new_scribble(user_id):
    print 'Got some request data from post' 
    base_html = request.data['base_html']
    base_url = request.data['base_url']
    scribble_id = ObjectId()
    base_html = make_soup(base_html, base_url, user_id, scribble_id)
    scribble = Scribble(user_id=user_id, mongo_id=scribble_id,
                        canvas_data=request.data.get('canvas_data'), 
                        marks_points=request.data.get('marks_data'), 
                        tags=request.data.get('tags'), 
                        base_html=base_html, base_url=base_url,
                        image_data=request.data.get('image_data'),
                        original_width=request.data.get('original_width'))
    print 'Saving to mongodb'
    scribble.scrib_shot = ObjectId()
    scribble.save()
    scrib_capt = create_capture.apply_async((str(scribble.scrib_shot), str(scribble.mongo_id), 'one_scribble', dict(user_id=user_id, scribble_id=str(scribble.mongo_id))))
    scribble = scribble.filter_out_fields([])
    scribble['mongo_id'] = str(scribble['mongo_id'])
    scribble['scrib_shot'] = str(scribble['scrib_shot'])
    return json.dumps(scribble)


@scribs.route('/<user_id>')
def my_scribbles(user_id):
    scribbles = Scribble.query.filter(Scribble.user_id == user_id).all()
    scrib_list = list()
    for index, scribble in enumerate(scribbles):
        scribble = scribble.filter_out_fields([])
        scribble['mongo_id'] = str(scribble['mongo_id'])
        scribble['base_html'] = scribble['base_html']
        if 'scrib_shot' in scribble:
            try:
                scribble['capture'] = scrib_grid.get(str(scribble['scrib_shot'])).read()
            except NoFile:
                pass
        scrib_list.append(scribble)
    if request_for_json():
        return jsonify(scribbles=scrib_list)
    return render_template('all_scribbles.html', 
                           scribbles=scrib_list)

@scribs.route('/<user_id>/captures/<scrib_shot>')
def one_scrib_capture( user_id, scrib_shot ):
    return scrib_grid.get(scrib_shot).read()

@scribs.route('/<user_id>/<scribble_id>')
def one_scribble(user_id, scribble_id):
    scribble = Scribble.query.filter(
                Scribble.user_id == user_id,
                Scribble.mongo_id == ObjectId(scribble_id)
                ).one()
    if request_for_json():
        return jsonify(scribble.filter_out_fields(['mongo_id']))
    scribble = scribble.filter_out_fields(['mongo_id'])
    scribble['scrib_shot'] = str(scribble['scrib_shot'])
    #return render_template('one_scribble.html',
    #        scrib=scribble)
    return scribble['base_html']

@scribs.route('/<user_id>/<scribble_id>/canvas')
def one_scribble_canvas(user_id, scribble_id):
    scribble = Scribble.query.filter(
                Scribble.user_id == user_id,
                Scribble.mongo_id == ObjectId(scribble_id)
                ).one()
    return scribble.image_data


@scribs.route('/page/<page_name>')
def return_overlay(page_name):
    # home = 'https://scrib-tresback.rhcloud.com'
    page_width = request.args.get('width')
    page_height = request.args.get('height')
    return render_template(page_name, home=HOME_URL, 
            page_width=page_width, page_height=page_height)


