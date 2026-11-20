import asyncio
import os
import re
import aiohttp

OUTPUT_DIR = "assets/items"
API_URL = "https://stealabrainrot.fandom.com/api.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://stealabrainrot.fandom.com/",
}

ITEMS = [
    {"id": "esok_sekolah", "queries": ["Esok Sekolah"]},
    {"id": "agarini_la_palini", "queries": ["Agarini La Palini"]},
    {"id": "abbysaloco", "queries": ["Abbysaloco", "Abyssaloco"]},
    {"id": "los_mobills", "queries": ["Los Mobills", "Los Mobilis"]},
    {"id": "rainbow_slap", "queries": ["Rainbow Slap"]},
    {"id": "los_burritos", "queries": ["Los Burritos"]},
    {"id": "los_puggles", "queries": ["Los Puggles"]},
    {"id": "orcaledon", "queries": ["Orcaledon"]},
    {"id": "ketupat_kepat", "queries": ["Ketupat Kepat"]},
    {"id": "mieteteira", "queries": ["Mieteteira Bicicleteira"]},
    {"id": "los_candies", "queries": ["Los Candies", "Los Candles"]},
    {"id": "demon_head", "queries": ["Demon Head"]},
    {"id": "lavadorito", "queries": ["Lavadorito Spinito"]},
    {"id": "crystal_slap", "queries": ["Crystal Slap"]},
    {"id": "ying_yang_lamp", "queries": ["Ying Yang Lamp", "Yin Yang Lamp"]},
    {"id": "bloodmoon_slap", "queries": ["Bloodmoon Slap"]},
    {"id": "cupid_wings", "queries": ["Cupid Wings"]},
    {"id": "los_tangcitos", "queries": ["Los Tangcitos", "Los Tang Tang"]},
    {"id": "waverider", "queries": ["Waverider"]},
    {"id": "witch_broom", "queries": ["Witch Broom"]},
    {"id": "blackhole_bomb", "queries": ["Blackhole Bomb", "Black Hole Bomb"]},
    {"id": "mi_gatito", "queries": ["Mi Gatito"]},
    {"id": "camera_ramen", "queries": ["Camera Ramen"]},
    {"id": "ventollero", "queries": ["Ventollero Pavon", "Ventollero Pavonero"]},
    {"id": "yes_my_examine", "queries": ["Yes My Examine"]},
    {"id": "los_primos", "queries": ["Los Primos"]},
    {"id": "air_strike", "queries": ["Air Strike", "Airstrike"]},
    {"id": "candy_sentry", "queries": ["Candy Sentry"]},
    {"id": "los_planitos", "queries": ["Los Planitos"]},
    {"id": "la_summer_grande", "queries": ["La Summer Grande"]},
    {"id": "honey_honey_bear", "queries": ["Honey Honey Bear"]},
    {"id": "garama", "queries": ["Garama and Madundung"]},
    {"id": "ketchuru", "queries": ["Ketchuru and Musturu"]},
    {"id": "quesadilo", "queries": ["Quesadilo Vampiro", "Quesadillo Vampiro"]},
    {"id": "cash_or_card", "queries": ["Cash or Card"]},
    {"id": "noodle_noodle", "queries": ["Noodle Noodle P", "Noodle Noodle Poodle"]},
    {"id": "phantom_slap", "queries": ["Phantom Slap"]},
    {"id": "la_jolly_grande", "queries": ["La Jolly Grande"]},
    {"id": "sammyni_fattini", "queries": ["Sammyni Fattini"]},
    {"id": "eviledon", "queries": ["Eviledon"]},
    {"id": "w_or_l", "queries": ["W or L"]},
    {"id": "lava_blaster", "queries": ["Lava Blaster"]},
    {"id": "los_tictacs", "queries": ["Los Tictacs"]},
    {"id": "los_sweethearts", "queries": ["Los Sweethearts"]},
    {"id": "john_doe", "queries": ["John Doe"]},
    {"id": "pizza_and_ranch", "queries": ["Pizza and Ranch"]},
    {"id": "los_jolly_comb", "queries": ["Los Jolly Combination"]},
    {"id": "popcuru", "queries": ["Popcuru and Fizzuru"]},
    {"id": "los_mariachis", "queries": ["Los Mariachis"]},
    {"id": "quackini", "queries": ["Quackini Snackini"]},
    {"id": "santas_sleigh", "queries": ["Santas Sleigh", "Santa's Sleigh"]},
    {"id": "la_secret_comb", "queries": ["La Secret Combination"]},
    {"id": "celestial_pegasus", "queries": ["Celestial Pegasus"]},
    {"id": "scorpino_coaster", "queries": ["Scorpino Coaster"]},
]

