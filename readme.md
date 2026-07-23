# 📍 Auto-Spotted Instagram Bot

A fully automated Python bot for managing and publishing content for "Spotted" Instagram pages. 

The system reads user submissions from a Google Form, performs automated moderation and text formatting using **Google Gemini AI**, generates a post graphic using **Pillow**, and publishes it directly to Instagram via the **Meta Graph API** and **GitHub Actions**.

---

## 🚀 System Architecture

1. **Google Sheets (CSV):** Collects user submissions from the input form.
2. **Google Gemini API (`gemini-3.1-flash-lite`):** 
   - Moderates content (filters out hate speech, doxxing, and harassment).
   - Shortens/cleans the quote for the image card (max 30 words).
   - Generates an engaging Instagram caption with relevant hashtags.
3. **Pillow (PIL):** Renders a 1080x1080px image card (standard Instagram square format).
4. **GitHub Pages:** Hosts and serves the generated image (`latest_post.jpg`) via a public HTTPS URL.
5. **Instagram Graph API:** Creates the media container and publishes the post to the connected Instagram account.
6. **GitHub Actions:** Runs the entire workflow automatically every 6 hours (or on demand).

---

## 🛠️ Built With

- **Python 3.10**
- **Pandas** (for parsing Google Sheets data)
- **Google GenAI SDK** (for Gemini AI integration)
- **Pillow** (for image generation)
- **Requests** (for Meta Graph API requests)
- **GitHub Actions & Pages** (for automation and hosting)

---

## 🔑 Environment Variables & Secrets

To run the bot, you need to set up the following **Repository Secrets** on GitHub (`Settings` > `Secrets and variables` > `Actions`):

| Secret Name | Description |
| :--- | :--- |
| `SHEET_CSV_URL` | The public CSV export URL of your Google Sheet. |
| `GEMINI_API_KEY` | API key to access the Gemini model (from Google AI Studio). |
| `META_ACCESS_TOKEN` | Long-lived Meta Graph API token with Instagram publishing permissions. |
| `IG_USER_ID` | Numeric ID of your Instagram Business/Creator account. |
| `IMAGE_URL` | Public URL of the generated image hosted on GitHub Pages (`https://<username>.github.io/<repo>/latest_post.jpg`). |

---

## 📂 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── run.yml           # GitHub Actions workflow (schedule + execution)
├── main.py                   # Main Python automation script
├── requirements.txt          # Python dependencies
├── latest_post.jpg           # Latest generated image (served via GitHub Pages)
└── README.md                 # Project documentation