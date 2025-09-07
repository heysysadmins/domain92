from PIL import Image
from io import BytesIO
import time as _time
import re
import random
import string
from art import *
import freedns
import sys
import argparse
import pytesseract
import copy
from PIL import ImageFilter
import os
import platform
from importlib.metadata import version
import lolpython
import asyncio
import aiohttp
from functools import partial

# ---------- CLI ----------
parser = argparse.ArgumentParser(
    description="Automatically creates links for an ip on freedns (async aiohttp version)"
)
parser.add_argument(
    "-v",
    "--version",
    action="version",
    version="domain92 installed with version: " + str(version("domain92")),
    help="show the installed version of this package (domain92)",
)
parser.add_argument("--number", help="number of links to generate", type=int)
parser.add_argument("--ip", help="ip to use", type=str)
parser.add_argument("--webhook", help="webhook url, do none to not ask", type=str)
parser.add_argument(
    "--proxy", help="use if you get ip blocked.", type=str, default="none"
)
parser.add_argument(
    "--use_tor",
    help="use a local tor proxy to avoid ip blocking. See wiki for instructions.",
    action="store_true",
)
parser.add_argument(
    "--silent",
    help="no output other than showing you the captchas",
    action="store_true",
)
parser.add_argument(
    "--outfile", help="output file for the domains", type=str, default="domainlist.txt"
)
parser.add_argument(
    "--type", help="type of record to make, default is A", type=str, default="A"
)
parser.add_argument(
    "--pages",
    help="range of pages to scrape, see readme for more info (default is first ten)",
    type=str,
)
parser.add_argument(
    "--subdomains",
    help="comma separated list of subdomains to use, default is random",
    type=str,
    default="random",
)
parser.add_argument(
    "--auto",
    help="uses tesseract to automatically solve the captchas. tesseract is now included, and doesn't need to be installed seperately",
    action="store_true",
)
parser.add_argument("--single_tld", help="only create links for a single tld", type=str)
args = parser.parse_args()

ip = args.ip

if not args.silent:
    lolpython.lol_py(text2art("domain92"))
    print("made with <3 by Cbass92")
    _time.sleep(1)


def checkprint(input):
    global args
    if not args.silent:
        print(input)


# ---------- freedns client ----------
client = freedns.Client()
checkprint("client initialized")


# ---------- tesseract setup ----------
def get_data_path():
    script_dir = os.path.dirname(__file__)
    checkprint("checking os")
    if platform.system() == "Windows":
        filename = os.path.join(script_dir, "data", "windows", "tesseract")
    elif platform.system() == "Linux":
        filename = os.path.join(script_dir, "data", "tesseract-linux")
    else:
        print(
            "Unsupported OS. This could cause errors with captcha solving. Please install tesseract manually."
        )
        return None
    os.environ["TESSDATA_PREFIX"] = os.path.join(script_dir, "data")
    return filename


path = get_data_path()
if path:
    pytesseract.pytesseract.tesseract_cmd = path
    checkprint(f"Using tesseract executable: {path}")
else:
    checkprint("No valid tesseract file for this OS.")


# ---------- globals ----------
domainlist = []
domainnames = []
checkprint("getting ip list")
# iplist will be fetched async later
iplist = {}

hookbool = False
webhook = ""
non_random_domain_id = None


