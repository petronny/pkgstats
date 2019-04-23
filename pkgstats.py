#!/bin/python3
import os
import sys
import urllib.request
import urllib.parse
import json
import time
import datetime
import progressbar
sys.path.append(os.path.join(os.path.dirname(__file__), 'djangorm'))
import djangorm
from db.models import Cache

threshold = datetime.datetime.now() + datetime.timedelta(days=-7)

def search_online(pkgname):
    url = 'https://pkgstats.archlinux.de/package/datatables'
    length = 100
    params = {
            "draw": "1",
            "start": 0,
            "length": length,
            "search[value]": '%s' % pkgname
            }

    bar = progressbar.ProgressBar(max_value=1)
    bar.update(0)
    tmp_url = url + '?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(tmp_url).read().decode('utf-8')
    response = json.loads(response)
    bar.max_value = response['recordsFiltered']
    bar.update(len(response['data']))
    progressbar.streams.flush()
    for i in range(0, (response['recordsFiltered'] - 1) // length):
        time.sleep(1)
        params["start"] = (i + 1) * length
        tmp_url = url + '?' + urllib.parse.urlencode(params)
        tmp_response = urllib.request.urlopen(tmp_url, timeout=3).read().decode('utf-8')
        response['data'] += json.loads(tmp_response)['data']
        bar.update(len(response['data']))
    print()
    for i in response['data']:
        update_cache(i['pkgname'], i['count'], response['recordsTotal'])

    if pkgname != '':
        try:
            cache = Cache.objects.get(pkgname=pkgname)
        except:
            cache = Cache(pkgname=pkgname, total=search('pacman').total)
            cache.save()
        return cache
    return None

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

    try:
        pkgname = sys.argv[1]
    except:
        pkgname = ''

    #list_cache()

    result = search(pkgname)

    if result:
        print('%d / %d = %.2f%%' % (result.count, result.total, 100 * result.count / result.total))
