import html
import re
from datetime import datetime

import feedparser


def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y.%m.%d")
    except ValueError:
        return date_str


def get_thumbnail(entry):
    thumbnails = entry.get("media_thumbnail", [])
    if thumbnails:
        return thumbnails[0].get("url", "")
    for enclosure in entry.get("enclosures", []):
        if enclosure.get("type", "").startswith("image/"):
            return enclosure.get("url", "")
    content = entry.get("description") or entry.get("summary", "")
    match = re.search(r'''<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["']''', content, re.I)
    return html.unescape(match.group(1)) if match else ""


def format_post(title, link, published, thumbnail=""):
    title = re.sub(r"\s+", " ", html.unescape(title)).strip()
    title = html.escape(title, quote=True).replace("|", "&#124;")
    link = html.escape(link, quote=True).replace("|", "&#124;")
    date = html.escape(format_date(published), quote=True)
    image = ""
    if thumbnail:
        thumbnail = html.escape(thumbnail, quote=True).replace("|", "&#124;")
        image = f'<a href="{link}"><img src="{thumbnail}" width="100" alt="{title}"></a>'
    details = f'<a href="{link}"><strong>{title}</strong></a>' + (f"<br/><sub>{date}</sub>" if date else "")
    return (
        '<tr>\n'
        f'  <td width="120" align="center">{image}</td>\n'
        f'  <td align="left">{details}</td>\n'
        '</tr>'
    )


def create_blog_table(feed_url, max_posts=6):
    feed = feedparser.parse(feed_url)
    posts = [
        format_post(entry["title"], entry["link"], entry.get("published", ""), get_thumbnail(entry))
        for entry in feed.entries[:max_posts]
        if entry.get("title") and entry.get("link")
    ]
    if not posts:
        raise ValueError("RSS에 유효한 글이 없어 기존 목록을 유지합니다.")
    return '<table>\n' + '\n'.join(posts) + '\n</table>\n'


def update_readme(readme_path, posts_content):
    with open(readme_path, encoding="utf-8") as source:
        content = source.read()
    start_marker = "<!-- BLOG-POST-LIST:START -->"
    end_marker = "<!-- BLOG-POST-LIST:END -->"
    start = content.find(start_marker)
    end = content.find(end_marker)
    if start == -1 or end < start:
        raise ValueError("README에서 블로그 목록 마커를 찾을 수 없습니다.")
    content = content[:start + len(start_marker)] + "\n" + posts_content + content[end:]
    with open(readme_path, "w", encoding="utf-8") as destination:
        destination.write(content)
    print("README.md updated successfully.")


if __name__ == "__main__":
    update_readme("README.md", create_blog_table("https://hskhsmm.tistory.com/rss"))
