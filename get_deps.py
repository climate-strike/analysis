import json
import time
import lxml.html
from tqdm import tqdm
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


driver = webdriver.Firefox()

def get_deps(repo):
    url = 'https://github.com{}/network/dependencies'.format(repo)
    driver.get(url)
    time.sleep(2)

    try:
        while True:
            driver.find_element_by_css_selector('#dependencies .ajax-pagination-btn').click()
            time.sleep(5)
    except NoSuchElementException:
        pass

    html = lxml.html.fromstring(driver.page_source)
    deps = [a.attrib['href'] for a in html.cssselect('#dependencies .js-dependency [data-octo-click=dep_graph_package]')]
    return deps

with open('data/repos.json', 'r') as f:
    repos = json.load(f)

for i, repo in tqdm(enumerate(repos)):
    if 'dependencies' in repo: continue
    url = repo['url']
    deps = get_deps(url)
    repo['dependencies'] = deps
    if i % 10 == 0:
        with open('data/repos.json', 'w') as f:
            json.dump(repos, f)

with open('data/repos.json', 'w') as f:
    json.dump(repos, f)

driver.close()
