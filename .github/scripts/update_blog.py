import html
import re
from datetime import datetime

import feedparser


def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y.%m.%d")
    except ValueError:
        return date_str


def format_post(title, link, published):
    title = re.sub(r"\s+", " ", html.unescape(title)).strip()
    title = title.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
    date = format_date(published)
    return f"- [{title}]({link})" + (f" · {date}" if date else "")


def create_blog_list(feed_url, max_posts=6):
    feed = feedparser.parse(feed_url)
    posts = [
        format_post(entry["title"], entry["link"], entry.get("published", ""))
        for entry in feed.entries[:max_posts]
        if entry.get("title") and entry.get("link")
    ]
    if not posts:
        raise ValueError("RSS에 유효한 글이 없어 기존 목록을 유지합니다.")
    return "\n".join(posts) + "\n"


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
    update_readme("README.md", create_blog_list("https://hskhsmm.tistory.com/rss"))