# ---------- helpers ----------
def generate_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def denoise(img: Image.Image) -> Image.Image:
    imgarr = img.load()
    newimg = Image.new("RGB", img.size)
    newimgarr = newimg.load()
    dvs = []
    for y in range(img.height):
        for x in range(img.width):
            r = imgarr[x, y][0]
            g = imgarr[x, y][1]
            b = imgarr[x, y][2]
            if (r, g, b) == (255, 255, 255):
                newimgarr[x, y] = (r, g, b)
            elif ((r + g + b) / 3) == (112):
                newimgarr[x, y] = (255, 255, 255)
                dvs.append((x, y))
            else:
                newimgarr[x, y] = (0, 0, 0)

    backup = copy.deepcopy(newimg)
    backup = backup.load()
    for y in range(img.height):
        for x in range(img.width):
            if newimgarr[x, y] == (255, 255, 255):
                continue
            black_neighbors = 0
            for ny in range(max(0, y - 2), min(img.height, y + 2)):
                for nx in range(max(0, x - 2), min(img.width, x + 2)):
                    if backup[nx, ny] == (0, 0, 0):
                        black_neighbors += 1
            if black_neighbors <= 5:
                newimgarr[x, y] = (255, 255, 255)
    for x, y in dvs:
        black_neighbors = 0
        for ny in range(max(0, y - 2), min(img.height, y + 2)):
            for nx in range(max(0, x - 1), min(img.width, x + 1)):
                if newimgarr[nx, ny] == (0, 0, 0):
                    black_neighbors += 1
            if black_neighbors >= 5:
                newimgarr[x, y] = (0, 0, 0)
            else:
                newimgarr[x, y] = (255, 255, 255)
    width, height = newimg.size
    black_pixels = set()
    for y in range(height):
        for x in range(width):
            if newimgarr[x, y] == (0, 0, 0):
                black_pixels.add((x, y))

    for x, y in list(black_pixels):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in black_pixels:
                newimgarr[nx, ny] = 0
    backup = copy.deepcopy(newimg)
    backup = backup.load()
    for y in range(img.height):
        for x in range(img.width):
            if newimgarr[x, y] == (255, 255, 255):
                continue
            black_neighbors = 0
            for ny in range(max(0, y - 2), min(img.height, y + 2)):
                for nx in range(max(0, x - 2), min(img.width, x + 2)):
                    if backup[nx, ny] == (0, 0, 0):
                        black_neighbors += 1
            if black_neighbors <= 6:
                newimgarr[x, y] = (255, 255, 255)
    return newimg


def solve_sync(image: Image.Image) -> str:
    image = denoise(image)
    text = pytesseract.image_to_string(
        image.filter(ImageFilter.GaussianBlur(1))
        .convert("1")
        .filter(ImageFilter.RankFilter(3, 3)),
        config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 13 -l freednsocr",
    )
    text = text.strip().upper()
    checkprint("captcha solved: " + text)
    if len(text) not in (4, 5):
        checkprint("captcha doesn't match correct pattern, trying different captcha")
        # We'll return empty here so caller can fetch new captcha
        return ""
    return text


# ---------- aiohttp utility functions ----------
async def fetch_text(session: aiohttp.ClientSession, url: str, **kwargs) -> str:
    async with session.get(url, **kwargs) as resp:
        resp.raise_for_status()
        return await resp.text()


async def fetch_json(session: aiohttp.ClientSession, url: str, **kwargs) -> dict:
    async with session.get(url, **kwargs) as resp:
        resp.raise_for_status()
        return await resp.json()


async def post_json(session: aiohttp.ClientSession, url: str, json_payload: dict, **kwargs) -> dict:
    async with session.post(url, json=json_payload, **kwargs) as resp:
        # sometimes webhook returns 204 or text
        if resp.status == 204:
            return {}
        try:
            return await resp.json()
        except Exception:
            return {"status": resp.status, "text": await resp.text()}


# ---------- parsing page ranges ----------
def getpagelist(arg):
    arg = arg.strip()
    if "," in arg:
        arglist = arg.split(",")
        pagelist = []
        for item in arglist:
            if "-" in item:
                sublist = item.split("-")
                if len(sublist) == 2:
                    sp = int(sublist[0])
                    ep = int(sublist[1])
                    if sp < 1 or sp > ep:
                        checkprint("Invalid page range: " + item)
                        sys.exit()
                    pagelist.extend(range(sp, ep + 1))
                else:
                    checkprint("Invalid page range: " + item)
                    sys.exit()
        return pagelist
    elif "-" in arg:
        pagelist = []
        sublist = arg.split("-")
        if len(sublist) == 2:
            sp = int(sublist[0])
            ep = int(sublist[1])
            if sp < 1 or sp > ep:
                checkprint("Invalid page range: " + arg)
                sys.exit()
            pagelist.extend(range(sp, ep + 1))
        else:
            checkprint("Invalid page range: " + arg)
            sys.exit()
        return pagelist
    else:
        return [int(arg)]


