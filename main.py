import os
import io
import json
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# CONFIGURATION & ENVIRONMENT SECRETS
# ---------------------------------------------------------------------------
SHEET_CSV_URL = os.environ["SHEET_CSV_URL"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]
IMAGE_URL = os.environ["IMAGE_URL"] # Public gh-pages image link

# ---------------------------------------------------------------------------
# STEP 1: READ SUBMISSIONS FROM GOOGLE SHEET CSV EXPORT
# ---------------------------------------------------------------------------
def get_pending_submission():
    print("Fetching submissions from Google Sheet...")
    df = pd.read_csv(SHEET_CSV_URL)
    
    # Assumes your sheet has a 'Status' column and a 'Submission' column
    pending = df[df['Status'] == 'Pending']
    
    if pending.empty:
        print("No pending submissions found.")
        return None
    
    # Grab the oldest pending post
    first_row = pending.iloc[0]
    return first_row['Submission']

# ---------------------------------------------------------------------------
# STEP 2: MODERATE & FORMAT WITH GEMINI API
# ---------------------------------------------------------------------------
def process_with_gemini(text):
    print("Processing post with Gemini...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    You are an automated editor for a college 'Spotted' Instagram page.
    Analyze this user submission: "{text}"
    
    Task:
    1. Moderation: Reject if it contains slurs, severe harassment, or explicit personal contact info (doxxing).
    2. Format: Shorten/clean the quote for an image card (max 30 words).
    3. Caption: Write a short, engaging Instagram caption with 3-5 relevant hashtags.
    
    Return STRICT JSON:
    {{
      "approved": true,
      "card_text": "Short clean quote here",
      "caption": "Fun caption here! #spotted"
    }}
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    
    return json.loads(response.text)

# ---------------------------------------------------------------------------
# STEP 3: RENDER QUOTE IMAGE CARD USING PILLOW
# ---------------------------------------------------------------------------
def generate_image(text, output_path="latest_post.jpg"):
    print("Generating image card...")
    # Create 1080x1080 canvas (Instagram square)
    img = Image.new('RGB', (1080, 1080), color='#0F172A') # Dark slate background
    draw = ImageDraw.Draw(img)
    
    # Basic text-wrapping logic
    font = ImageFont.load_default()
    margin = 80
    offset = 450
    
    # Draw simple centered/wrapped text box
    draw.multiline_text(
        (margin, offset), 
        text, 
        fill='#F8FAFC', 
        font=font, 
        spacing=10
    )
    
    img.save(output_path)
    print(f"Image saved to {output_path}")

# ---------------------------------------------------------------------------
# STEP 4: PUBLISH TO INSTAGRAM VIA GRAPH API
# ---------------------------------------------------------------------------
def publish_to_instagram(caption):
    print("Publishing to Instagram...")
    
    # 1. Create Media Container
    container_url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"
    container_payload = {
        'image_url': IMAGE_URL,
        'caption': caption,
        'access_token': META_ACCESS_TOKEN
    }
    res = requests.post(container_url, data=container_payload).json()
    
    if 'id' not in res:
        print("Error creating media container:", res)
        return
        
    creation_id = res['id']
    
    # 2. Publish Media
    publish_url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        'creation_id': creation_id,
        'access_token': META_ACCESS_TOKEN
    }
    pub_res = requests.post(publish_url, data=publish_payload).json()
    print("Published successfully! Post ID:", pub_res.get('id'))

# ---------------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    raw_submission = get_pending_submission()
    
    if raw_submission:
        ai_result = process_with_gemini(raw_submission)
        
        if ai_result.get("approved"):
            generate_image(ai_result["card_text"])
            publish_to_instagram(ai_result["caption"])
        else:
            print("Submission rejected by Gemini safety moderation.")