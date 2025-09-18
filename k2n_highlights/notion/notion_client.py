from notion_client import Client
from dotenv import load_dotenv
from ..parser.html_parser import parse_html
from .formatter import build_notion_blocks
from datetime import datetime
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from .user_state import user_data_overrides
import requests
import urllib.parse
import asyncio
import os

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

notion = Client(auth=NOTION_API_KEY)

# Genre to emoji mapping
genre_emoji_map = {
    "Fiction": "📖",
    "History": "🏰",
    "Psychology": "🧠",
    "Science": "🔬",
    "Philosophy": "📚",
    "Biography": "👤",
    "Business": "💼",
    "Self-Help": "🧘",
    "Health": "🩺",
    "Education": "🎓"
}

def get_cover_search_url(book_title, author):
    query = f"{book_title} {author} cover"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?tbm=isch&q={encoded_query}"

def get_genre_and_emoji(book_title, author):
    params = {
        "q": f"{book_title} {author}",
        "maxResults": 1,
        "printType": "books"
    }
    r = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
    if r.status_code != 200:
        return None, None, None

    data = r.json()
    items = data.get("items", [])
    if not items:
        return None, None, None

    volume_info = items[0].get("volumeInfo", {})
    categories = volume_info.get("categories", [])
    published_date = volume_info.get("publishedDate", "")

    genre = categories[0] if categories else None
    emoji = None

    if genre:
        if genre.startswith("Fiction"):
            genre = "Fiction"
            emoji = genre_emoji_map.get("Fiction")
        else:
            emoji = genre_emoji_map.get(genre)

    # Extract only year
    year = published_date.split("-")[0] if published_date else None

    return genre, emoji, {"published_year": year}

def find_or_create_page(book_title, author):
    genre, emoji, extra = get_genre_and_emoji(book_title, author)

    query = notion.databases.query(
        **{"database_id": NOTION_DATABASE_ID, "filter": {"property": "Title", "rich_text": {"equals": book_title}}}
    )
    if query["results"]:
        return query["results"][0]["id"]

    props = {
        "Title": {"title": [{"text": {"content": book_title}}]},
        "Author": {"rich_text": [{"text": {"content": author}}]},
        "Status": {"status": {"name": "Finished"}},
        "End of reading": {"date": {"start": datetime.today().strftime("%Y-%m-%d")}}
    }

    if genre:
        clean_genre = genre.split(",")[0].strip()
        props["Genre"] = {"select": {"name": clean_genre}}
    if extra and extra.get("published_year"):
        props["Year"] = {"rich_text": [{"text": {"content": extra["published_year"]}}]}

    page = notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties=props,
        icon={"emoji": emoji or "📚"}
    )
    return page["id"]

async def process_html_file(file_path, update, context):
    parsed = parse_html(file_path)
    print("🧩 Parsing result:")
    print(parsed)

    user_id = update.effective_user.id
    user_data_overrides[user_id] = {
        "parsed": parsed,
        "file_path": file_path
    }

    await update.message.reply_text(
        f"👤 Author: {parsed['author']}\n\nIs this correct?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data="confirm_author"),
                InlineKeyboardButton("✏️ Edit", callback_data="edit_author")
            ]
        ])
    )
    return None

async def continue_processing_after_confirmation(user_id, update, context):
    data = user_data_overrides.get(user_id)
    if not data:
        return "❌ Data lost. Please send the file again."

    parsed = data["parsed"]
    book_title = parsed["title"]
    author = parsed["author"]
    highlights = parsed["highlights"]

    page_id = find_or_create_page(book_title, author)

    # 🧹 Safe deletion of old blocks
    children = notion.blocks.children.list(page_id).get("results", [])
    for child in children:
        try:
            block_type = child.get("type")
            if block_type not in ["unsupported", "breadcrumb", "table_of_contents"]:
                notion.blocks.delete(child["id"])
                await asyncio.sleep(0.1)  # short pause for stability
        except Exception as e:
            print(f"⚠️ Failed to delete block {child['id']}: {e}")
            continue

#   print("--- Highlights before build_notion_blocks ---")
#   print(parsed["highlights"])
#   print("--- End of highlights ---")

    # Getting structured sections and blocks
    sections, content_blocks = build_notion_blocks(parsed)

    # Insert placeholder TOC
    placeholder_toc = {
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "📚"},
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "⌛ Generating Table of Contents..."
                }
            }]
        }
    }
    placeholder = notion.blocks.children.append(page_id, children=[placeholder_toc])
    toc_block_id = placeholder["results"][0]["id"]

    # Insert heading_2 and highlights
    inserted = notion.blocks.children.append(page_id, children=content_blocks)
    inserted_blocks = inserted["results"]

    # Create mapping: section -> heading block_id
    heading_map = {}
    heading_idx = 0
    for s in sections:
        heading_map[s["section"]] = inserted_blocks[heading_idx]["id"]
        heading_idx += 1 + len(s["paragraphs"])

    # TOC with anchor links
    toc_rich_text = []
    for sec in sections:
        heading_id = heading_map[sec["section"]]
        url = f"https://www.notion.so/{page_id.replace('-', '')}#{heading_id.replace('-', '')}"
        toc_rich_text.append({
            "type": "text",
            "text": {
                "content": f"- {sec['section']}\n",
                "link": {"url": url}
            }
        })

    # Synced line (no link)
    toc_rich_text.append({
        "type": "text",
        "text": {
            "content": f"\nSynced by kindle_highlights2notion_bot at {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        }
    })

    # Update placeholder TOC block
    notion.blocks.update(toc_block_id, callout={
        "icon": {"type": "emoji", "emoji": "📚"},
        "rich_text": toc_rich_text
    })

    # Prepare for cover upload
    context.user_data["pending_cover"] = {
        "page_id": page_id,
        "book_title": book_title,
        "author": author
    }

    search_url = get_cover_search_url(book_title, author)

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"✅ {len(highlights)} highlights added to the page '{book_title}'.\n\n"
            "📚 If you want to add a cover — press the button below, find an image on Google and send it here 👇"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search cover in Google", url=search_url)]
        ])
    )
    # 🧹 Delete temporary file
    try:
        file_path = data.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧼 Temporary file deleted: {file_path}")
    except Exception as e:
        print(f"⚠️ Failed to delete temporary file: {e}")

    return None
