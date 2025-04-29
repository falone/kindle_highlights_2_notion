def get_cover_search_url(title, author):
    query = f"{title} {author} cover".replace(" ", "+")
    return f"https://www.google.com/search?tbm=isch&q={query}"
