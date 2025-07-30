import os
import pickle
from fastapi import FastAPI, Request, HTTPException, Query, Path
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from urllib.parse import unquote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from bs4 import BeautifulSoup
import urllib.parse
import sys
import generator
import json
from lxml import etree as ET  # Use lxml for robust XML parsing
ANIME_TITLE_CACHE_FILE = "anime_title_cache.json"

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Utility for cookies
COOKIES_FILE = "cookies.pkl"

def get_cookies():
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, 'rb') as f:
            return pickle.load(f)
    return None

def save_cookies(driver):
    with open(COOKIES_FILE, 'wb') as f:
        pickle.dump(driver.get_cookies(), f)

def set_cookies(driver, cookies):
    for cookie in cookies:
        driver.add_cookie(cookie)

def fetch_download_links(anime_session, episode_session):
    import re
    url = f"https://animepahe.ru/play/{anime_session}/{episode_session}"
    cookies = get_api_cookies()
    jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies:
        jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
    try:
        resp = requests.get(url, cookies=jar, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = []
        dropdowns = soup.select('.dropdown-menu')
        print(f"[DEBUG] Found {len(dropdowns)} .dropdown-menu elements on {url}")
        for menu in dropdowns:
            a_tags = menu.find_all('a', class_='dropdown-item')
            print(f"[DEBUG] Found {len(a_tags)} <a.dropdown-item> in one dropdown-menu")
            for a in a_tags:
                text = a.get_text(strip=True)
                href = a.get('href')
                print(f"[DEBUG] Link text: '{text}' href: {href}")
                if not href:
                    continue
                # Only allow links that are direct downloads (pahe.win, kwik.si, gdrive, drive.google.com)
                if not (('pahe.win' in href) or ('kwik.si' in href) or ('gdrive' in href) or ('drive.google.com' in href)):
                    continue
                fansub, quality, size = None, None, None
                match = re.match(r"(.+?)\s*[·\-]\s*([0-9]+p)\s*\(([^)]+)\)", text)
                if match:
                    fansub, quality, size = match.groups()
                else:
                    parts = re.split(r"[·\-]", text)
                    if len(parts) >= 2:
                        fansub = parts[0].strip()
                        rest = parts[1].strip()
                        q_match = re.match(r"([0-9]+p)\s*\(([^)]+)\)", rest)
                        if q_match:
                            quality, size = q_match.groups()
                        else:
                            quality = rest
                # Only include links with a quality and size (likely real downloads)
                if not quality or not size:
                    continue
                links.append({
                    "href": href,
                    "text": text,
                    "fansub": fansub,
                    "quality": quality,
                    "size": size
                })
        return links
    except Exception as e:
        print(f"[ERROR] requests download link extraction: {e}")
        return []

def get_api_cookies(force_refresh=False):
    # Try to load cookies from file
    if not force_refresh and os.path.exists(COOKIES_FILE):
        try:
            if os.path.getsize(COOKIES_FILE) == 0:
                raise EOFError('cookies.pkl is empty')
            with open(COOKIES_FILE, 'rb') as f:
                return pickle.load(f)
        except (EOFError, pickle.UnpicklingError) as e:
            print(f"[DEBUG] Cookie load failed: {e}, deleting cookies.pkl and regenerating...")
            try:
                os.remove(COOKIES_FILE)
            except Exception:
                pass
            # fall through to regenerate
    # Otherwise, use undetected-chromedriver to get cookies
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    driver.get("https://animepahe.ru/")
    import time
    time.sleep(10)  # Wait for DDoS-Guard JS to complete
    cookies = driver.get_cookies()
    driver.quit()
    with open(COOKIES_FILE, 'wb') as f:
        pickle.dump(cookies, f)
    return cookies

# --- Kwik/Pahe direct link generator ---
def _deobfuscate_script(obfuscated_string, key_string, offset, base):
    def _decode_base(wu, xe, q):
        chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/+"
        h = chars[:xe]
        i = chars[:q]
        j = 0
        for idx, char_val in enumerate(reversed(wu)):
            if char_val in h:
                j += h.index(char_val) * (xe ** idx)
        if j == 0: return "0"
        k = ""
        while j > 0:
            k = i[j % q] + k
            j //= q
        return k or "0"
    try:
        delimiter = key_string[base]
        parts = obfuscated_string.split(delimiter)
        key_map = {char: str(i) for i, char in enumerate(key_string)}
        result_chars = []
        for s in parts:
            if not s: continue
            for char, index in key_map.items():
                s = s.replace(char, index)
            decoded_val_str = _decode_base(s, base, 10)
            char_code = int(decoded_val_str) - offset
            result_chars.append(chr(char_code))
        final_string = "".join(result_chars)
        return urllib.parse.unquote(final_string)
    except Exception as e:
        print(f"[Module Error] Deobfuscation failed: {e}", file=sys.stderr)
        return ""

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

def get_direct_link(pahe_url):
    # Try cloudscraper first
    if HAS_CLOUDSCRAPER:
        session = cloudscraper.create_scraper()
        try:
            print(f"[DEBUG] Fetching pahe.win URL with cloudscraper: {pahe_url}")
            response = session.get(pahe_url, timeout=15)
            print(f"[DEBUG] pahe.win status: {response.status_code}")
            print(f"[DEBUG] pahe.win response (first 500 chars): {response.text[:500]}")
            response.raise_for_status()
            kwik_url_match = re.search(r'\$\("a\\.redirect"\)\\.attr\("href","(https://kwik\\.si/f/[^\"]+)"\)', response.text)
            if kwik_url_match:
                kwik_url = kwik_url_match.group(1)
                print(f"[DEBUG] Found kwik.si URL: {kwik_url}")
                direct = _get_link_from_kwik(kwik_url, session)
                print(f"[DEBUG] Final direct link: {direct}")
                return direct
            else:
                print(f"[DEBUG] cloudscraper could not find kwik.si link in HTML.")
        except Exception as e:
            print(f"[Module Error] cloudscraper failed: {e}", file=sys.stderr)
    # Fallback to Selenium
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        print(f"[DEBUG] Fetching pahe.win URL with Selenium: {pahe_url}")
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = uc.Chrome(options=options)
        driver.get(pahe_url)
        # Wait for the redirect link to appear in the DOM
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.redirect'))
        )
        # Get the kwik.si link from the href attribute
        kwik_url = driver.find_element(By.CSS_SELECTOR, 'a.redirect').get_attribute('href')
        print(f"[DEBUG] Found kwik.si URL with Selenium: {kwik_url}")
        driver.quit()
        if kwik_url and 'kwik.si' in kwik_url:
            session = requests.Session()
            session.headers.update({'User-Agent': 'okhttp/5.0.0-alpha.14'})
            direct = _get_link_from_kwik(kwik_url, session)
            print(f"[DEBUG] Final direct link: {direct}")
            return direct
        else:
            print(f"[DEBUG] Selenium could not find kwik.si link in DOM.")
    except Exception as e:
        print(f"[Module Error] Selenium fallback failed: {e}", file=sys.stderr)
    print(f"[DEBUG] get_direct_link failed for {pahe_url}")
    return None

