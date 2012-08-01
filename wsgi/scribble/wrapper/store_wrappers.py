__author__ = 'tresback'

from bs4 import BeautifulSoup, Comment, Tag
import re
import urlparse


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
    print "making a soup object"
    soup = BeautifulSoup(base_html, "html.parser")    
    print "finding tags with URL references, %s" % soup
    ref_tags = [modify_rels(tag, base_url) 
                    for tag  in soup.find_all() 
                        if find_all_ref_tags(tag)]
    print "removing scribble elements"
    #remove_scribble_elements(soup.find_all(id=
    #                            'scribble_overlay'))
    remove_scribble_elements(soup.find_all('script')) 
    print "finding all comments"
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    print "creating new tags"
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
    print "inserting new tags"
    soup.body.insert(0, new_script)
    print "converting to unicode and return"
    return unicode(soup)

