import time
import requests
from bs4 import BeautifulSoup
import os
import mysql.connector
from mysql.connector import Error

url = "https://ar.wikipedia.org/wiki/%D8%AA%D8%B5%D9%86%D9%8A%D9%81:%D8%A3%D8%B3%D9%85%D8%A7%D9%83_%D8%A7%D9%84%D8%A8%D8%AD%D8%B1_%D8%A7%D9%84%D8%A3%D8%AD%D9%85%D8%B1"
# --------------------------------------------------
try:
    DB = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "admin"),
        "database": os.getenv("DB_NAME", "FISH"),
        "port": int(os.getenv("DB_PORT", 3306)),
    }
    connection = mysql.connector.connect(**DB)
    cursor = connection.cursor()

except Error as e:
    print(f" {e}")
# ------------------------------------------------
HEADERS = {
    "User-Agent": "Edu_Fish_project (+https://github.com/ElafMohammed3/Fish/blob/main/scraping/scraping-info.html) - Educational use; data will be documented",
    "From": 'elafmohammedalhalili@gmail.com' , 
    "Accept": "text/html"
    }

def polite_sleep():
    """Simple polite wait between requests."""
    time.sleep(1.5)

def get_article_links(url, max_links=52):
    """Return full article URLs found in a Wikipedia category page (no namespace links)."""
    links = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print("Category page fetch failed:", r.status_code)
            return links
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/wiki/") and ":" not in href:
                full = "https://ar.wikipedia.org" + href
                if full not in links:
                    links.append(full)
                if len(links) >= max_links:
                    break
    except Exception as e:
        print("Error fetching category links:", e)
    return links

def scrape_article(article_url):
    """Return (title, first_paragraph, image_bytes or None)."""
    try:
        r = requests.get(article_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print("Article fetch failed:", article_url, r.status_code)
            return None, None, None
        soup = BeautifulSoup(r.text, "html.parser")

        # Title
        title_tag = soup.find(id="firstHeading")
        title = title_tag.get_text(strip=True) if title_tag else None

        # First meaningful paragraph
        content = soup.find(id="mw-content-text")
        first_para = None
        if content:
            p = content.find("p")
            while p and not p.get_text(strip=True):
                p = p.find_next_sibling("p")
            if p:
                first_para = p.get_text(strip=True)

        # First image in infobox or content
        image_bytes = None
        # try infobox image
        infobox = soup.find("table", class_="infobox")
        img_tag = None
        if infobox:
            img_tag = infobox.find("img")
        if not img_tag:
            img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            src = img_tag["src"]
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = "https://ar.wikipedia.org" + src
            try:
                img_resp = requests.get(src, headers=HEADERS, timeout=15)
                if img_resp.status_code == 200:
                    image_bytes = img_resp.content
            except Exception:
                image_bytes = None

        return title, first_para, image_bytes

    except Exception as e:
        print("Error scraping article:", e)
        return None, None, None

def save_to_db(name, description, source_url, image_bytes):
    """Insert record into fish table in DB."""
    try:
        query = """
        INSERT INTO fish (name, description, source_url, image)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, description, source_url, image_bytes))
        connection.commit()
        print("saved ",name)
        return True, "saved"
    except Exception as e:
        # handle duplicate name (unique constraint) or other errors
        return False, f" {e}"

def run(url, limit=10):
    print("Fetching links from category...")
    links = get_article_links(url, max_links=52)
    print("Found links:", len(links))

    for i, url in enumerate(links, start=1):
        print(f"\n[{i}/{len(links)}] Processing:", url)
        polite_sleep()

        title, para, img = scrape_article(url)
        if not title:
            print("  Skipped: no title")
            continue
        desc = para or "No description available"
        print("  Title:", title)
        print("  Desc len:", len(desc))
        print("  Image bytes:", "yes" if img else "no")

        success, msg = save_to_db(title, desc, url, img)
        if success:
            print("  Saved to DB")
        else:
            print("  DB error:", msg)

        polite_sleep()


if __name__ == "__main__":
    run(url,limit=10) 
    cursor.close()
    connection.close()