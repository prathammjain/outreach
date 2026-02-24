content = open('index.html').read()
content = content.replace('#C29B4A', '#7C9082')
content = content.replace('rgba(194, 155, 74', 'rgba(124, 144, 130')
content = content.replace('rgba(194,155,74', 'rgba(124,144,130')
content = content.replace('#A8863D', '#617467')
content = content.replace('#E6C983', '#A8BDB0')
content = content.replace('#DAB059', '#94A89A')
with open('index.html', 'w') as f:
    f.write(content)
