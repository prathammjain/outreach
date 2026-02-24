import re

with open('index.html', 'r') as f:
    html = f.read()

# Replace Outfit with Inter for a unified, clean sans-serif look
html = html.replace("font-family: 'Outfit', sans-serif;", "font-family: 'Inter', sans-serif;")

# Lower the font weights globally
html = html.replace("font-weight: 800;", "font-weight: 400;")
html = html.replace("font-weight: 700;", "font-weight: 400;")
html = html.replace("font-weight: 600;", "font-weight: 400;")
html = html.replace("font-weight: 500;", "font-weight: 300;")

# Make h1 specifically 300 weight
html = re.sub(r'(h1\s*\{[^}]*font-weight:\s*)400(;\s*)', r'\g<1>300\g<2>', html)

# Remove the gradient text to match the minimalist pure text aesthetic in the image
old_gradient_css = """        .gradient-text {
            background: linear-gradient(135deg, #617467 20%, #A8BDB0 75%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }"""
new_gradient_css = """        .gradient-text {
            color: var(--text-primary);
            font-weight: 300;
        }"""
html = html.replace(old_gradient_css, new_gradient_css)

with open('index.html', 'w') as f:
    f.write(html)
