import scribble
from bs4 import BeautifulSoup

def test_modify_rels():
    BeautifulSoup('<html><body><script src="http://google.com"/></body></html>')

