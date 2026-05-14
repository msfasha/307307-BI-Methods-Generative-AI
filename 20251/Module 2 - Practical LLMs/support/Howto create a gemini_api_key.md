## Create  Gemini API Key

### Step 0 — Prerequisite: A Google Account

Before you begin, make sure you have an active Google account (for example, a Gmail account).
You’ll need it to sign in to Google AI Studio and manage your Gemini API keys.

If you don’t have one, you can create it here:
https://accounts.google.com/signup

### Step 1 — Go to Google AI Studio

1. Open: [https://aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account.
3. You’ll see the Gemini AI Studio dashboard.

---

### Step 2 — Accept Terms and Set Up Project

* If this is your first time, you’ll be asked to accept the terms of service.
* Optionally, create or select a Google Cloud project to organize usage and billing.

---

### Step 3 — Create an API Key

1. Click “Get API key” in the top-left menu or go directly to:
   [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click “Create API key.”
3. Copy the key that looks like this:

   ```
   AIzaSyC5vFxxxxxxxxxxxxxxxxxxxxxxxx
   ```

Keep this key private. Do not upload it to GitHub or share it publicly.

---

### Step 4 — Install the Python Client Library

If you plan to use the API from Python, install the Gemini SDK:

```bash
pip install google-genai
```

---

### Step 5 — Use the API Key in Your Code

Example Python script:

```python
from google import genai

# Configure the Gemini client
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# Create a client
client = genai.Client()

# Generate text
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Write a haiku about data science."
)

print(response.text)
```

---

### Step 6 — (Optional) Store the Key Securely

You can store the key as an environment variable instead of hardcoding it.

**Windows (PowerShell):**

```powershell
setx GEMINI_API_KEY "YOUR_GEMINI_API_KEY"
```

**macOS/Linux (bash):**

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Then load it in Python:

```python
import os
from google import genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```

