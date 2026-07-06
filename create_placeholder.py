import os
from PIL import Image, ImageDraw, ImageFont

# Ensure directory exists
os.makedirs('app/static/images', exist_ok=True)

# Create a placeholder image
img = Image.new('RGB', (200, 200), color='#1a3a6b')
d = ImageDraw.Draw(img)

# Draw text
d.text((40, 85), 'No Image', fill='#c9a227')

# Save the image
img.save('app/static/images/placeholder.jpg')

print("✅ Placeholder image created successfully!")