SKIP_KEYWORDS = ("wiki", "icon", "logo", "coin", "cash", "button", "banner", "placeholder")


def clean_wikia_url(url: str) -> str:
    # Убираем обрезку ревизии при необходимости, оставляя прямой PNG/WebP
    return re.sub(r"/revision/latest/scale-to-width-down/\d+", "/revision/latest", url)


async def get_page_image(session: aiohttp.ClientSession, title: str) -> str | None:
    params = {
        "action": "query",
        "titles": title,
        "redirects": 1,
        "prop": "pageimages|images",
        "pithumbsize": 500,
        "imlimit": 20,
        "format": "json",
    }
    async with session.get(API_URL, params=params) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()

    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "missing" in page:
            continue
        thumb = page.get("thumbnail", {}).get("source")
        if thumb:
            return clean_wikia_url(thumb)

        # Запасной путь: берем подходящий файл из списка картинок на странице
        for im in page.get("images", []):
            im_title = im.get("title", "")
            low = im_title.lower()
            if any(k in low for k in SKIP_KEYWORDS):
                continue
            if not low.endswith((".png", ".webp", ".jpg", ".jpeg")):
                continue
            info_params = {
                "action": "query",
                "titles": im_title,
                "prop": "imageinfo",
                "iiprop": "url",
                "format": "json",
            }
            async with session.get(API_URL, params=info_params) as iresp:
                if iresp.status == 200:
                    idata = await iresp.json()
                    for ipage in idata.get("query", {}).get("pages", {}).values():
                        ii = ipage.get("imageinfo", [])
                        if ii and ii[0].get("url"):
                            return clean_wikia_url(ii[0]["url"])
    return None


async def search_title(session: aiohttp.ClientSession, query: str) -> str | None:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 3,
        "format": "json",
    }
    async with session.get(API_URL, params=params) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
    results = data.get("query", {}).get("search", [])
    return results[0]["title"] if results else None


async def download_one(session: aiohttp.ClientSession, sem: asyncio.Semaphore, item: dict):
    out_path = os.path.join(OUTPUT_DIR, f"{item['id']}.png")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 500:
        print(f"[SKIP] {item['id']}.png уже скачан")
        return True

    async with sem:
        img_url = None
        for q in item["queries"]:
            img_url = await get_page_image(session, q)
            if img_url:
                break

        if not img_url:
            found_title = await search_title(session, item["queries"][0])
            if found_title:
                img_url = await get_page_image(session, found_title)

        if not img_url:
            print(f"[MISS] {item['id']} ({item['queries'][0]}) — не найдено на вики")
            return False

        for attempt in range(3):
            try:
                async with session.get(img_url) as r:
                    if r.status == 200:
                        raw = await r.read()
                        if len(raw) > 500:
                            with open(out_path, "wb") as f:
                                f.write(raw)
                            print(f"[OK]   {item['id']}.png")
                            return True
            except Exception:
                await asyncio.sleep(0.8 * (attempt + 1))

        print(f"[FAIL] {item['id']} — ошибка загрузки {img_url}")
        return False


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sem = asyncio.Semaphore(5)
    connector = aiohttp.TCPConnector(ssl=False)
    timeout = aiohttp.ClientTimeout(total=25)

    async with aiohttp.ClientSession(headers=HEADERS, connector=connector, timeout=timeout) as session:
        tasks = [download_one(session, sem, item) for item in ITEMS]
        results = await asyncio.gather(*tasks)

    ok_count = sum(1 for r in results if r)
    print(f"\nГотово: {ok_count} из {len(ITEMS)} сохранено в {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
