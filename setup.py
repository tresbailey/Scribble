from setuptools import setup

fn = os.path.join(os.path.dirname(__file__), 'requirements.txt')
reqs_list = list()
with open(fn, 'r') as reqs:
    for line in reqs.readlines():
        reqs_list.append(line)


setup(name='YourAppName',
      version='1.0',
      description='OpenShift App',
      author='Your Name',
      author_email='example@example.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=reqs_list,
     )
