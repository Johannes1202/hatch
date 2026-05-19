from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
import json, os, secrets, httpx, re
from urllib.parse import urljoin

app = FastAPI()
DATA_FILE = "/data/shortcuts.json"
VERSION = "0.1.0"
PASSWORD = os.environ.get("HATCH_PASSWORD", "changeme")
TOKEN = secrets.token_hex(32)

_favicon_cache: dict[str, tuple[bytes, str]] = {}

DEFAULT_SHORTCUTS = {
    "profiles": [{
        "id": "home",
        "name": "Home",
        "shortcuts": [
            {"id": "d001", "name": "YouTube", "url": "https://youtube.com"},
            {"id": "d002", "name": "GitHub", "url": "https://github.com"},
            {"id": "d003", "name": "Reddit", "url": "https://reddit.com"}
        ]
    }]
}

def load():
    if not os.path.exists(DATA_FILE):
        return DEFAULT_SHORTCUTS
    with open(DATA_FILE) as f:
        raw = json.load(f)
    if isinstance(raw, list):
        return {"profiles": [{"id": "home", "name": "Home", "shortcuts": raw}]}
    raw.pop("activeProfile", None)
    return raw

def save(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def authed(request: Request):
    return request.headers.get("X-Token") == TOKEN

@app.post("/api/login")
async def login(request: Request):
    body = await request.json()
    if body.get("password") == PASSWORD:
        return {"token": TOKEN}
    return JSONResponse({"error": "wrong password"}, status_code=401)

@app.get("/api/shortcuts")
def get_data(request: Request):
    if not authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return load()

@app.put("/api/shortcuts")
async def save_data(request: Request):
    if not authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    body = await request.json()
    save(body)
    return {"ok": True}

NOTES_FILE = "/data/notes.json"
CONFIG_FILE = "/data/config.json"

@app.get("/api/config")
def get_config(request: Request):
    if not authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)

@app.put("/api/config")
async def save_config(request: Request):
    if not authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    body = await request.json()
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(body, f)
    return {"ok": True}

@app.get("/api/notes")
def get_notes(request: Request):
    if not authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE) as f:
            return json.load(f)
    notes = {"tabs": [{"id": "default", "name": "Notes", "content": ""}], "active_tab": "default"}
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)
    return notes

@app.put("/api/notes")
async def save_notes(request: Request):
    if not authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    body = await request.json()
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
    with open(NOTES_FILE, "w") as f:
        json.dump(body, f)
    return {"ok": True}

@app.get("/api/weather")
async def get_weather(request: Request, lat: str = None, lon: str = None, city: str = None):
    if not authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            city_name = ""
            if city:
                geo = (await client.get(
                    f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
                )).json()
                results = geo.get("results", [])
                if not results:
                    return JSONResponse({"error": "city not found"}, status_code=404)
                w_lat = str(results[0]["latitude"])
                w_lon = str(results[0]["longitude"])
                city_name = results[0].get("name", city)
            elif lat and lon:
                w_lat, w_lon = lat, lon
            else:
                geo = (await client.get("https://ipapi.co/json/")).json()
                w_lat = str(geo["latitude"])
                w_lon = str(geo["longitude"])
                city_name = geo.get("city", "")
            w = (await client.get(
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={w_lat}&longitude={w_lon}"
                f"&current=temperature_2m,apparent_temperature,weather_code"
                f"&timezone=auto"
            )).json()
            cur = w["current"]
            if not city_name:
                tz = w.get("timezone", "")
                city_name = tz.split("/")[-1].replace("_", " ") if "/" in tz else ""
            return {
                "temp": round(cur["temperature_2m"]),
                "feels": round(cur["apparent_temperature"]),
                "code": cur["weather_code"],
                "city": city_name
            }
    except Exception:
        return JSONResponse({"error": "fetch failed"}, status_code=502)

@app.get("/api/favicon")
async def proxy_favicon(url: str):
    if url in _favicon_cache:
        content, ct = _favicon_cache[url]
        return Response(content=content, media_type=ct, headers={"Cache-Control": "max-age=86400"})

    base = url.rstrip("/")
    async with httpx.AsyncClient(verify=False, timeout=5, follow_redirects=True) as client:
        try:
            r = await client.get(base + "/favicon.ico")
            if r.status_code == 200 and len(r.content) > 0:
                ct = r.headers.get("content-type", "image/x-icon")
                _favicon_cache[url] = (r.content, ct)
                return Response(content=r.content, media_type=ct, headers={"Cache-Control": "max-age=86400"})
        except Exception:
            pass

        try:
            r = await client.get(base + "/")
            if r.status_code == 200:
                final_base = str(r.url)
                html = r.text[:10000]
                for match in re.finditer(r"<link([^>]+)>", html, re.IGNORECASE):
                    attrs = match.group(1)
                    if not re.search(r"rel=[\"'][^\"']*icon[^\"']*[\"']", attrs, re.IGNORECASE):
                        continue
                    href_m = re.search(r"href=[\"']([^\"']+)[\"']", attrs, re.IGNORECASE)
                    if not href_m:
                        continue
                    favicon_url = urljoin(final_base, href_m.group(1))
                    try:
                        fr = await client.get(favicon_url)
                        if fr.status_code == 200 and len(fr.content) > 0:
                            ct = fr.headers.get("content-type", "image/x-icon")
                            _favicon_cache[url] = (fr.content, ct)
                            return Response(content=fr.content, media_type=ct, headers={"Cache-Control": "max-age=86400"})
                    except Exception:
                        pass
        except Exception:
            pass

    return Response(status_code=404)


SUGGEST_URLS = {
    'google':     'https://suggestqueries.google.com/complete/search?client=firefox&q={}',
    'duckduckgo': 'https://duckduckgo.com/ac/?q={}&type=list',
    'brave':      'https://search.brave.com/api/suggest?q={}',
    'bing':       'https://api.bing.com/osjson.aspx?query={}',
}

@app.get('/api/suggest')
async def suggest(request: Request, q: str = '', engine: str = 'google'):
    if not authed(request):
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    if not q.strip():
        return JSONResponse([])
    url_template = SUGGEST_URLS.get(engine, SUGGEST_URLS['google'])
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(url_template.format(httpx.URL(q)), headers={'User-Agent': 'Mozilla/5.0'})
            data = r.json()
            if isinstance(data, list) and len(data) >= 2 and isinstance(data[1], list):
                return JSONResponse(data[1][:8])
    except Exception:
        pass
    return JSONResponse([])

@app.get('/api/version')
def get_version():
    return {'version': VERSION}

app.mount("/", StaticFiles(directory="/app/static", html=True), name="static")