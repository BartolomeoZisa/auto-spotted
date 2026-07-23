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
def get_pending_submission(debug=False):
    if debug:
        print("Fetching submissions from Google Sheet...")
        print(f"DEBUG - Fetching from URL: {SHEET_CSV_URL[:60]}...")
    
    try:
        df = pd.read_csv(SHEET_CSV_URL, engine='python')
    except Exception as e:
        if debug:
            print(f"❌ DEBUG - Error reading CSV: {e}")
        return None

    # Clean whitespace from column headers
    df.columns = df.columns.str.strip()
    
    if debug:
        print("\n--- 🔍 DEBUG INFO ---")
        print(f"Total rows retrieved: {len(df)}")
        print(f"Detected columns: {list(df.columns)}")
        print("\nRaw Data Snippet:")
        print(df.to_string())
        print("---------------------\n")

    if df.empty:
        if debug:
            print("⚠️ DEBUG - Dataframe is completely empty!")
        return None

    if 'Status' in df.columns:
        # Normalize status column values
        status_series = df['Status'].fillna('').astype(str).str.strip().str.lower()
        if debug:
            print(f"DEBUG - Unique values in 'Status' column: {status_series.unique()}")
        
        # Match 'pending' or empty values
        pending = df[status_series.isin(['pending', ''])]
    else:
        if debug:
            print("⚠️ DEBUG - 'Status' column not found! Treating all rows as pending.")
        pending = df

    if debug:
        print(f"DEBUG - Pending rows found: {len(pending)}")

    if pending.empty:
        print("No new pending submissions found.")
        return None

    # Pick the first pending row
    latest_row = pending.iloc[0]
    
    # Target text column
    target_col = 'Chi o cosa vuoi spottare?'
    if target_col in df.columns:
        submission_text = latest_row[target_col]
    else:
        submission_text = latest_row.iloc[1]

    if debug:
        print(f"✅ DEBUG - Selected submission: '{submission_text}'")
        
    return submission_text

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
    
    For card_text and caption, write them in the language of the original submission.
    For approved, return true or false.

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
    
    # 1. Image Base (White with solid Border)
    # 1080x1080 square for Instagram
    border_width = 100
    base_color = "#FFFFFF" # Main internal canvas (white)
    border_color = "#0F172A" # Different sophisticated border color (Midnight Blue)
    
    img = Image.new('RGB', (1080, 1080), color=border_color)
    draw_canvas = ImageDraw.Draw(img)
    
    # Draw internal white rectangle
    canvas_top_left = (border_width, border_width)
    canvas_bottom_right = (1080 - border_width, 1080 - border_width)
    draw_canvas.rectangle([canvas_top_left, canvas_bottom_right], fill=base_color)

    # 2. Text Container (Bubble) - mimic the structure of the prompt reference
    bubble_color = "#F1F5F9" # Light grey bubble
    bubble_paddings = (60, 60, 60, 60) # T, R, B, L
    
    # Define Font (prefer truetype for clean looks)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
    except IOError:
        font = ImageFont.load_default()
        print("Warning: Arial not found. Using default font.")

    # Measure text for centering and bubble sizing
    wrapped_lines = []
    max_line_width = 0
    words = text.split()
    current_line = []
    
    for word in words:
        current_line.append(word)
        line_text = " ".join(current_line)
        line_bbox = draw_canvas.textbbox((0, 0), line_text, font=font)
        line_w = line_bbox[2] - line_bbox[0]
        
        if line_w > (1080 - 2 * border_width - bubble_paddings[1] - bubble_paddings[3]):
            # Start new line
            wrapped_lines.append(" ".join(current_line[:-1]))
            current_line = [word]
        else:
            if line_w > max_line_width:
                max_line_width = line_w
                
    wrapped_lines.append(" ".join(current_line)) # Add the final line
    formatted_text = "\n".join(wrapped_lines)

    # Text measurement for the bubble
    text_bbox = draw_canvas.multiline_textbbox((0, 0), formatted_text, font=font, spacing=15)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    # Bubble Dimensions
    bubble_w = text_w + bubble_paddings[1] + bubble_paddings[3]
    bubble_h = text_h + bubble_paddings[0] + bubble_paddings[2]
    
    # Position bubble centrally on the white canvas
    bubble_x = (1080 - bubble_w) // 2
    bubble_y = (1080 - bubble_h) // 2
    
    # Draw bubble (rounded rectangle)
    bubble_radius = 25
    draw_canvas.rounded_rectangle(
        [(bubble_x, bubble_y), (bubble_x + bubble_w, bubble_y + bubble_h)],
        fill=bubble_color,
        radius=bubble_radius,
        outline=None,
    )
    
    # Add subtle shadow for depth
    shadow_offset = (5, 5)
    shadow_color = (200, 200, 200, 100)
    shadow_image = Image.new('RGBA', img.size, (255, 255, 255, 0))
    shadow_draw = ImageDraw.Draw(shadow_image)
    shadow_draw.rounded_rectangle(
        [(bubble_x + shadow_offset[0], bubble_y + shadow_offset[1]), 
         (bubble_x + bubble_w + shadow_offset[0], bubble_y + bubble_h + shadow_offset[1])],
        fill=shadow_color,
        radius=bubble_radius
    )
    img = Image.alpha_composite(img.convert("RGBA"), shadow_image).convert("RGB")
    draw_canvas = ImageDraw.Draw(img) # Refresh draw object after compositing

    # 3. Text rendering inside bubble
    text_x = bubble_x + bubble_paddings[3]
    text_y = bubble_y + bubble_paddings[0]
    
    # The example text we are generating, as suggested by the example file image_2.png
    sample_text = "📍 SPOTTED\nSaw you drinking coffee in the library looking incredibly productive. You've got my attention. #spotted #coffee 📍"
    
    # Measure final text for final placement adjustment
    text_bbox = draw_canvas.multiline_textbbox((0,0), formatted_text, font=font, spacing=15)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    # Redraw multiline text inside bubble with specified spacing and font
    # Anchor is "la" (left-aligned) by default for multiline
    draw_canvas.multiline_text(
        (text_x, text_y), 
        formatted_text, 
        fill=border_color, # Same color as the border
        font=font, 
        spacing=15,
        align="left"
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
    raw_submission = get_pending_submission(debug=True)
    
    if raw_submission:
        ai_result = process_with_gemini(raw_submission)
        
        if ai_result.get("approved"):
            generate_image(ai_result["card_text"])
            publish_to_instagram(ai_result["caption"])
        else:
            print("Submission rejected by Gemini safety moderation.")