#!/bin/python3
import os
import sys
import urllib.request
import urllib.parse
import json
import time
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'djangorm'))
import djangorm
from db.models import Cache

threshold = datetime.datetime.now() + datetime.timedelta(days=-7)

def search_online(pkgname):
    url = 'https://pkgstats.archlinux.de/api/packages/%s/series' % pkgname
    #params = {'startMonth': 201901, 'endMonth': 201901}
    #url = url + '?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(url).read().decode('utf-8')
    response = json.loads(response)['packagePopularities']
    if len(response) == 0:
        update_cache(pkgname, 0, search('pacman').total)
    else:
        response = response[0]
        update_cache(response['name'], response['count'], response['samples'])
    cache = Cache.objects.get(pkgname=pkgname)
    return cache

def update_cache(pkgname, count, total):
    try:
        cache = Cache.objects.get(pkgname=pkgname)
        cache.count = count
        cache.total = total
    except:
        cache = Cache(pkgname=pkgname, count=count, total=total)
    cache.save()

def list_cache():
    for cache in Cache.objects.all():
        print(djangorm.object_to_dict(cache))

def search(pkgname, force_online=False):
    try:
        assert not force_online
        cache = Cache.objects.get(pkgname=pkgname, timestamp__gte=threshold)
    except:
        cache = search_online(pkgname)
    return cache

if __name__ == '__main__':
    djangorm.migrate()

    pkgname = sys.argv[1]

    if len(sys.argv) < 2:
        print('Usage:\tpython pkgstats.py [pkgname]')
        sys.exit()

    #list_cache()

    result = search(pkgname, True)

    if result:
        print('%d / %d = %.2f%%' % (result.count, result.total, 100 * result.count / result.total))
