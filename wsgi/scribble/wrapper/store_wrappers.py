__author__ = 'tresback'

from bs4 import BeautifulSoup, Comment, Tag, NavigableString
import re
import urlparse

from scribble import HOME_URL


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
    print 'Tag is has base_url of %s' % base_url
    parsed = urlparse.urlparse(base_url)                    
    path = [res for res in parsed.path.split('/') if res]
    if "." in path[-1]:
        path.pop()
    # Attrs that would have a relative path
    tag_attr = dict(img='src', script='src', a='href',
                    link='href')
    attr = tag_attr.get(tag.name)
    if attr is not None:
        tag_val = tag.get(attr)
        print 'old url is %s' % path
        new_path = parse_path(path, tag_val, parsed)
        print 'old url is %s -- new url is %s' % (path, new_path)
        tag[attr] = str(new_path)
    if tag.get('style') is not None:
        # Must be something with a url() style reference
        def style_callb(match):
            rel_path = match.group(1).lstrip("'").rstrip("'")
            new_path = parse_path(path, rel_path, parsed)
            return "url('%s')" % new_path
        style_links = re.sub('url\((.*?)\)', style_callb,
                             tag.get('style'))
        tag['style'] = style_links
    print 'Tag has been replaced as %s' % tag
    return tag


def parse_path(path, tag_val, parsed):
    up_dirs = re.findall('\.\.\/', tag_val)

    print "PATH: %s" % path

    if up_dirs:
        for up in up_dirs:
            path.pop()
        path = modify_path(path, tag_val)
        path = urlparse.urlunsplit((parsed.scheme, 
                                       parsed.netloc,
                                       '/'.join(path), '', ''))
    elif re.findall(r'^(https:\/\/)', tag_val) or re.findall(r'^(http:\/\/)', tag_val) or \
        re.findall(r'^(\/\/)', tag_val):
        path = tag_val
    elif re.findall('\.\/', tag_val) or \
        re.findall(r'^(?!https:\/\/)', tag_val)  or \
        re.findall(r'^(?!http:\/\/)', tag_val):
        path = modify_path(path, tag_val)
        path = urlparse.urlunsplit((parsed.scheme, 
                                       parsed.netloc,
                                       '/'.join(path), '', ''))
    return path


def remove_scribble_elements(scribble_tag):
    for tag in scribble_tag:
        tag.extract()


def add_scribble_canvas(soup_obj, user_id, scribble_id):
    script_tag = Tag(soup_obj, name="script")
    script_tag['src'] = '//code.jquery.com/jquery-1.7.2.min.js'
    soup_obj.body.insert(-1, script_tag)
    script_tag = Tag(soup_obj, name="script")
    script_text = NavigableString("var BASEURL='%s'" % HOME_URL)
    script_tag.insert(0, script_text)
    soup_obj.body.insert(-1, script_tag)
    with open("scribble/static/js/load_canvas.js") as scribjs:
        script_tag = Tag(soup_obj, name="script")
        script_text = NavigableString(scribjs.read().format( user_id, scribble_id))
        script_tag.insert(0, script_text)
        soup_obj.body.insert(-1, script_tag)


def make_soup(base_html, base_url, user_id, scribble_id):
    print "making a soup object"
    soup = BeautifulSoup(base_html, "html.parser")    
    print "finding tags with URL references, %s" % soup
    ref_tags = [modify_rels(tag, base_url) 
                    for tag  in soup.find_all() 
                        if find_all_ref_tags(tag)]
    print "removing scribble elements"
    remove_scribble_elements(soup.find_all(id=
                                'base_actions'))
    remove_scribble_elements(soup.find_all('script')) 
    print "finding all comments"
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    add_scribble_canvas(soup, user_id, scribble_id)
    print "converting to unicode and return"
    return unicode(soup)

