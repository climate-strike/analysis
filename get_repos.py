import json
import time
import requests
import lxml.html
from tqdm import tqdm
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def get_repo(url):
    resp = requests.get('https://github.com{}'.format(url))
    html = lxml.html.fromstring(resp.content)
    stars = html.cssselect('.social-count')[1].text

    try:
        desc = html.cssselect('[itemprop=about]')[0].text.strip()
    except IndexError:
        desc = None

    tags = []
    for t in html.cssselect('.topic-tag'):
        tag = t.text.strip()
        tags.append(tag)

    return {
        'url': url,
        'tags': tags,
        'desc': desc,
        'stars': int(stars)
    }


repos = []
new_topics = set()
topics = open('topics.txt').read().splitlines()

driver = webdriver.Firefox()

seen = set()
bar = tqdm(topics)
for topic in bar:
    bar.set_description(topic)

    topic_url = 'https://github.com/topics/{}'.format(topic)
    driver.get(topic_url)
    time.sleep(2)

    try:
        while True:
            driver.find_element_by_css_selector('.ajax-pagination-btn').click()
            time.sleep(5)
    except NoSuchElementException:
        pass

    html = lxml.html.fromstring(driver.page_source)

    for repo in html.cssselect('article'):
        url = repo.cssselect('h1 a:last-child')[0].attrib['href']

        # Probably an issue, not a repo
        if url.count('/') > 2: continue

        # Already encountered
        if url in seen: continue

        repo = get_repo(url)
        for t in repo['tags']:
            if t not in topics:
                new_topics.add(t)
        repos.append(repo)
        seen.add(url)

terms = open('terms.txt').read().splitlines()
bar = tqdm(terms)
for term in bar:
    bar.set_description(term)
    page = 1
    while True:
        resp = requests.get('https://github.com/search', params={'q': term, 'p': page})

        html = lxml.html.fromstring(resp.content)
        results = html.cssselect('.repo-list-item')
        if not results:
            break

        for repo in results:
            url = repo.cssselect('a')[0].attrib['href']

            # Already encountered
            if url in seen: continue

            repo = get_repo(url)
            for t in repo['tags']:
                if t not in topics:
                    new_topics.add(t)
            repos.append(repo)
            seen.add(url)
        page += 1

print(len(repos), 'repos')

with open('data/repos.json', 'w') as f:
    json.dump(repos, f)

with open('data/new_topics.txt', 'w') as f:
    f.write('\n'.join(list(new_topics)))