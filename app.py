import sys
import argparse
import urllib.request
from flask import Flask, request
from re import search
import requests
app = Flask(__name__)


url = "https://fbdownloader.online/api/analyze"


headers = {
    "authority": "fbdownloader.online",
    "method": "POST",
    "path": "/api/analyze",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-IN,en;q=0.9,ja;q=0.8,en-US;q=0.7",
    "content-type": "application/json;charset=UTF-8",
    "cookie": "i18n_fb=en; __atuvc=1%7C12; _ga=GA1.2.1675180035.1647859875; _gid=GA1.2.2065770898.1647859875",
    "dnt": "1",
    "origin": "https://fbdownloader.online",
    "referer": "https://fbdownloader.online/",
    "sec-ch-ua": "' Not A Brand';v='99', 'Chromium';v='99', 'Google Chrome';v='99'",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "'Windows';v='5.1', 'Mac OS X';v='10.14', 'Linux';v='4.4'",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
}


@app.route('/', methods=("GET", "POST"), strict_slashes=False)
def home():
    fburl = request.args.get("url")
    print(fburl)
    if fburl.__contains__("reel"):
        spiltreels = fburl.split("/")[4]
        fburl = 'https://www.facebook.com/' + spiltreels
    else:
        fburl = fburl
    payload = {"q": fburl}
    # create regex parttern of this url  https://m.facebook.com/watch/?v=1068216013712168&ref=sharing
    response = requests.request(
        "POST", url, json=payload, headers=headers).json()
    if response["code"] == 200:
        if response['resource'].__contains__('hd'):
            return {"video": response['resource']['hd']}
        else:
            return {"video": response['resource']['sd']}
    else:
        # https://m.facebook.com/watch/?v=1068216013712168&ref=sharing
        # https://www.facebook.com/watch/?v=1068216013712168&ref=share
        # https://www.facebook.com/watch/?v=1068216013712168&ref=share

        if fburl is None:
            return "No URL provided"
        if fburl == None:
            return "No URL", 500
        if search(r"^https?://(www\.)?facebook\.com/", fburl) or search(r"fb.watch/([a-zA-Z0-9]+)/", fburl) or search(r"^https?://(m\.)?facebook\.com/", fburl):
            pass
        else:
            return "Invalid Fb URL", 500
        if search(r"fb.watch/([a-zA-Z0-9]+)/", fburl):
            if fburl.startswith("https://"):
                site = requests.get(fburl)
                fburl = site.url
            else:
                site = requests.get("https://" + fburl)
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
        # filename = xpartition(vidurl, '/', '?')
        return {"video": vidurl}


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


# print(resolve_url('https://m.facebook.com/story.php?story_fbid=5004822856207850&id=100076447896070&m_entstream_source=video_home&player_suborigin=feed&player_format=permalink'))
if __name__ == '__main__':
    app.run(debug=True)