# ---------- domain scraping (async) ----------
async def getdomains(arg: str, session: aiohttp.ClientSession):
    global domainlist, domainnames
    for sp in getpagelist(arg):
        checkprint("getting page " + str(sp))
        html = await fetch_text(
            session,
            f"https://freedns.afraid.org/domain/registry/?page={sp}&sort=2&q=",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "DNT": "1",
                "Host": "freedns.afraid.org",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "sec-ch-ua": '"Not;A=Brand";v="24", "Chromium";v="128"',
                "sec-ch-ua-platform": "Linux",
            },
        )
        pattern = r"<a href=\/subdomain\/edit\.php\?edit_domain_id=(\d+)>([\w.-]+)<\/a>(.+\..+)<td>public<\/td>"
        matches = re.findall(pattern, html)
        domainnames.extend([match[1] for match in matches])
        domainlist.extend([match[0] for match in matches])


# ---------- find_domain_id (sync freedns client call in thread) ----------
async def find_domain_id(domain_name: str, session: aiohttp.ClientSession):
    page = 1
    html = await fetch_text(
        session,
        "https://freedns.afraid.org/domain/registry/?page=" + str(page) + "&q=" + domain_name,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        },
    )
    pattern = r"<a href=\/subdomain\/edit\.php\?edit_domain_id=([0-9]+)><font color=red>(?:.+\..+)<\/font><\/a>"
    matches = re.findall(pattern, html)
    if len(matches) > 0:
        checkprint(f"Found domain ID: {matches[0]}")
    else:
        raise Exception("Domain ID not found")
    return matches[0]


# ---------- captcha retrieval using freedns client (run in thread) ----------
async def getcaptcha():
    # client.get_captcha() is blocking and returns bytes; call in thread
    data = await asyncio.to_thread(client.get_captcha)
    return Image.open(BytesIO(data))


