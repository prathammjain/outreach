import re

with open('index.html', 'r') as f:
    content = f.read()

# 1. Update CSS variables in :root
content = re.sub(r'--bg: #050505;', r'--bg: #FAFAF7;', content)
content = re.sub(r'--surface: #0f0f0f;', r'--surface: #FFFFFF;', content)
content = re.sub(r'--surface-2: #141414;', r'--surface-2: #F3F1EA;', content)
content = re.sub(r'--surface-hover: #161616;', r'--surface-hover: #F0EEE5;', content)
content = re.sub(r'--border: rgba\(255, 255, 255, 0\.07\);', r'--border: rgba(0, 0, 0, 0.08);', content)
content = re.sub(r'--border-bright: rgba\(255, 255, 255, 0\.14\);', r'--border-bright: rgba(0, 0, 0, 0.15);', content)
content = re.sub(r'--text-primary: #f1f5f9;', r'--text-primary: #2C2A28;', content)
content = re.sub(r'--text-secondary: #8b99ae;', r'--text-secondary: #6B655F;', content)
content = re.sub(r'--text-muted: #555e6d;', r'--text-muted: #9C968F;', content)
content = re.sub(r'--accent: #00e57a;', r'--accent: #C29B4A;', content)
content = re.sub(r'--accent-glow: rgba\(0, 229, 122, 0\.12\);', r'--accent-glow: rgba(194, 155, 74, 0.12);', content)
content = re.sub(r'--accent-dim: #00b860;', r'--accent-dim: #A8863D;', content)
content = re.sub(r'--glass: rgba\(255, 255, 255, 0\.028\);', r'--glass: rgba(255, 255, 255, 0.6);', content)
content = re.sub(r'--glass-border: rgba\(255, 255, 255, 0\.055\);', r'--glass-border: rgba(0, 0, 0, 0.05);', content)

# 2. Update hardcoded colors based on the dark theme
content = content.replace('rgba(0, 229, 122', 'rgba(194, 155, 74')
content = content.replace('rgba(0,229,122', 'rgba(194,155,74')
content = content.replace('#14f090', '#DAB059')  # hover accent
content = content.replace('#00e57a', '#C29B4A')
content = content.replace('#50ffb4', '#E6C983')
content = content.replace('rgba(255, 255, 255, 0.022)', 'rgba(0, 0, 0, 0.03)')
content = content.replace('rgba(255,255,255,0.035)', 'rgba(0,0,0,0.04)')
content = content.replace('rgba(255,255,255,0.018)', 'rgba(0,0,0,0.02)')
content = content.replace('rgba(255,255,255,0.12)', 'rgba(0,0,0,0.12)')

# Replace hardcoded whites and dark bits
content = content.replace('color: #fff;', 'color: var(--text-primary);')
content = content.replace('color: #ffffff;', 'color: var(--text-primary);')
content = content.replace('background: rgba(5, 5, 5, 0.82)', 'background: rgba(250, 250, 247, 0.82)')
content = content.replace('color: #020d06;', 'color: #FFFFFF;') # Buttons text changed to white
content = content.replace('background: #0f0f0f', 'background: #FFFFFF')
content = content.replace('background: #161616', 'background: #F3F1EA')
content = content.replace('rgba(0,0,0,0.94)', 'rgba(250,250,247,0.94)')
content = content.replace('rgba(0,0,0,0.96)', 'rgba(250,250,247,0.96)')
content = content.replace('rgba(0,0,0,0.7)', 'rgba(0,0,0,0.1)') # shadows
content = content.replace('rgba(0,0,0,0.45)', 'rgba(0,0,0,0.08)')
content = content.replace('rgba(0, 0, 0, 0.5)', 'rgba(0, 0, 0, 0.08)')

# Specifically for the gradient text in h1
content = re.sub(r'background: linear-gradient\(135deg, #e2fdf0 20%, var\(--accent\) 75%\);',
                 r'background: linear-gradient(135deg, #A8863D 20%, #E6C983 75%);', content)

# Remove the inverted logo check or update it
content = content.replace('color: #e2fdf0', 'color: #332B1A')
content = content.replace('#8b99ae', '#6B655F')
content = content.replace('#ff6b81', '#D44D5C')
content = content.replace('color: #3a404a;', 'color: #8A837A;')
content = content.replace('color: #555e6d;', 'color: #9C968F;')

with open('index.html', 'w') as f:
    f.write(content)
print("done")
