import requests


def download(path, url):
    r = requests.get(url)
    with open(path, 'wb') as f:
        f.write(r.content)
