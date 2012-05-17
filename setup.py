from setuptools import setup

reqs_list = list()
with open('requirements.txt', 'r') as reqs:
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