# ---------- login flow (uses GuerrillaMail via aiohttp, freedns client in thread) ----------
async def login(session: aiohttp.ClientSession):
    while True:
        try:
            checkprint("getting captcha")
            image = await getcaptcha()
            if args.auto:
                # run solve_sync in a thread because pytesseract is CPU bound and blocks
                capcha = await asyncio.to_thread(solve_sync, image)
                if not capcha:
                    checkprint("auto-solve failed, retrying")
                    continue
                checkprint("captcha solved (hopefully)")
            else:
                checkprint("showing captcha")
                # image.show blocks; run in thread
                await asyncio.to_thread(image.show)
                capcha = await asyncio.to_thread(input, "Enter the captcha code: ")
            checkprint("generating email")
            stuff = await fetch_json(session, "https://api.guerrillamail.com/ajax.php?f=get_email_address")
            email = stuff["email_addr"]
            checkprint("email address generated email:" + email)
            checkprint("creating account")
            username = generate_random_string(13)

            # Freedns client create_account is blocking — run in thread
            await asyncio.to_thread(
                client.create_account,
                capcha,
                generate_random_string(13),
                generate_random_string(13),
                username,
                "pegleg1234",
                email,
            )
            checkprint("activation email sent")
            checkprint("waiting for email")
            hasnotreceived = True
            sid_token = stuff.get("sid_token")
            while hasnotreceived:
                nerd = await fetch_json(session, f"https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token={sid_token}")
                if int(nerd.get("count", 0)) > 0:
                    checkprint("email received")
                    mail = await fetch_json(session, f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={nerd['list'][0]['mail_id']}&sid_token={sid_token}")
                    match = re.search(r'\?([^">]+)"', mail.get("mail_body", ""))
                    if match:
                        checkprint("code found")
                        checkprint("verification code: " + match.group(1))
                        checkprint("activating account")
                        # run activate_account in thread
                        await asyncio.to_thread(client.activate_account, match.group(1))
                        checkprint("accout activated")
                        await asyncio.sleep(1)
                        checkprint("attempting login")
                        await asyncio.to_thread(client.login, email, "pegleg1234")
                        checkprint("login successful")
                        hasnotreceived = False
                    else:
                        checkprint("no match in email! you should generally never get this.")
                        checkprint("error!")
                else:
                    checkprint("checked email")
                    await asyncio.sleep(2)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            checkprint("Got error while creating account: " + repr(e))
            if args.use_tor:
                checkprint("attempting to change tor identity")
                try:
                    from stem import Signal
                    from stem.control import Controller

                    async def change_tor():
                        with Controller.from_port(port=9051) as controller:
                            controller.authenticate()
                            controller.signal(Signal.NEWNYM)
                            time_to_wait = controller.get_newnym_wait()
                            await asyncio.sleep(time_to_wait)
                            checkprint("tor identity changed")

                    await change_tor()
                except Exception as e:
                    checkprint("Got error while changing tor identity: " + repr(e))
                    continue
            continue
        else:
            break


# ---------- create domain (uses freedns client create_subdomain in thread, webhook via aiohttp) ----------
async def createdomain(session: aiohttp.ClientSession):
    while True:
        try:
            image = await getcaptcha()
            if args.auto:
                capcha = await asyncio.to_thread(solve_sync, image)
                if not capcha:
                    checkprint("auto-solve failed, retrying")
                    continue
                checkprint("captcha solved")
            else:
                checkprint("showing captcha")
                await asyncio.to_thread(image.show)
                capcha = await asyncio.to_thread(input, "Enter the captcha code: ")

            if args.single_tld:
                random_domain_id = non_random_domain_id
            else:
                random_domain_id = random.choice(domainlist)
            if args.subdomains == "random":
                subdomainy = generate_random_string(10)
            else:
                subdomainy = random.choice(args.subdomains.split(","))
            # call freedns client in thread
            await asyncio.to_thread(client.create_subdomain, capcha, args.type, subdomainy, random_domain_id, ip)
            tld = args.single_tld or domainnames[domainlist.index(random_domain_id)]
            checkprint("domain created")
            checkprint("link: http://" + subdomainy + "." + tld)
            # write to file (sync, but small)
            async def write_out():
                with open(args.outfile, "a") as domainsdb:
                    domainsdb.write("\nhttp://" + subdomainy + "." + tld)
            await asyncio.to_thread(write_out)

            if hookbool:
                checkprint("notifying webhook")
                try:
                    await post_json(session, webhook, {"content": "Domain created:\nhttp://" + subdomainy + "." + tld + "\n ip: " + ip})
                    checkprint("webhook notified")
                except Exception as e:
                    checkprint("Webhook notification failed: " + repr(e))
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            checkprint("Got error while creating domain: " + repr(e))
            continue
        else:
            break


async def createlinks(number: int, session: aiohttp.ClientSession):
    for i in range(number):
        if i % 5 == 0:
            if args.use_tor:
                checkprint("attempting to change tor identity")
                try:
                    from stem import Signal
                    from stem.control import Controller

                    async def change_tor():
                        with Controller.from_port(port=9051) as controller:
                            controller.authenticate()
                            controller.signal(Signal.NEWNYM)
                            time_to_wait = controller.get_newnym_wait()
                            await asyncio.sleep(time_to_wait)
                            checkprint("tor identity changed")

                    await change_tor()
                except Exception as e:
                    checkprint("Got error while changing tor identity: " + repr(e))
                    checkprint("Not going to try changing identity again")
                    args.use_tor = False
            await login(session)
        await createdomain(session)


async def createmax(session: aiohttp.ClientSession):
    await login(session)
    checkprint("logged in")
    checkprint("creating domains")
    await createdomain(session)
    await createdomain(session)
    await createdomain(session)
    await createdomain(session)
    await createdomain(session)


def chooseFrom(dictionary, message):
    checkprint(message)
    for i, key in enumerate(dictionary.keys()):
        checkprint(f"{i+1}. {key}")
    choice = int(input("Choose an option by number: "))
    return list(dictionary.keys())[choice - 1]


# ---------- finddomains wrapper ----------
async def finddomains(pagearg: str, session: aiohttp.ClientSession):
    pages = pagearg.split(",")
    for page in pages:
        await getdomains(page, session)


# ---------- initialization and orchestration ----------
async def init_async():
    global args, ip, iplist, webhook, hookbool, non_random_domain_id

    # create aiohttp session
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    }
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        # fetch iplist async (was a raw github url)
        try:
            raw = await fetch_text(session, "https://raw.githubusercontent.com/heysysadmins/byod-ip/refs/heads/master/byod.json")
            iplist_local = eval(raw)
            # iplist expected to be a dict in original script
            if isinstance(iplist_local, dict):
                iplist = iplist_local
            else:
                # if it's a list, convert to dict-like mapping
                iplist = {str(i): ipaddr for i, ipaddr in enumerate(iplist_local, start=1)}
        except Exception as e:
            checkprint("Failed to fetch ip list: " + repr(e))
            iplist = {"1": "127.0.0.1"}  # fallback

        if not args.ip:
            chosen = chooseFrom(iplist, "Choose an IP to use:")
            match chosen:
                case "custom":
                    ip = input("Enter the custom IP: ")
                case _:
                    ip = iplist[chosen]
            args.ip = ip  # Assign the chosen/entered IP back to args
        else:
            ip = args.ip  # Ensure ip variable is set even if provided via CLI

        if not args.pages:
            args.pages = (
                input(
                    "Enter the page range(s) to scrape (e.g., 15 or 5,8,10-12, default: 10): "
                )
                or "10"
            )

        if not args.webhook:
            match input("Do you want to use a webhook? (y/n) ").lower():
                case "y":
                    hookbool = True
                    webhook = input("Enter the webhook URL: ")
                    args.webhook = webhook  # Assign entered webhook back to args
                case "n":
                    hookbool = False
                    args.webhook = "none"  # Explicitly set to none if declined
        else:
            if args.webhook.lower() == "none":
                hookbool = False
            else:
                hookbool = True
                webhook = args.webhook  # Ensure webhook variable is set

        if (not args.proxy) and (not args.use_tor):
            match input("Do you want to use a proxy? (y/n) ").lower():
                case "y":
                    args.proxy = input("Enter the proxy URL (e.g., http://user:pass@host:port): ")
                case "n":
                    match input("Do you want to use Tor (local SOCKS5 proxy on port 9050)? (y/n) ").lower():
                        case "y":
                            args.use_tor = True
                        case "n":
                            pass  # Neither proxy nor Tor selected

        if args.proxy == "none":
            args.proxy = False

        if not args.outfile:
            args.outfile = (
                input(f"Enter the output filename for domains (default: {args.outfile}): ")
                or args.outfile
            )

        if not args.type:
            args.type = (
                input(f"Enter the type of DNS record to create (default: {args.type}): ")
                or args.type
            )

        if not args.pages:
            args.pages = (
                input(
                    f"Enter the page range(s) to scrape (e.g., 1-10 or 5,8,10-12, default: {args.pages}): "
                )
                or args.pages
            )

        if not args.subdomains:
            match input("Use random subdomains? (y/n) ").lower():
                case "n":
                    args.subdomains = input("Enter comma-separated list of subdomains to use: ")
                case "y":
                    pass

        if not args.number:
            num_links_input = input("Enter the number of links to create: ")
            try:
                num_links = int(num_links_input)
                args.number = num_links
            except ValueError:
                checkprint("Invalid number entered. Exiting.")
                sys.exit(1)
        if not args.auto:
            match input("Use automatic captcha solving? (y/n) ").lower():
                case "y":
                    args.auto = True
                case "n":
                    args.auto = False

        # If using tor for freedns client (requests), set proxies there.
        if args.use_tor:
            checkprint("using local tor proxy on port 9050 for freedns client")
            proxies = {
                "http": "socks5h://127.0.0.1:9050",
                "https": "socks5h://127.0.0.1:9050",
            }
            # client.session is a requests.Session; update proxies in thread
            await asyncio.to_thread(client.session.proxies.update, proxies)
            checkprint("tor proxy set for freedns client")

        if args.proxy and args.proxy is not False:
            checkprint("setting proxy with proxy: " + str(args.proxy) + " for freedns client")
            proxies = {"http": args.proxy, "https": args.proxy}
            await asyncio.to_thread(client.session.proxies.update, proxies)
            checkprint("proxy set for freedns client")

        if args.single_tld:
            checkprint("Using single domain mode")
            checkprint("Finding domain ID for: " + args.single_tld)
            non_random_domain_id = await find_domain_id(args.single_tld, session)
            checkprint(f"Using single domain ID: {non_random_domain_id}")
        else:
            # gather domains (async)
            await finddomains(args.pages, session)

        if args.number:
            await createlinks(args.number, session)


def main():
    try:
        asyncio.run(init_async())
    except KeyboardInterrupt:
        checkprint("Interrupted by user, exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
def init():
    import asyncio
    asyncio.run(main())
