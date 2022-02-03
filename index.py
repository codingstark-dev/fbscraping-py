import sys
import argparse
import urllib.request
from flask import Flask, request
from re import search
import requests

app = Flask(__name__)


@app.route('/', methods=("GET", "POST"), strict_slashes=False)
def home():
    fburl = request.args.get("url")
    print("here", fburl)

    if fburl is None:
        return "No URL provided"
    if fburl == None:
        return "No URL", 500
    if search(r"^https?://(www\.)?facebook\.com/", fburl) or search(r"fb.watch/([a-zA-Z0-9]+)/", fburl):
        pass
    else:
        return "Invalid Fb URL", 500
    if search(r"fb.watch/([a-zA-Z0-9]+)/", fburl):
        site = requests.get("https://" + fburl)
        print(site.url)
        fburl = site.url

    def xpartition(bigstr, sep1, sep2):
        x = bigstr.partition(sep1)
        y = x[2].partition(sep2)
        return y[0]

    # fb_parse = argparse.ArgumentParser(
    #     prog='FBVids', description="This script downloads Facebook videos.")
    # fb_parse.add_argument('userurl', help='URL of the FB video.')
    # argsobj = fb_parse.parse_args()
    # userurl = argsobj.userurl

    if('facebook.com/' in fburl):
        cleanurl = 'https://facebook.com/' + \
            fburl.rpartition('facebook.com/')[2]
    else:
        raise ValueError('Check URL.')

    fbsrc = urllib.request.Request(cleanurl, headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "DNT": "1", "Sec-Fetch-Dest": "document",
                                                      "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "cross-site", "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"})
    with urllib.request.urlopen(fbsrc) as fbdata1:
        fbstr1 = str(fbdata1.read())
    # print(fbstr1)
    try:
        fbstr1.index('playable_url')
    except ValueError:
        print('Check URL.')

    mediastr = xpartition(fbstr1, '"playable_url":',
                          ',"spherical_video_fallback_urls')
    # print(mediastr)
    medialist = mediastr.split('"')
    if (':null' in medialist) or ('_nc_vs' in medialist[5]):
        vidurl = medialist[1].replace('\\', '')
    else:
        vidurl = medialist[5].replace('\\', '')
    print(vidurl)
    filename = xpartition(vidurl, '/', '?')
    return {"url": vidurl}


# vidreq = urllib.request.Request(vidurl, headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "DNT": "1", "Sec-Fetch-Dest": "document",
#                                 "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "cross-site", "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"})
# # with urllib.request.urlopen(vidreq) as vidobj:
#     vidata = vidobj.read()
# with open(filename, 'wb') as vid:
#     vid.write(vidata)

def resolve_url(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        return (url, None)

    if r.status_code != 200:
        longurl = None
    else:
        longurl = r.url

    return (url, longurl)


if __name__ == '__main__':
    app.run(debug=True)
