from setuptools import setup
import os

"""
fn = os.path.join(os.path.dirname(__file__), 'requirements.txt')
reqs_list = list()
with open(fn, 'r') as reqs:
    for line in reqs.readlines():
        reqs_list.append(line)
"""

setup(name='WriteOwn', version='1.0',
      description='OpenShift Python-2.7 Community Cartridge based application',
      author='Your Name', author_email='ramr@example.org',
      url='http://www.python.org/sigs/distutils-sig/',

      #  Uncomment one or more lines below in the install_requires section
      #  for the specific client drivers/modules your application needs.
      install_requires=[ 'Flask==0.8', 'MongoAlchemy==0.11',
        'Werkzeug==0.8.3', 'Flask-Login==0.2.7', 'Flask-OpenId==1.1.1',
        'pymongo==2.1.1', 'python-dateutil==1.5', 
        'redis==2.4.11', 'simplejson==2.1.6', 
        'wsgiref==0.1.2', 'Flask-Principal==0.4.0',
        'Flask-MongoAlchemy==0.5.3', 'flask_oauth==0.12',
        'Jinja2==2.6', 'Pillow==9.0.1', 'amqp==1.0.13',
        'anyjson==0.3.3', 'beautifulsoup4==4.0.5', 
        'billiard==2.7.3.34', 'celery==3.0.24', 'certifi==0.0.8',
        'chardet==2.1.1', 'httplib2==0.7.4', 'kombu==2.5.15',
        'lxml==2.3.4', 'nose==1.0.0', 'requests==0.11.1', 
        'selenium==2.33.0', 'six==1.3.0']
     )

