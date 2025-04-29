<p align="center">
  <img src="https://raw.githubusercontent.com/falone/kindle_highlights_2_notion/main/assets/new.png" alt="Kindle Highlights 2 Notion Bot banner" width="400"/>
</p>

# Kindle Highlights 2 Notion Bot ![Badge](https://hitscounter.dev/api/hit?url=https%3A%2F%2Fgithub.com%2Ffalone%2Fkindle_highlights_2_notion&label=Hits&icon=github&color=%23198754)

This Telegram bot lets you upload Kindle highlights (APA-style HTML) and automatically imports them into Notion — with formatting, cover image selection, genre tagging, and more.


## Disclaimer
I am not a professional programmer, but a hobbyist who writes code with ChatGPT and Gemini for my own needs. Therefore, this code may be funny, silly, or incorrect - I absolutely understand that. If you have any tips on how to improve it, I will be grateful for the hints, but I don't promise that I will be able to implement them.

---
### 📚 Table of Contents

- [Features](#-features)
- [How to use the bot](#-how-to-use-the-bot)
- [Preparation](#-preparation)
  - [1. Create a notion database with the required fields](#1-create-a-notion-database-with-the-required-fields)
  - [2. Create a connection and connect it to your database](#2-create-a-connection-and-connect-it-to-your-database)
  - [3. Create telegram bot via @BotFather](#3-create-telegram-bot-via-botfather)
  - [4. Set up Imgur and get the necessary tokens to upload pictures](#4-set-up-imgur-and-get-the-necessary-tokens-to-upload-pictures)
- [Quick Start](#-quick-start)
  - [Option 1: Run with Docker](#-option-1-run-with-docker)
  - [Option 2: Run manually (Python)](#-option-2-run-manually-python)
- [Telegram bot demo](#-telegram-bot-demo)
- [Notion Screenshots](#-notion-screenshots)
- [Support](#-support)

---

## ✨ Features

- Parses Kindle APA HTML highlights
- Detects title, author, sections, pages, highlight color
- Automatically creates or updates a Notion book page
- Adds Table of Contents with anchor links
- Emoji-based page icons based on genre
- Optional manual cover image upload
- Syncs highlights with dates and metadata
- UPD: Now covers are loaded to Imgur. See the "Preparation" section for necessary instructions
---
## 🧰 How to use the bot:
1. Install the official Kindle app on your phone/tablet
2. Download the book from which you want to export highlights
3. Click on Highlights - Share
4. Be sure to select Citation style - APA
5. Send the resulting HTML file to your bot
6. If necessary, edit the Title and Author, add a Cover page

Enjoy!

By default after sending highlights the bot will set the status to "Finished" and the "End of reading" date will be set on the day you uploaded the highlights

---
# ⭐ Preparation:
## 1. Create a notion database with the required fields

|Property name | Property type|
|---------------|----------------|
|Title | Text|
|Author | Text|
|Status | Status|
|End of reading | Date|
|Year | Text|
|Genre | Select|

Do not change the name of the properties or if you want to - then edit them in notion_client.py

## 2. Create a connection and connect it to your database
To allow the bot to access your Notion workspace and database, follow these steps:

### 1️⃣ Create a New Integration in Notion
Go to https://www.notion.so/profile/integrations
- Click +New integration
- Give your integration a name (e.g. Kindle2Notion Bot)
- Select the workspace you want to connect it to
- Under Capabilities, enable:
  ✅ Read content
  ✅ Insert content
  ✅ Update content
- Click Submit
- Copy the Internal Integration Token — you’ll use this as NOTION_API_KEY in your .env or stack.env

### 2️⃣ Share Your Notion Database with the Integration
- Navigate to the database you want the integration to access.
- Click on the ••• (More options) button at the top-right corner of the page (not the table!)
- Select Connections from the dropdown menu.
- In the pop-up, search for the name of your integration.
- Select your integration and click Confirm to grant it access to the database.

### 3️⃣ Find Your Notion Database ID
- Open your Notion database in a browser
- Look at the URL — it should look like:
```text
https://www.notion.so/yourworkspace/Book-Highlights-abcd1234ef56789012345678abcdef12
```

The long string at the end (32 characters) 
```text
abcd1234ef56789012345678abcdef12
```
is your database ID
Use this as NOTION_DATABASE_ID in your .env or stack.env

## 3. Create telegram bot via @BotFather
Use it's Token as TELEGRAM_BOT_TOKEN in your .env or stack.env.

## 4. Set up Imgur and get the necessary tokens to upload pictures
To allow the bot to upload book cover images to Imgur (for reliable image hosting), you'll need to set up an Imgur application and configure your environment with the required tokens.

### 1️⃣ Register an Imgur Application
1. Visit [Imgur API registration](https://api.imgur.com/oauth2/addclient). Login with Google if necessary.
2. Fill out the form:
- **Authorization type:** ```OAuth 2 authorization without a callback URL```
- **Application name:** e.g., ```Kindle Highlights to Notion```
- **Email:** your valid email
- **Description:** anything (e.g., ```Bot that uploads Kindle highlights to Notion with cover support```)
3. Submit the form.
4. You’ll receive two important credentials:
- Client ID - you’ll use this as IMGUR_CLIENT_ID in your .env or stack.env
- Client Secret - you’ll use this as IMGUR_CLIENT_SECRET in your .env or stack.env

### 2️⃣ Authorize Your App
1. Open the following URL in your browser, replacing ```<CLIENT_ID>``` with your actual Client ID:
   ```bash
   https://api.imgur.com/oauth2/authorize?client_id=<CLIENT_ID>&response_type=token
   ```
2. Log in to your Imgur account and **authorize the app**.
3. You’ll be redirected to a URL that looks like:
   ```bash
   https://imgur.com/#access_token=...&expires_in=...&token_type=...&refresh_token=...&account_username=...&account_id=...
   ```
4. Copy and save the following values from the URL:
- access_token - you’ll use this as IMGUR_ACCESS_TOKEN in your .env or stack.env
- refresh_token - you’ll use this as IMGUR_REFRESH_TOKEN in your .env or stack.env
- account_username - you’ll use this as ACCOUNT_USERNAME in your .env or stack.env
  
### ❓ What the Bot Does with These Tokens
It uploads book cover images directly to your Imgur account.
If the access token expires, the bot will automatically refresh it using the refresh token.
Uploaded images are hosted in your Imgur profile under ```https://imgur.com/user/<your_account_username>``` and used as external image URLs in Notion.

---
# 📦 Installation and Setup Instructions (for Beginners)

## 🪟 Windows

### 1. Create a Project Folder

- Open File Explorer (`Win + E`)
- Create a folder, e.g., `D:\Projects\k2n_project`
- Open Command Prompt (`Win + R`, type `cmd`)

    
    cd /d D:\Projects\k2n_project
    

### 2. Create and Activate a Virtual Environment

    python -m venv venv
    venv\Scripts\activate
    
✅ `(venv)` should appear at the beginning of the command line.

### 3. Install the Bot

    pip install k2n-highlights
    
### 4. Create and Configure the `.env` File

    copy nul .env
    
- Open `.env` in Notepad.
- Fill it based on `.env.example`:

    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_token
    NOTION_API_KEY=your_notion_api_key
    NOTION_DATABASE_ID=your_notion_database_id

    IMGUR_ACCESS_TOKEN=
    IMGUR_REFRESH_TOKEN=
    IMGUR_CLIENT_ID=
    IMGUR_CLIENT_SECRET=
    IMGUR_ACCOUNT_USERNAME=
    ```

### 5. Run the Bot

    k2n-highlights
    
or
    ```
    python -m k2n_highlights
    ```

---

## 🐧 Linux

### 1. Create a Project Folder

    cd ~/Documents
    mkdir k2n_project
    cd k2n_project
    
### 2. Create and Activate a Virtual Environment

    python3 -m venv venv
    source venv/bin/activate
    
✅ `(venv)` should appear.

### 3. Install the Bot

    pip install k2n-highlights
    
### 4. Create and Configure the `.env` File

    touch .env
    nano .env
    
Fill the `.env` file like this:

    TELEGRAM_BOT_TOKEN=your_telegram_token
    NOTION_API_KEY=your_notion_api_key
    NOTION_DATABASE_ID=your_notion_database_id

    IMGUR_ACCESS_TOKEN=
    IMGUR_REFRESH_TOKEN=
    IMGUR_CLIENT_ID=
    IMGUR_CLIENT_SECRET=
    IMGUR_ACCOUNT_USERNAME=
    
Save (`Ctrl + O`, `Enter`) and exit (`Ctrl + X`).

### 5. Run the Bot

    k2n-highlights
    
or

    python3 -m k2n_highlights
---

## 🍏 macOS

### 1. Create a Project Folder

    cd ~/Documents
    mkdir k2n_project
    cd k2n_project
    
### 2. Create and Activate a Virtual Environment

    python3 -m venv venv
    source venv/bin/activate
    
✅ `(venv)` should appear.

### 3. Install the Bot

    pip install k2n-highlights
    
### 4. Create and Configure the `.env` File

    touch .env
    nano .env
    
Fill the `.env` file:

    TELEGRAM_BOT_TOKEN=your_telegram_token
    NOTION_API_KEY=your_notion_api_key
    NOTION_DATABASE_ID=your_notion_database_id

    IMGUR_ACCESS_TOKEN=
    IMGUR_REFRESH_TOKEN=
    IMGUR_CLIENT_ID=
    IMGUR_CLIENT_SECRET=
    IMGUR_ACCOUNT_USERNAME=
    
Save and exit.

### 5. Run the Bot

    k2n-highlights
    
or
    
    python3 -m k2n_highlights
---
# ⚡ Important: Reactivating the Environment After Restart

Each time you open a new terminal or command prompt window:
1. Navigate to your project folder.
2. Activate the virtual environment again.

Only then run the bot.

---

# 🛠 For Developers (Advanced Users)

If you want to run the bot directly from the source code instead of installing it:

### 1. Clone the Repository

    git clone https://github.com/falone/kindle_highlights_2_notion.git
    cd k2n_highlights
    
### 2. Create and Activate a Virtual Environment

#### Windows:

    python -m venv venv
    venv\Scripts\activate
    
#### Linux / macOS:

    python3 -m venv venv
    source venv/bin/activate
    
### 3. Install Dependencies

    pip install -r requirements.txt
    
### 4. Configure the `.env` File

    copy .env.example .env    # Windows
    cp .env.example .env      # Linux/macOS
    
Edit `.env` and fill in your tokens.

### 5. Run the Bot

    python -m k2n_highlights
    
✅ Now the bot will start using the local source code.

---

# 📋 Notes for Developers

- Make sure `.env` is present in the working directory.
- This method is intended for debugging and development.
- For production use, prefer installing from PyPI.

🔐 Environment Variables (.env)
|Variable | Description|
|---------------|----------------|
|TELEGRAM_BOT_TOKEN | Your Telegram bot token|
|NOTION_API_KEY | Notion integration token|
|NOTION_DATABASE_ID | Notion database ID|
|IMGUR_ACCESS_TOKEN | Imgur access token|
|IMGUR_REFRESH_TOKEN | Imgur refresh token|
|IMGUR_CLIENT_ID | Imgur client id|
|IMGUR_CLIENT_SECRET | Imgur client secret|
|IMGUR_ACCOUNT_USERNAME | Imgur account username|
---
Don't forget to create a file named .env (see .env.example) with your credentials

---
## 📱 Telegram bot demo
![Demo](https://raw.githubusercontent.com/falone/kindle_highlights_2_notion/main/assets/demo.gif)

## 🖼 Notion Screenshots
<details>
<summary><b>📸 Example Output</b></summary>
<img src="https://raw.githubusercontent.com/falone/kindle_highlights_2_notion/main/assets/preview3.png" width="600"/>
<img src="https://raw.githubusercontent.com/falone/kindle_highlights_2_notion/main/assets/preview4.png" width="600"/>
<img src="https://raw.githubusercontent.com/falone/kindle_highlights_2_notion/main/assets/preview1.png" width="600"/>
<img src="https://raw.githubusercontent.com/falone/kindle_highlights_2_notion/main/assets/preview2.png" width="600"/>
</details>

---
## 💖 Support

If you find this project useful, you can support me here:

<a href='https://ko-fi.com/V7V71DIZWQ' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
