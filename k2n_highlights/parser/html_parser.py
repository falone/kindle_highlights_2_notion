from bs4 import BeautifulSoup

def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml-xml")

    title = soup.find("div", class_="bookTitle").get_text(strip=True)
    author = soup.find("div", class_="authors").get_text(strip=True)

    sections = []
    current_section = None
    highlights = []

    for el in soup.find_all("div"):
        if "sectionHeading" in el.get("class", []):
            current_section = el.get_text(strip=True)

        elif "noteHeading" in el.get("class", []):
            note_heading_text = el.get_text(strip=True)
            page_info = None
            current_color = "yellow"  # Default color
            highlight_type = "highlight"  # Default type

            # 🔍 If it's a Note — change type
            if note_heading_text.strip().lower().startswith("note"):
                highlight_type = "note"

            # 🎨 Detect highlight color from span class
            span = el.find("span")
            if span and span.get("class"):
                full_class = "".join(span.get('class'))
                if "highlight_" in full_class:
                    current_color = full_class.replace("highlight_", "")

            # 📄 Detect page info
            if "Location" in note_heading_text:
                page_info = note_heading_text.split("Location")[-1].strip()
            elif "Page" in note_heading_text:
                page_part = note_heading_text.split("Page")[-1].split("-")[0].strip()
                page_info = page_part.split(")")[0].strip()

            if current_section and page_info is not None:
                highlights.append({
                    "section": current_section,
                    "page": page_info,
                    "text": None,
                    "color": current_color,
                    "type": highlight_type
                })

        elif "noteText" in el.get("class", []):
            text = el.get_text(strip=True)
            if highlights and highlights[-1]["text"] is None:
                highlights[-1]["text"] = text

    return {
        "title": title,
        "author": author,
        "highlights": highlights
    }
