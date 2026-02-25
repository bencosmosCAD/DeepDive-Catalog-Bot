# 🚀 How to Share Your App (Deployment Guide)

Since you want to send this to your wife quickly, here are the two best options.

## Option 1: The "5-Minute" Method (Temporary)
This creates a public link to your *currently running* computer. It stops working if you close the terminal or turn off your PC.

1.  **Run the App**: Ensure your app is running in the terminal (`streamlit run app_v2.py`).
2.  **Open a New Terminal**: Press `Win + R`, type `powershell`, and hit Enter.
3.  **Run this Command**:
    ```powershell
    ssh -R 80:localhost:8501 nokey@localhost.run
    ```
    *(If that asks for a key verification, type `yes`)*.
4.  **Copy the URL**: It will output something like `https://random-name.localhost.run`.
5.  **Send it**: She can open this on her phone or laptop immediately.

---

## Option 2: The "Professional" Method (Permanent)
Use **Streamlit Community Cloud**. This gives you a permanent, professional link (e.g., `deepdive-catalog.streamlit.app`) that works 24/7.

**Prerequisite**: A GitHub Account (free).

### Updated Steps:
1.  **Create a Repository**:
    - Go to GitHub.com -> New Repository.
    - Name it `catalog-bot`.
    - Set it to **Public**.
2.  **Upload Files**:
    - Upload **ALL** files from `c:/me/catalog_bot` into the repo.
    - *Crucial*: Ensure `requirements.txt` and `.streamlit/config.toml` are included.
3.  **Deploy on Streamlit**:
    - Go to [share.streamlit.io](https://share.streamlit.io).
    - Log in with GitHub.
    - Click **"New App"**.
    - Select your `catalog-bot` repository.
    - Set **Main file path** to `app_v2.py`.
    - **IMPORTANT**: Click **"Advanced Settings"** -> **"Secrets"**.
    - Paste your API Key like this:
      ```toml
      GEMINI_API_KEY = "AIzaSy..."
      ```
    - Click **Deploy!**

### Troubleshooting Verification
Before you send the link, open `app_v2.py` and ensure line 26/27 are using `gemini-2.0-flash-exp` (I already did this for you).

Your `requirements.txt` is updated and ready for cloud deployment.
