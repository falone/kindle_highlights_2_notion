from datetime import datetime

def build_notion_blocks(parsed):
    sections = []
    section_blocks = []
    seen_sections = set()

    # Mapping Kindle highlight colors to Notion colors
    color_map = {
        "yellow": "yellow",
        "blue": "blue",
        "pink": "pink",
        "orange": "orange"
    }

    for h in parsed["highlights"]:
        sec = h["section"]
        notion_color = color_map.get(h.get("color", "yellow"), "default")
        text = h["text"]
        page = h["page"]
        h_type = h.get("type", "highlight")  # "highlight" or "note"

        # Create a heading block if the section has not been seen
        if sec not in seen_sections:
            seen_sections.add(sec)
            heading_block = {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": sec}
                    }]
                }
            }
            sections.append({
                "section": sec,
                "heading_block": heading_block,
                "paragraphs": []
            })
            section_blocks.append(heading_block)

        # 📝 NOTE as quote block
        if h_type == "note":
            quote_rich_text = []

            # Emoji as the first text fragment
            quote_rich_text.append({
                "type": "text",
                "text": {"content": "📝 "},
                "annotations": {"italic": True, "color": "default"}
            })

            # Main text
            chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
            for chunk in chunks:
                quote_rich_text.append({
                    "type": "text",
                    "text": {"content": chunk},
                    "annotations": {"italic": True, "color": "default"}
                })

            # Page reference
            quote_rich_text.append({
                "type": "text",
                "text": {"content": f" (Page {page})"},
                "annotations": {"italic": True, "color": notion_color}
            })

            note_block = {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": quote_rich_text
                }
            }

            for s in sections:
                if s["section"] == sec:
                    s["paragraphs"].append(note_block)
                    break

        # 📌 HIGHLIGHT as paragraph block
        else:
            rich_text_parts = [{
                "type": "text",
                "text": {"content": "📌 "},
                "annotations": {"color": "default"}
            }]

            chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
            for chunk in chunks:
                rich_text_parts.append({
                    "type": "text",
                    "text": {"content": chunk},
                    "annotations": {"color": "default"}
                })

            rich_text_parts.append({
                "type": "text",
                "text": {"content": f" (Page {page})"},
                "annotations": {"italic": True, "color": notion_color}
            })

            paragraph_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text_parts
                }
            }

            for s in sections:
                if s["section"] == sec:
                    s["paragraphs"].append(paragraph_block)
                    break

    # Combine all blocks together
    all_blocks = []
    for s in sections:
        all_blocks.append(s["heading_block"])
        all_blocks.extend(s["paragraphs"])

    return sections, all_blocks