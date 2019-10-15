import json
import matplotlib.pyplot as plt
from collections import defaultdict

plt.style.use('ggplot')

with open('data/repos.json', 'r') as f:
    repos = json.load(f)

html = []

html.append('''
    <style>
        body {
            font-family: monospace;
        }
    </style>
''')
html.append('<h1>{} repos</h1>'.format(len(repos)))

dep_counts = defaultdict(int)
no_deps = 0
for repo in repos:
    deps = set(repo['dependencies'])
    if not deps:
        no_deps += 1
    for dep in deps:
        dep_counts[dep] += 1

html.append('<h2>{} repos missing dependencies</h2>'.format(no_deps))

all_deps = sorted(dep_counts.items(), key=lambda e: e[1], reverse=True)
html.append('<ul style="columns:20em;">{}</ul>'.format('\n'.join('<li>{} ({})</li>'.format(dep, count) for dep, count in all_deps)))

html.append('<hr />')

no_deps = []
for repo in sorted(repos, key=lambda r: r['stars'], reverse=True):
    if repo['dependencies']:
        html.append('''
                    <div style="margin:2em 0 0 0;padding:2em 0 0 0;border-top: 1px solid blue;">
                        <h3><a href="https://github.com{url}">{url}</a> ({stars} stars)</h3>
                        <h4>{tags}</h4>
                        <p>{desc}</p>
                        <ul style="columns:20em;">{deps}</ul>
                    </div>
                    '''.format(url=repo['url'],
                            stars=repo['stars'],
                            tags=', '.join(repo['tags']),
                            desc=repo['desc'] or '',
                            deps='\n'.join('<li>{}</li>'.format(dep) for dep in set(repo['dependencies']))))
    else:
        no_deps.append(repo)

html.append('<h1 style="margin-top:2em;padding-top:1em;border-top: 1px solid blue;">Missing dependencies</h1>')
html.append('<ul style="columns:20em;">{}</ul>'.format(
    '\n'.join('<li><a href="https://github.com{url}">{url}</a></li>'.format(url=r['url']) for r in no_deps)))

plt.title('Repo dependency distribution')
plt.hist(dep_counts.values(), bins=100)
plt.savefig('results/dist.png')
# plt.show()

html.append('<img src="dist.png">')

with open('results/index.html', 'w') as f:
    f.write('\n'.join(html))