import re

with open('terms.html', 'r') as f:
    html = f.read()

# CSS variable replacements
html = html.replace('--bg: #050505;', '--bg: #DDD0C8;')
html = html.replace('--surface: #0f0f0f;', '--surface: #EEDDDB;')
html = html.replace('--border: rgba(255, 255, 255, 0.08);', '--border: rgba(0, 0, 0, 0.08);')
html = html.replace('--border-bright: rgba(255, 255, 255, 0.15);', '--border-bright: rgba(0, 0, 0, 0.15);')
html = html.replace('--text-primary: #ffffff;', '--text-primary: #323232;')
html = html.replace('--text-secondary: #94a3b8;', '--text-secondary: #4A4A4A;')
html = html.replace('--accent: #00ff88;', '--accent: #7C9082;')
html = html.replace('--accent-glow: rgba(0, 255, 136, 0.15);', '--accent-glow: rgba(124, 144, 130, 0.15);')
html = html.replace('--glass: rgba(255, 255, 255, 0.03);', '--glass: rgba(255, 255, 255, 0.6);')
html = html.replace('--glass-border: rgba(255, 255, 255, 0.06);', '--glass-border: rgba(0, 0, 0, 0.05);')

# Font replacements
html = html.replace("font-family: 'Outfit', sans-serif;", "font-family: 'Inter', sans-serif;")
html = html.replace("font-weight: 800;", "font-weight: 400;")
html = html.replace("font-weight: 700;", "font-weight: 400;")
html = html.replace("font-weight: 600;", "font-weight: 400;")
html = html.replace("font-weight: 500;", "font-weight: 300;")
html = re.sub(r'(h1\s*\{[^}]*font-weight:\s*)400(;\s*)', r'\g<1>300\g<2>', html)

# Hardcoded rgba/hex replacements
html = html.replace('rgba(0, 255, 136', 'rgba(124, 144, 130')
html = html.replace('rgba(255, 255, 255, 0.025)', 'rgba(0, 0, 0, 0.03)')
html = html.replace('rgba(5, 5, 5, 0.8)', 'rgba(221, 208, 200, 0.82)')
html = html.replace('#50ffb4', '#94A89A')
html = html.replace('color: #444;', 'color: #8A837A;')

with open('terms.html', 'w') as f:
    f.write(html)
