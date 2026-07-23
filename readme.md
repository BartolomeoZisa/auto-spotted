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
```

Setting up Google Sheets write access requires creating a **Google Cloud Service Account** key. Here is how to generate those credentials from scratch and link them to your project.

---

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Log in with your Google account.
3. Click the **Project Selector** dropdown at the top left (next to the Google Cloud logo) and click **New Project**.
4. Enter a project name (e.g., `Instagram-Spotted-Bot`) and click **Create**.
5. Ensure your new project is selected in the top dropdown.

---

## Step 2: Enable the Required APIs

1. In the left navigation menu, go to **APIs & Services > Library**.
2. Search for **Google Sheets API**, click on it, and click **Enable**.
3. Search for **Google Drive API**, click on it, and click **Enable**. *(Needed so the service account can locate your sheet)*.

---

## Step 3: Create a Service Account

1. In the left navigation menu, go to **APIs & Services > Credentials**.
2. Click **+ Create Credentials** at the top and select **Service Account**.
3. Fill in the service account details:
* **Service account name**: e.g., `sheets-updater`
* **Service account ID**: (generates automatically)


4. Click **Create and Continue**.
5. *(Optional)* Skip the role and user access steps by clicking **Done**.

---

## Step 4: Generate the JSON Key File

1. On the **Credentials** page, look under the **Service Accounts** section at the bottom.
2. Click on the email address of the service account you just created.
3. Select the **Keys** tab at the top.
4. Click **Add Key > Create new key**.
5. Select **JSON** as the key type and click **Create**.
6. A `.json` file will automatically download to your computer.

---

## Step 5: Place the Credentials & Share the Sheet

1. **Rename and move the JSON key:** Local Setup.
Rename the downloaded `.json` file to `credentials.json` and move it directly into your Python project root folder (where your `main.py` script lives).


2. **Copy the Service Account Email:** Google Cloud Console.
Open `credentials.json` or check the Service Accounts tab in Google Cloud to copy the `client_email` address (it looks like `sheets-updater@your-project-id.iam.gserviceaccount.com`).


3. **Share the Google Sheet:** Google Sheets.
Open your Google Sheet, click **Share** in the top-right corner, paste the `client_email`, give it **Editor** permissions, and click **Send**.


4. **Add Environment Variables:** .env File.
Add the spreadsheet ID (found in your Google Sheet's URL between `/d/` and `/edit`) to your `.env` file:

```env
SPREADSHEET_ID="your_sheet_id_here"
GOOGLE_SERVICE_ACCOUNT_FILE="credentials.json"

```


---

> **Important:** Keep your `credentials.json` file private. If pushing your code to GitHub, ensure `credentials.json` is added to your `.gitignore` file.