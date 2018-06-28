#!/usr/bin/env python
from multiprocessing import Pool
import os
import argparse
import logging
import urllib2
import urllib

from BeautifulSoup import BeautifulSoup

LOG = logging.getLogger(__name__)

def has_latest(url):
    '''If url has latest return latest url
    else return False
    '''
    for subFolder in get_sub_folders(url):
        if subFolder == "latest/":
            LOG.debug("Has latest: " + url)
            return True
    return False

def scrape_latest(tuple):
    url, output_path, tag = tuple
    output_path = os.path.join(output_path, tag)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for link in get_image_links(url):
        for i in range(10):
            try:
                with open(os.path.join(output_path, link), 'w') as f: f.write(urllib2.urlopen(url + link).read())
                LOG.debug(url + " - scraped: " + str(link))
                break
            except urllib2.URLError:
                LOG.critical("urlerror at: " + url + link)
                continue

def get_image_links(url):
    return [link for link in get_links(url) if link[-4:] == ".jpg"]

def get_sub_folders(url):
    subFolders = []
    for link in get_links(url):
        if link[-1] == '/' and link[0] != '/':
            subFolders.append(link)
    return subFolders

def get_links(url):
    links = []
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html)
    for a in soup.findAll('a'):
        links.append(a.get('href'))
    return links

def recursive_get_latest(url, output_path, tag):
    result = []
    LOG.info("recursive: " + url)
    subFolders = get_sub_folders(url)
    LOG.debug(url + " - sub folders: " + str(subFolders))
    if "latest/" in subFolders:
        result.append((url + "latest/", output_path, tag))
    else:
        for x in subFolders:
            result.extend(recursive_get_latest(url + x, os.path.join(output_path, x), tag))
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, nargs=1,
        help='Starting url')
    parser.add_argument('-v', '--verbose', action='count',
        help='Print more info')
    parser.add_argument('-o', '--output-path', type=str, default='./',
        help='Path to output directory')
    parser.add_argument('-t', '--tag', type=str, default='latest',
        help='Path to output directory')
    parser.add_argument('-p', '--processors', type=int, default=1,
        help='Number of processors to use')
    args = parser.parse_args()

    if args.verbose == None:
        logging_level = logging.WARNING
    elif args.verbose == 1:
        logging_level = logging.INFO
    else:
        logging_level = logging.DEBUG

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging_level)

    if args.processors > 0 :
        pool = Pool(processes=args.processors, maxtasksperchild=3)
        pool.map(scrape_latest, recursive_get_latest(args.url[0], args.output_path, args.tag))
    else:
        [scrape_latest(x) for x in recursive_get_latest(args.url[0], args.output_path, args.tag)]

class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

if __name__ == "__main__":
    main()