#!/usr/bin/env python
import parallel
import threading
import os
import argparse
import logging
import urllib2
import ssl
import requests
import shutil
from io import BytesIO

from BeautifulSoup import BeautifulSoup

LOG = logging.getLogger(__name__)

def scrape_link(tuple, terminal=10):
    url, args = tuple
    try:
        response = requests.get(url, stream=False, timeout=30)
        if response.headers['content-type'] != 'image/jpeg':
            print response.headers['content-type']
            raise Exception('Not jpeg')
        image = BytesIO(
            response.content)
        with open(os.path.join(args.output_path, os.path.basename(url)), 'w') as f:
            shutil.copyfileobj(image, f)
    except Exception, e:
        if terminal is 0:
            LOG.critical(str(e) + " at: " + url)
            return
        else:
            scrape_link(tuple, terminal=terminal-1)

def get_image_links(url, terminal=10):
    result = [(os.path.join(url, link)) for link in get_links(url) if link[-4:] == ".jpg"]
    if len(result) is 0:
        return get_image_links(url, terminal=terminal-1)
    else:
        return result

def get_links(url):
    links = []
    print url
    html = requests.get(url).content
	
    soup = BeautifulSoup(html)
    for a in soup.findAll('a'):
        links.append(a.get('href'))
    return links

def has_latest(url):
    '''If url has latest return latest url
    else return False
    '''
    for subFolder in get_sub_folders(url):
        if subFolder == "latest/":
            LOG.debug("Has latest: " + url)
            return True
    return False

def get_sub_folders(url):
    subFolders = []
    for link in get_links(url):
        if link[-1] == '/' and link[0] != '/':
            subFolders.append(link)
    return subFolders

def recursive_get_latest(url):
    result = []
    LOG.info("recursive: " + url)
    subFolders = get_sub_folders(url)
    LOG.debug(url + " - sub folders: " + str(subFolders))
    if "latest/" in subFolders:
        result.append((os.path.join(url,"latest/")))
    else:
        for x in subFolders:
            result.extend(recursive_get_latest(url + x))
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str,
        help='Starting url')
    parser.add_argument('-v', '--verbose', action='count',
        help='Print more info')
    parser.add_argument('-o', '--output_path', type=str, default='', nargs='?',
        help='Path to output directory')
    parser.add_argument('-c', '--check_path', type=str, default='', nargs='?',
        help='Path to existing files')
    parser.add_argument('-p', '--processors', type=int, default=0,
        help='If set to 1 web requests will be multiprocessed')
    parser.add_argument('-r', '--recursive', nargs='?', const=True, default=False,
        help='If set will recursively search link')
    parser.add_argument('--replace', nargs='?', const=True, default=False,
        help='If set will not check for duplicates')
    args = parser.parse_args()

    if args.verbose == None:
        logging_level = logging.WARNING
    elif args.verbose == 1:
        logging_level = logging.INFO
    else:
        logging_level = logging.DEBUG

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging_level)

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    if args.recursive:
        latest = recursive_get_latest(args.input)
        latest_image_links = [(url, args) for l in latest for url in get_image_links(l)
            if args.replace or not os.path.isfile(os.path.join(args.check_path, os.path.basename(url)))]
    else:
        latest_image_links = [(url, args) for url in get_image_links(args.input)
            if args.replace or not os.path.isfile(os.path.join(args.check_path, os.path.basename(url)))]

    if args.processors > 0:
        parallel.task_mapper(scrape_link, latest_image_links, parallel_procs=args.processors)
    else:
        map(scrape_link, latest_image_links)

if __name__ == "__main__":
    main()