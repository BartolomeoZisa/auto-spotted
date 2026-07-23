import os

# Set dummy environment variables to bypass main's top-level checks
os.environ.setdefault("SHEET_CSV_URL", "dummy")
os.environ.setdefault("GEMINI_API_KEY", "dummy")
os.environ.setdefault("META_ACCESS_TOKEN", "dummy")
os.environ.setdefault("IG_USER_ID", "dummy")
os.environ.setdefault("IMAGE_URL", "dummy")

from main import generate_image

generate_image(
    "Spotted: Someone drinking coffee in the library looking very productive.",
    output_path="latest_post.jpg",
)

print("✅ Image generated successfully! Check 'latest_post.jpg'.")