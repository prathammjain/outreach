with open('index.html', 'r') as f:
    content = f.read()

# Update the main backgrounds
content = content.replace('--bg: #FAFAF7;', '--bg: #DDD0C8;')
content = content.replace('--surface: #FFFFFF;', '--surface: #EEDDDB;') # slightly lighter/different
content = content.replace('--surface-2: #F3F1EA;', '--surface-2: #E1D2CB;')
content = content.replace('--surface-hover: #F0EEE5;', '--surface-hover: #E8D8D3;')

# Update text colors
content = content.replace('--text-primary: #2C2A28;', '--text-primary: #323232;')
content = content.replace('--text-secondary: #6B655F;', '--text-secondary: #4A4A4A;')
content = content.replace('--text-muted: #9C968F;', '--text-muted: #626262;')

# Replace the hardcoded background rgba values: #DDD0C8 is rgb(221, 208, 200)
content = content.replace('rgba(250, 250, 247', 'rgba(221, 208, 200')
content = content.replace('rgba(250,250,247', 'rgba(221, 208, 200')

# Replace the hardcoded #FFFFFF surface backgrounds with #EEDDDB
content = content.replace('#FFFFFF', '#EEDDDB')

# For the buttons and elements that need white text, replace them back
content = content.replace('color: #EEDDDB;', 'color: #FFFFFF;')

with open('index.html', 'w') as f:
    f.write(content)
