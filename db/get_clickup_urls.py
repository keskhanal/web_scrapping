import requests
import re
import sys
from requests_oauthlib import OAuth2Session

list_id = "900700126495"
url = f"https://api.clickup.com/api/v2/list/{list_id}/task"

def get_tasks(list_id, page, api_key):
    headers = {
        "Authorization": api_key
    }
    params = {"page": page, "include_closed": True}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    print(data.keys())
    if 'last_page' in data or len(data['tasks']) == 0:
        return data["tasks"], True
    else:
        return data['tasks'], False 

def extract_url(task, subdomain):
    pattern = re.compile(r'https?://[^\s]+')
    if task['description']:
        urls = re.findall(pattern, task["description"])
        for url in urls:
            if subdomain in url:
                return url
    else:
        print('none')
    return None


api_key = 'pk_61321102_WW1QOVC4KG9D50RJ9WTKJ5YUECR9U3LG'
tasks = []
page = 0
while True:
    page_tasks, last_page = get_tasks(list_id, page, api_key)
    tasks += page_tasks
    print(f"{last_page} {len(tasks)} {page}")
    if last_page:
        break
    page += 1

subdomain = sys.argv[1]
f = open(f'{subdomain}.txt', 'w')

for task in tasks:
    url = extract_url(task, subdomain)
    if url:
        f.write(f'{task["id"]}|{url}\n')
        print(task["name"], ":", url)