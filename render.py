import json
from collections import defaultdict

with open('repos.json', 'r') as f:
    repos = json.load(f)

html = []

html.append('<h1>{} repos</h1>'.format(len(repos)))

all_deps = defaultdict(int)
for repo in repos:
    for dep in set(repo['dependencies']):
        all_deps[dep] += 1

all_deps = sorted(all_deps.items(), key=lambda e: e[1], reverse=True)
html.append('<ul>{}</ul>'.format('\n'.join('<li>{} : {}</li>'.format(dep, count) for dep, count in all_deps)))

html.append('<hr />')

for repo in repos:
    html.append('''
                <h3>{url} ({stars} stars)</h3>
                <h4>{tags}</h4>
                <p>{desc}</p>
                <ul>{deps}</ul>
                '''.format(url=repo['url'],
                           stars=repo['stars'],
                           tags=', '.join(repo['tags']),
                           desc=repo['desc'] or '',
                           deps='\n'.join('<li>{}</li>'.format(dep) for dep in repo['dependencies'])))


with open('index.html', 'w') as f:
    f.write('\n'.join(html))