def _get_link_from_kwik(kwik_url, session):
    try:
        print(f"[DEBUG] Fetching kwik.si URL: {kwik_url}")
        kwik_response = session.get(kwik_url, timeout=15)
        print(f"[DEBUG] kwik.si status: {kwik_response.status_code}")
        print(f"[DEBUG] kwik.si response (first 500 chars): {kwik_response.text[:500]}")
        kwik_response.raise_for_status()
        html_content = kwik_response.text
        pattern = re.compile(r'eval\\(function\\(.*?\\}\("(.+?)",\\d+,"(.+?)",(\\d+),(\\d+),.*?\\)\\)', re.DOTALL)
        match = pattern.search(html_content)
        if not match:
            print("[Module Error] Could not find obfuscated script on Kwik page.", file=sys.stderr)
            return None
        params = {
            'obfuscated_string': match.group(1),
            'key_string': match.group(2),
            'offset': int(match.group(3)),
            'base': int(match.group(4))
        }
        print(f"[DEBUG] Deobfuscating script with params: {params}")
        decoded_script = _deobfuscate_script(**params)
        print(f"[DEBUG] Decoded script (first 500 chars): {decoded_script[:500]}")
        if not decoded_script:
            return None
        form_action_match = re.search(r'action="([^"]+)"', decoded_script)
        token_match = re.search(r'name="_token" value="([^"]+)"', decoded_script)
        if not (form_action_match and token_match):
            print("[Module Error] Could not parse form data from decoded script.", file=sys.stderr)
            return None
        post_url = form_action_match.group(1)
        token = token_match.group(1)
        print(f"[DEBUG] POSTing to: {post_url} with token: {token}")
        payload = {'_token': token}
        post_headers = {'referer': kwik_url}
        download_response = session.post(post_url, data=payload, headers=post_headers, allow_redirects=False)
        print(f"[DEBUG] POST response headers: {download_response.headers}")
        return download_response.headers.get('Location')
    except Exception as e:
        print(f"[Module Error] Request failed during Kwik processing: {e}", file=sys.stderr)
        return None

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

