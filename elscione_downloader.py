# https://github.com/Anteicodes/h5ai-downloader

# python elscione_downloader.py --worker=5 --dest=./elscione --url=https://server.elscione.com/

import os
import argparse
import requests
import urllib.parse

from concurrent.futures import ThreadPoolExecutor

folder_skipping = []

arg = argparse.ArgumentParser()
arg.add_argument('--worker', type=int, default=3, help='Deafult Worker 3')
arg.add_argument('--dest', type=str, default=os.getcwd(), help='Default Dest Path' + os.getcwd())
arg.add_argument('--url', type=str, required=True)
woke = arg.parse_args()

worker = woke.worker
dest = woke.dest.strip('/') + '/'
BASE_URL = woke.url

def createfolder(fn: str):
    tree = fn.strip('/').split('/')
    for i, n in enumerate(tree, 1):
        folder_path = dest + '/'.join(tree[:i])
        if os.path.isdir(folder_path):
            continue
        os.makedirs(folder_path)

def download(url, path):
    if os.path.isfile(path):
        return False
    
    req = requests.get(url, headers={'Referer': 'https://server.elscione.com/', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}, stream=True)

    with open(path, 'wb') as file:
        for iter in req.iter_content(1024):
            file.write(iter)
        print(f'{path} downloaded')
          
def get_items(path):
    global folder_skipping
    with ThreadPoolExecutor(max_workers=worker) as th:
        response = requests.post(BASE_URL + '?', json={'action': 'get', 'items': {'what': 1, 'href': path}}).json()
        items = response['items'][1:]
        for item in items:
            item_href_decoded = urllib.parse.unquote(item['href'])
            if item_href_decoded.startswith('/Officially Translated Light Novels/'):
                if not item_href_decoded.endswith('/'):
                    if item_href_decoded.endswith('.epub'):
                        file_url = BASE_URL + item['href'][1:]
                        print(f'downloading {file_url}')
                        th.submit(download, file_url, dest + item_href_decoded[1:])
                else: 
                    folder_href = item_href_decoded
                    tree = folder_href.strip('/').split('/')
                    for i, folder in enumerate(tree, 1):
                        if i == 1:
                            continue 
                        # parent_folder_path = dest + '/'.join(tree[:i-1])
                        parent_folder_name = tree[i-2]
                        if parent_folder_name.startswith('!') and '!Side Stories' not in folder_href:
                            print(f'Skipping folder {folder_href}')
                            break 
                    else:
                        if folder_href not in folder_skipping:
                            folder_skipping.append(folder_href)
                            print(f'create folder {folder_href}')
                            createfolder(folder_href.strip('/'))
                            get_items(folder_href)

get_items('/')
