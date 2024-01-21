#!/usr/bin/env python3

import json
import requests
import os
from tqdm import tqdm

def get_all_episode_links():
    url1 = "https://psapi.nrk.no/radio/catalog/podcast/radioresepsjonen/episodes?page=" 
    url2 = "&pageSize=50&sort=asc"
    page = 1
    episodes = []
    episode_count = 0
    while (True):
        url = url1 + str(page) + url2
        json_obj = json.loads(requests.get(url).text)
        episode_info = json_obj['_embedded']['episodes']
        if (episode_info == []):
            break;
        for episode in episode_info:
            playback_url = "https://psapi.nrk.no/playback/manifest/podcast/" + episode['episodeId']
            playback_json = json.loads(requests.get(playback_url).text)
            mp3_url = playback_json['playable']['assets'][0]['url']
            date = playback_json['availability']['onDemand']['from'].split('T')[0]
            title = episode['titles']['title']
            title = ''.join([i for i in title if not i.isdigit() and i != '.'])
            title = title.strip().replace(' ', '_')
            title = date + '_' + title
            episodes.append({'title': title, 'url': mp3_url, 'year': date.split('-')[0]})
            episode_count += 1
            if (episode_count % 50 == 0):
                print("Processed", episode_count, "episodes")
        page += 1
    return episodes

def create_folders(episodes, root_dir):
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    
    created = {}
    
    for e in episodes:
        if not e['year'] in created:
            year_dir = os.path.join(root_dir, e['year'])
            if not os.path.exists(year_dir):
                os.mkdir(year_dir)
            created[e['year']] = True

def download_files(episodes, root_dir):
    for e in (pbar := tqdm(episodes)):
        pbar.set_postfix_str(e['title'])
        dl_request = requests.get(e['url'])
        with open(os.path.join(root_dir, e['year'], e['title'] + '.mp3'), 'wb') as f:
            f.write(dl_request.content)

if __name__ == '__main__':
    root_dir = 'Radioresepsjonen'
    
    print("Collecting episode data")
    episodes = get_all_episode_links()
    print("Found", len(episodes), " episodes")
    create_folders(episodes, root_dir)
    print("Start download")
    download_files(episodes, root_dir)
    print("Done")
