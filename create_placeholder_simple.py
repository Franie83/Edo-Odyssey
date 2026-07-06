import os
import base64

# Simple SVG placeholder
svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <rect width="200" height="200" fill="#1a3a6b"/>
  <text x="100" y="110" font-family="Arial" font-size="20" fill="#c9a227" text-anchor="middle">No Image</text>
</svg>'''

# Create directory
os.makedirs('app/static/images', exist_ok=True)

# Save as SVG
with open('app/static/images/placeholder.svg', 'w') as f:
    f.write(svg)

# Create a simple HTML placeholder that can be used as image
html = '''<!DOCTYPE html>
<html>
<head><style>body{margin:0;background:#1a3a6b;display:flex;justify-content:center;align-items:center;height:200px;font-family:Arial;color:#c9a227;font-size:20px;}</style></head>
<body>No Image</body>
</html>'''
with open('app/static/images/placeholder.html', 'w') as f:
    f.write(html)

print("✅ Placeholder files created")