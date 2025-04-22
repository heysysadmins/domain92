from PIL import Image
from io import BytesIO
import time
import requests as req
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
import time

parser = argparse.ArgumentParser(
    description="Automatically creates links for an ip on freedns"
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
parser.add_argument("--proxy", help="use if you get ip blocked.", type=str)
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
    default="10",
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
args = parser.parse_args()
ip = args.ip
if not args.silent:
    lolpython.lol_py(text2art("domain92"))


def checkprint(input):
    global args
    if not args.silent:
        print(input)


client = freedns.Client()

checkprint("client initialized")


def get_data_path():
    script_dir = os.path.dirname(__file__)
    checkprint("checking os")
    if platform.system() == "Windows":
        filename = os.path.join(script_dir, "data", "windows", "tesseract")
    elif platform.system() == "Linux":
        filename = os.path.join(script_dir, "data", "tesseract-linux")
    else:
        print("Unsupported OS. This could cause errors with captcha solving.")
        return None
    os.environ["TESSDATA_PREFIX"] = os.path.join(script_dir, "data")
    return filename


path = get_data_path()
if path:
    pytesseract.pytesseract.tesseract_cmd = path
    checkprint(f"Using tesseract data file: {path}")
else:
    checkprint("No valid tesseract file for this OS.")

domainlist = []
domainnames = []
checkprint("finding domains")
if args.use_tor:
    checkprint("using local tor proxy on port 9050")
    proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
    client.session.proxies.update(proxies)
    checkprint("tor proxy set")

if args.proxy:
    checkprint("setting proxy with proxy: " + args.proxy)
    proxies = {"http": args.proxy, "https": args.proxy}
    client.session.proxies.update(proxies)
    checkprint("proxy set")
iplist = {
    "custom": "custom",
    "1346.lol": "159.54.169.0",
    "Acceleration": "141.148.134.230",
    "Artclass": "198.251.90.4",
    "Astro": "104.243.37.85",
    "Astroid": "5.161.68.227",
    "Astroid (2)": "152.53.53.8",
    "Boredom": "152.53.36.42",
    "Bolt": "104.36.86.24",
    "Breakium": "172.93.100.82",
    "BrunysIXLWork": "185.211.4.69",
    "Canlite (3kh0 v5)": "104.36.85.249",
    "Catway": "A-92.38.148.24",
    "Comet/PXLNOVA": "172.66.46.221",
    "Core": "207.211.183.185",
    "Croxy Proxy": "157.230.79.247",
    "Croxy Proxy (2)": "143.244.204.138",
    "Croxy Proxy (3)": "157.230.113.153",
    "Doge Unblocker": "104.243.38.142",
    "DuckHTML": "104.167.215.179",
    "Duckflix": "104.21.54.237",
    "Emerald/Phantom Games/G1mkit": "66.23.198.136 ",
    "Equinox": "74.208.202.111",
    "FalconLink": "104.243.43.17",
    "Frogie's Arcade": "152.53.81.196",
    "Ghost/AJH's Vault": "163.123.192.9",
    "GlacierOS": "66.241.124.98",
    "Hdun": "109.204.188.135",
    "Interstellar": "66.23.193.126",
    "Kasm 1": "145.40.75.101",
    "Kasm 2": "142.93.68.85",
    "Kasm 3": "165.22.33.54",
    "Kazwire": "103.195.102.132 ",
    "Light": "104.243.45.193",
    "Lunaar": "164.152.26.189",
    "Mocha": "45.88.186.218",
    "Moonlight": "172.93.104.11",
    "Onyx": "172.67.158.114",
    "Plexile Arcade": "216.24.57.1",
    "Pulsar": "172.93.106.140",
    "Ruby": "104.36.86.104",
    "Rammerhead IP": "108.181.32.77",
    "Selenite (Ultrabrowse server)": "104.131.74.161",
    "Selenite": "65.109.112.222",
    "Seraph": "15.235.166.92",
    "Shadow": "104.243.38.18",
    "Space": "104.243.38.145",
    "Sunset": "107.206.53.96",
    "Sunnys Gym": "69.48.204.208",
    "Szvy Central": "152.53.38.100",
    "Tinf0il": "129.213.65.72",
    "The Pizza Edition": "104.36.84.31",
    "thepegleg": "104.36.86.105",
    "UniUB": "104.243.42.228",
    "Utopia": "132.145.197.109",
    "Velara": "185.211.4.69",
    "Void Network": "141.193.68.52",
    "Waves": "93.127.130.22",
    "Xenapsis/Ephraim": "66.175.239.22",
}


def getdomains(arg: str):
    if "-" in arg:
        pagelist = arg.split("-")
        if len(pagelist) == 2:
            sp = int(pagelist[0])
            ep = int(pagelist[1])
        else:
            checkprint("Invalid page range")
            sys.exit()
    else:
        sp = 1
        ep = int(arg)
    if sp < 1:
        checkprint("Invalid page range")
        sys.exit()
    if sp > ep:
        checkprint("Invalid page range")
        sys.exit()
    global domainlist, domainnames
    while sp <= ep:
        checkprint("getting page " + str(sp))
        html = req.get(
            "https://freedns.afraid.org/domain/registry/?page="
            + str(sp)
            + "&sort=2&q=",
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
        ).text
        pattern = r"<a href=/subdomain/edit\.php\?edit_domain_id=\d+>([\w.-]+)</a>.*?<td>public</td>"
        domainnames.extend(re.findall(pattern, html))
        pattern = r"<a href=/subdomain/edit\.php\?edit_domain_id=(\d+)>([\w.-]+)</a>.*?<td>public</td>"
        matches = re.findall(pattern, html)
        domainlist.extend([match[0] for match in matches])  # Extract only the IDs
        sp = sp + 1


def finddomains(pagearg):  # sp = start page, ep = end page
    pages = pagearg.split(",")
    for page in pages:
        getdomains(page)


finddomains(args.pages)
hookbool = False
webhook = ""
if args.subdomains != "random":
    checkprint("Subdomains set to:")
    checkprint(args.subdomains.split(","))
checkprint("ready")


def getcaptcha():
    return Image.open(BytesIO(client.get_captcha()))


def denoise(img):
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


def solve(image):
    image = denoise(image)
    text = pytesseract.image_to_string(
        image.filter(ImageFilter.GaussianBlur(1))
        .convert("1")
        .filter(ImageFilter.RankFilter(3, 3)),
        config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 7",
    )
    text = re.sub(r"[^A-Z]", "", text)
    checkprint("got text: " + text)
    if len(text) != 5 and len(text) != 4:
        checkprint("Retrying with different filters")
        text = pytesseract.image_to_string(
            image.filter(ImageFilter.GaussianBlur(2)).filter(
                ImageFilter.MedianFilter(3)
            ),
            config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 8",
        )
        text = re.sub(r"[^A-Za-z]", "", text)
        checkprint("got text: " + text)
    if len(text) != 5 and len(text) != 4:
        checkprint("Retrying with different filters")
        text = pytesseract.image_to_string(
            image,
            config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 8",
        )
        text = re.sub(r"[^A-Za-z]", "", text)
        checkprint("got text: " + text)
    if len(text) != 5 and len(text) != 4:
        checkprint("trying different captcha")
        text = solve(getcaptcha())
    return text


def generate_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def login():
    while True:
        try:
            checkprint("getting captcha")
            image = getcaptcha()
            if args.auto:
                capcha = solve(image)
                checkprint("captcha solved (hopefully)")
            else:
                checkprint("showing captcha")
                image.show()
                capcha = input("Enter the captcha code: ")
            checkprint("generating email")
            stuff = req.get(
                "https://api.guerrillamail.com/ajax.php?f=get_email_address"
            ).json()
            email = stuff["email_addr"]
            checkprint("email address generated email:" + email)
            checkprint(email)
            checkprint("creating account")
            username = generate_random_string(13)
            client.create_account(
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
            while hasnotreceived:
                nerd = req.get(
                    "https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token="
                    + str(stuff["sid_token"])
                ).json()

                if int(nerd["count"]) > 0:
                    checkprint("email received")
                    mail = req.get(
                        "https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id="
                        + str(nerd["list"][0]["mail_id"])
                        + "&sid_token="
                        + str(stuff["sid_token"])
                    ).json()
                    match = re.search(r'\?([^">]+)"', mail["mail_body"])
                    if match:
                        checkprint("code found")
                        checkprint("verification code: " + match.group(1))
                        checkprint("activating account")
                        client.activate_account(match.group(1))
                        checkprint("accout activated")
                        time.sleep(1)
                        checkprint("attempting login")
                        client.login(email, "pegleg1234")
                        checkprint("login successful")
                        hasnotreceived = False
                    else:
                        checkprint(
                            "no match in email! you should generally never get this."
                        )
                        checkprint("error!")

                else:
                    checkprint("checked email")
                    time.sleep(2)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            checkprint("Got error while creating account: " + repr(e))
            if args.use_tor:
                checkprint("attempting to change tor identity")
                try:
                    from stem import Signal
                    from stem.control import Controller

                    with Controller.from_port(port=9051) as controller:
                        controller.authenticate()
                        controller.signal(Signal.NEWNYM)
                        time.sleep(controller.get_newnym_wait())
                        checkprint("tor identity changed")
                except Exception as e:
                    checkprint("Got error while changing tor identity: " + repr(e))
                    continue
            continue
        else:
            break


def createlinks(number):
    for i in range(number):
        if i % 5 == 0:
            if args.use_tor:
                checkprint("attempting to change tor identity")
                try:
                    from stem import Signal
                    from stem.control import Controller

                    with Controller.from_port(port=9051) as controller:
                        controller.authenticate()
                        controller.signal(Signal.NEWNYM)
                        time.sleep(controller.get_newnym_wait())
                        checkprint("tor identity changed")
                except Exception as e:
                    checkprint("Got error while changing tor identity: " + repr(e))
                    checkprint("Not going to try changing identity again")
                    args.use_tor = False
            login()
        createdomain()


def createmax():
    login()
    checkprint("logged in")
    checkprint("creating domains")
    createdomain()
    createdomain()
    createdomain()
    createdomain()
    createdomain()


def createdomain():
    while True:
        try:
            image = getcaptcha()
            if args.auto:
                capcha = solve(image)
                checkprint("captcha solved")
            else:
                checkprint("showing captcha")
                image.show()
                capcha = input("Enter the captcha code: ")
            random_domain_id = random.choice(domainlist)
            if args.subdomains == "random":
                subdomainy = generate_random_string(10)
            else:
                subdomainy = random.choice(args.subdomains.split(","))
            client.create_subdomain(capcha, args.type, subdomainy, random_domain_id, ip)
            checkprint("domain created")
            checkprint(
                "link: http://"
                + subdomainy
                + "."
                + domainnames[domainlist.index(random_domain_id)]
            )
            domainsdb = open(args.outfile, "a")
            domainsdb.write(
                "\nhttp://"
                + subdomainy
                + "."
                + domainnames[domainlist.index(random_domain_id)]
            )
            domainsdb.close()
            if hookbool:
                checkprint("notifying webhook")
                req.post(
                    webhook,
                    json={
                        "content": "Domain created:\nhttp://"
                        + subdomainy
                        + "."
                        + domainnames[domainlist.index(random_domain_id)]
                        + "\n ip: "
                        + ip
                    },
                )
                checkprint("webhook notified")
        except KeyboardInterrupt:
            # quit
            sys.exit()
        except Exception as e:
            checkprint("Got error while creating domain: " + repr(e))
            continue
        else:
            break


def init():
    global args, ip, iplist, webhook, hookbool
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

    if not args.proxy and not args.use_tor:  # Only ask if neither proxy nor tor is set
        match input("Do you want to use a proxy? (y/n) ").lower():
            case "y":
                args.proxy = input(
                    "Enter the proxy URL (e.g., http://user:pass@host:port): "
                )
            case "n":
                match input(
                    "Do you want to use Tor (local SOCKS5 proxy on port 9050)? (y/n) "
                ).lower():
                    case "y":
                        args.use_tor = True
                    case "n":
                        pass  # Neither proxy nor Tor selected

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

    if args.subdomains == "random":
        match input("Use random subdomains? (y/n) ").lower():
            case "n":
                args.subdomains = input(
                    "Enter comma-separated list of subdomains to use: "
                )
            case "y":
                pass
    if not args.number:
        num_links_input = input("Enter the number of links to create: ")
        try:
            num_links = int(num_links_input)
            createlinks(num_links)
        except ValueError:
            checkprint("Invalid number entered. Exiting.")
            sys.exit(1)
    if not args.auto:
        match input("Use automatic captcha solving? (y/n) ").lower():
            case "y":
                args.auto = True
            case "n":
                args.auto = False

    if args.use_tor:
        checkprint("using local tor proxy on port 9050")
        proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050",
        }
        client.session.proxies.update(proxies)
        checkprint("tor proxy set")
    elif args.proxy:
        checkprint("setting proxy with proxy: " + args.proxy)
        proxies = {"http": args.proxy, "https": args.proxy}
        client.session.proxies.update(proxies)
        checkprint("proxy set")
    finddomains(args.pages)

    if args.number:
        createlinks(args.number)


def chooseFrom(dictionary, message):
    checkprint(message)
    for i, key in enumerate(dictionary.keys()):
        checkprint(f"{i+1}. {key}")
    choice = int(input("Choose an option by number: "))
    return list(dictionary.keys())[choice - 1]


if __name__ == "__main__":
    init()