# Load cache at startup
try:
    with open(ANIME_TITLE_CACHE_FILE, 'r', encoding='utf-8') as f:
        anime_title_cache = json.load(f)
except Exception:
    anime_title_cache = {}

def get_anime_title(anime_session):
    # Only use the file-based cache, never fetch from animepahe
    if anime_session in anime_title_cache:
        print(f"[DEBUG] Cache hit for {anime_session}: {anime_title_cache[anime_session]}")
        return anime_title_cache[anime_session]
    print(f"[DEBUG] No cache entry for {anime_session}. Please add it to anime_title_cache.json.")
    return None
# (Comment for user: To add new animeid-title pairs, edit anime_title_cache.json manually. Format: {"animeid": "Anime Title", ...})

def update_anime_title_cache(anime_session, anime_title):
    if anime_session and anime_title and anime_session not in anime_title_cache:
        anime_title_cache[anime_session] = anime_title
        with open(ANIME_TITLE_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(anime_title_cache, f, ensure_ascii=False, indent=2)
        print(f"[DEBUG] Auto-cached {anime_session}: {anime_title}")

# Home route placeholder
@app.get("/", response_class=HTMLResponse)
def index(request: Request, page: int = Query(1, ge=1)):
    url = f"https://animepahe.ru/api?m=airing&page={page}"
    print(f"[DEBUG] Fetching: {url}")
    def make_request_with_cookies(cookies):
        jar = requests.cookies.RequestsCookieJar()
        for cookie in cookies:
            jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
        return requests.get(url, timeout=10, cookies=jar)
    cookies = get_api_cookies()
    try:
        resp = make_request_with_cookies(cookies)
        print(f"[DEBUG] Status: {resp.status_code}")
        print(f"[DEBUG] Response: {resp.text[:500]}")
        if resp.status_code in (401, 403):
            print("[DEBUG] Cookies expired or invalid, regenerating...")
            cookies = get_api_cookies(force_refresh=True)
            resp = make_request_with_cookies(cookies)
            print(f"[DEBUG] Retry Status: {resp.status_code}")
            print(f"[DEBUG] Retry Response: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        animes = []
        last_page = data.get("last_page", 1)
        if data.get("data"):
            print(f"[DEBUG] Found {len(data['data'])} anime entries.")
            for item in data["data"]:
                anime_title = item.get("anime_title")
                anime_session = item.get("anime_session")
                update_anime_title_cache(anime_session, anime_title)
                slug_title = slugify(anime_title) if anime_title else "anime"
                animes.append({
                    "anime_title": anime_title,
                    "episode": item.get("episode"),
                    "fansub": item.get("fansub"),
                    "snapshot": item.get("snapshot"),
                    "anime_session": anime_session,
                    "session": item.get("session"),
                    "slug_title": slug_title
                })
        else:
            print("[DEBUG] No 'data' field in response or it's empty.")
            animes = []
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        animes = []
        last_page = 1

    # Fetch upcoming releases from SubsPlease
    upcoming_releases = []
    try:
        subsplease_url = "https://subsplease.org/api/?f=schedule&h=true&tz=Asia/Dhaka"
        sp_resp = requests.get(subsplease_url, timeout=10)
        if sp_resp.status_code == 200:
            sp_data = sp_resp.json()
            for anime in sp_data.get("schedule", []):
                upcoming_releases.append({
                    "title": anime["title"],
                    "time": anime["time"],
                    "aired": anime["aired"],
                    "image_url": "https://subsplease.org" + anime["image_url"]
                })
        else:
            print(f"[DEBUG] SubsPlease API error: {sp_resp.status_code}")
    except Exception as e:
        print(f"[ERROR] SubsPlease API: {e}")

    # Detect user IP and timezone
    user_timezone = "UTC"
    user_time = None
    try:
        # Get client IP (works with most deployments)
        client_host = request.headers.get("x-forwarded-for") or request.client.host
        if client_host and client_host != "127.0.0.1" and not client_host.startswith("192.168.") and not client_host.startswith("10."):
            geo_url = f"https://ipapi.co/{client_host}/json/"
            geo_resp = requests.get(geo_url, timeout=5)
            if geo_resp.status_code == 200:
                geo_data = geo_resp.json()
                user_timezone = geo_data.get("timezone", "UTC")
                # Get current time in user's timezone
                from datetime import datetime
                import pytz
                now = datetime.now(pytz.timezone(user_timezone))
                user_time = now.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"[ERROR] Could not determine user timezone: {e}")
        from datetime import datetime
        user_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    return templates.TemplateResponse("index.html", {"request": request, "animes": animes, "page": page, "last_page": last_page, "upcoming_releases": upcoming_releases, "user_timezone": user_timezone, "user_time": user_time})

@app.get("/external-anime/{mal_id}", response_class=HTMLResponse)
def external_anime(request: Request, mal_id: int):
    import requests as pyrequests
    anime_info = {}
    anime_image = None
    try:
        jikan_url = f"https://api.jikan.moe/v4/anime/{mal_id}"
        print(f"[DEBUG] Fetching Jikan anime info: {jikan_url}")
        jikan_resp = pyrequests.get(jikan_url, timeout=10)
        if jikan_resp.status_code == 200:
            jikan_data = jikan_resp.json()
            anime_info = jikan_data.get('data', {})
            anime_image = anime_info.get('images', {}).get('jpg', {}).get('large_image_url') or anime_info.get('images', {}).get('jpg', {}).get('image_url')
    except Exception as e:
        print(f"[ERROR] Could not fetch Jikan info: {e}")
    return templates.TemplateResponse("external_anime.html", {
        "request": request,
        "anime_info": anime_info,
        "anime_image": anime_image
    })

@app.get("/anime/{anime_session}", response_class=HTMLResponse)
def anime_details(request: Request, anime_session: str, page: int = Query(1, ge=1)):
    import requests as pyrequests
    url = f"https://animepahe.ru/api?m=release&id={anime_session}&sort=episode_desc&page={page}"
    print(f"[DEBUG] Fetching anime details: {url}")
    def make_request_with_cookies(cookies):
        jar = requests.cookies.RequestsCookieJar()
        for cookie in cookies:
            jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
        return requests.get(url, timeout=10, cookies=jar)
    cookies = get_api_cookies()
    try:
        resp = make_request_with_cookies(cookies)
        print(f"[DEBUG] Status: {resp.status_code}")
        print(f"[DEBUG] Response: {resp.text[:500]}")
        if resp.status_code in (401, 403):
            print("[DEBUG] Cookies expired or invalid, regenerating...")
            cookies = get_api_cookies(force_refresh=True)
            resp = make_request_with_cookies(cookies)
            print(f"[DEBUG] Retry Status: {resp.status_code}")
            print(f"[DEBUG] Retry Response: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        episodes = []
        last_page = data.get("last_page", 1)
        if data.get("data"):
            print(f"[DEBUG] Found {len(data['data'])} episodes.")
            for item in data["data"]:
                episodes.append({
                    "episode": item.get("episode"),
                    "duration": item.get("duration"),
                    "fansub": item.get("fansub"),
                    "snapshot": item.get("snapshot"),
                    "session": item.get("session"),
                })
        else:
            print("[DEBUG] No 'data' field in response or it's empty.")
            episodes = []
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        episodes = []
        last_page = 1

    # Use cached anime title for Jikan
    anime_title = get_anime_title(anime_session)
    anime_info = {}
    anime_image = None
    try:
        if anime_title:
            jikan_url = f"https://api.jikan.moe/v4/anime?q={pyrequests.utils.quote(anime_title)}&limit=1"
            print(f"[DEBUG] Fetching Jikan: {jikan_url}")
            jikan_resp = pyrequests.get(jikan_url, timeout=10)
            if jikan_resp.status_code == 200:
                jikan_data = jikan_resp.json()
                if jikan_data.get('data') and len(jikan_data['data']) > 0:
                    anime_info = jikan_data['data'][0]
                    anime_image = anime_info.get('images', {}).get('jpg', {}).get('large_image_url') or anime_info.get('images', {}).get('jpg', {}).get('image_url')
    except Exception as e:
        print(f"[ERROR] Could not fetch Jikan info: {e}")

    return templates.TemplateResponse("anime.html", {
        "request": request,
        "episodes": episodes,
        "anime_title": anime_title or "Anime",
        "anime_session": anime_session,
        "page": page,
        "last_page": last_page,
        "anime_info": anime_info,
        "anime_image": anime_image
    })

@app.get("/anime/{anime_session}/{episode_session}", response_class=HTMLResponse)
def episode_details(request: Request, anime_session: str, episode_session: str):
    print(f"[DEBUG] episode_details called for anime_session={anime_session}, episode_session={episode_session}")
    import requests as pyrequests
    from urllib.parse import quote
    # Fetch download links
    try:
        links = fetch_download_links(anime_session, episode_session)
        print(f"[DEBUG] Download links found: {len(links)}")
    except Exception as e:
        print(f"[DEBUG] Exception in fetch_download_links: {e}")
        links = []

    # Fetch episode info from animepahe
    episode_number = None
    episode_title = None
    anime_genres = []
    anime_description = None
    anime_image = None
    stream_first_link = None
    page = 1
    try:
        # Get episode info (need to find which episode this is)
        url = f"https://animepahe.ru/api?m=release&id={anime_session}&sort=episode_desc&page=1"
        cookies = get_api_cookies()
        jar = requests.cookies.RequestsCookieJar()
        for cookie in cookies:
            jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
        resp = requests.get(url, cookies=jar, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        found = False
        if data.get("data"):
            for item in data["data"]:
                if item.get("session") == episode_session:
                    episode_number = item.get("episode")
                    episode_title = item.get("title")
                    found = True
                    break
        # Fallback: try more pages if not found
        if not found:
            last_page = data.get("last_page", 1)
            for p in range(2, last_page+1):
                url = f"https://animepahe.ru/api?m=release&id={anime_session}&sort=episode_desc&page={p}"
                resp = requests.get(url, cookies=jar, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                if data.get("data"):
                    for item in data["data"]:
                        if item.get("session") == episode_session:
                            episode_number = item.get("episode")
                            episode_title = item.get("title")
                            found = True
                            break
                if found:
                    break
        print(f"[DEBUG] Episode number: {episode_number}, Episode title: {episode_title}")
    except Exception as e:
        print(f"[ERROR] Could not fetch episode info: {e}")

    # Use cached anime title for Jikan
    anime_title = get_anime_title(anime_session)
    anime_jikan_info = {}
    anime_genres = []
    anime_description = None
    try:
        if anime_title and isinstance(anime_title, str) and anime_title.strip():
            jikan_url = f"https://api.jikan.moe/v4/anime?q={quote(anime_title)}&limit=1"
            print(f"[DEBUG] Fetching Jikan: {jikan_url}")
            jikan_resp = pyrequests.get(jikan_url, timeout=10)
            if jikan_resp.status_code == 200:
                jikan_data = jikan_resp.json()
                if jikan_data.get('data') and len(jikan_data['data']) > 0:
                    anime_jikan_info = jikan_data['data'][0]
                    anime_image = anime_jikan_info.get('images', {}).get('jpg', {}).get('large_image_url') or anime_jikan_info.get('images', {}).get('jpg', {}).get('image_url')
                    anime_genres = [g['name'] for g in anime_jikan_info.get('genres', [])]
                    anime_description = anime_jikan_info.get('synopsis')
        else:
            print(f"[DEBUG] Skipping Jikan query due to invalid anime_title: {anime_title}")
    except Exception as e:
        print(f"[ERROR] Could not fetch Jikan info: {e}")

    # Get first streamable link
    if links:
        for link in links:
            if link.get('href') and ('pahe.win' in link['href'] or 'kwik.si' in link['href']):
                stream_first_link = link['href']
                break

    # --- Torrent Download Links from Nyaa.si ---
    torrent_links = []
    try:
        if anime_title and episode_number:
            # Prepare search query: anime title - 01 (zero-padded)
            try:
                ep_num = int(episode_number)
                ep_str = f"{ep_num:02d}"
            except Exception:
                ep_str = str(episode_number)
            base_title = anime_title.split(':')[0].strip()
            search_query = f"{base_title} - {ep_str}"
            nyaa_url = f"https://nyaa.si/?page=rss&q={quote(search_query)}&c=0_0&f=0&u=AkihitoSubsWeeklies"
            print(f"[DEBUG] Fetching Nyaa.si RSS: {nyaa_url}")
            rss_resp = pyrequests.get(nyaa_url, timeout=10)
            if rss_resp.status_code == 200:
                print(f"[DEBUG] Nyaa.si RSS raw XML:\n{rss_resp.text[:1000]}")
                root = ET.fromstring(rss_resp.content)
                ns = {'nyaa': 'https://nyaa.si/xmlns/nyaa'}
                items = root.xpath('//item')
                print(f"[DEBUG] Found {len(items)} <item> elements in RSS.")
                for item in items:
                    title = item.findtext('title') or ''
                    link = item.findtext('link') or ''
                    size = ''
                    nyaa_size = item.find('nyaa:size', namespaces=ns)
                    if nyaa_size is not None:
                        size = nyaa_size.text
                    torrent_links.append({
                        'title': title,
                        'link': link,
                        'size': size
                    })
                print(f"[DEBUG] Parsed torrent_links: {torrent_links}")
            else:
                print(f"[DEBUG] Nyaa.si RSS error: {rss_resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Could not fetch Nyaa.si torrents: {e}")

    return templates.TemplateResponse("episode.html", {
        "request": request,
        "links": links,
        "anime_session": anime_session,
        "episode_session": episode_session,
        "anime_title": anime_title or "Anime",
        "anime_image": anime_image or "https://cdn.appanimeplus.tk/img/anime/none.png",
        "episode_number": episode_number or "?",
        "episode_title": episode_title or None,
        "anime_genres": anime_genres or [],
        "anime_description": anime_description or "",
        "stream_first_link": stream_first_link,
        "torrent_links": torrent_links,  # <-- Pass to template
        # Pagination can be added if needed
    })

@app.get('/proxy-image')
def proxy_image(url: str):
    cookies = get_api_cookies()
    jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies:
        jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
    real_url = unquote(url)
    resp = requests.get(real_url, cookies=jar, stream=True)
    return StreamingResponse(resp.raw, media_type=resp.headers.get('content-type', 'image/jpeg'))

@app.get("/stream", response_class=HTMLResponse)
def stream(request: Request, url: str):
    direct_link = generator.get_direct_link(url)
    if not direct_link:
        return HTMLResponse("<h2>Could not generate direct streaming link.</h2>", status_code=500)
    return templates.TemplateResponse("stream.html", {"request": request, "direct_link": direct_link})

@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str = Query(..., min_length=1), page: int = Query(1, ge=1)):
    url = f"https://animepahe.ru/api?m=search&q={urllib.parse.quote(q)}&page={page}"
    print(f"[DEBUG] Searching anime: {url}")
    cookies = get_api_cookies()
    jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies:
        jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
    try:
        resp = requests.get(url, cookies=jar, timeout=15)
        print(f"[DEBUG] Status: {resp.status_code}")
        print(f"[DEBUG] Response: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        results = data.get('data', [])
        last_page = data.get('last_page', 1)
        # Auto-cache animeid-title pairs from search results
        for item in results:
            anime_session = item.get("session")
            anime_title = item.get("title")
            update_anime_title_cache(anime_session, anime_title)
    except Exception as e:
        print(f"[ERROR] Exception in search: {e}")
        results = []
        last_page = 1
    return templates.TemplateResponse("search.html", {"request": request, "results": results, "q": q, "page": page, "last_page": last_page})

if __name__ == "__main__":
    import uvicorn
    import socket
    import os
    base_port = int(os.getenv("PORT", 8000))
    max_attempts = 10
    for i in range(max_attempts):
        port = base_port + i
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                s.close()
                print(f"[INFO] Starting server on port {port}")
                uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
                break
            except OSError:
                print(f"[WARN] Port {port} in use, trying next...")
    else:
        print(f"[ERROR] Could not find a free port in range {base_port}-{base_port+max_attempts-1}")
