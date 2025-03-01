print("importing things...")
from PIL import Image
from io import BytesIO
import time
import requests as req
import re
import random
import string
from art import *
import freedns

ip = "104.36.86.105"
tprint("domain92")

client = freedns.Client()

print("client initialized")
domainlist = []
domainnames = []
print("finding domains")
# uncomment the following lines to use tor if you get ip banned
# you need to set up the tor service on your system and start it.
# print("setting proxy through tor")
# proxies = {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}
# client.session.proxies.update(proxies)
# print("proxy set")
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
    "Frogiees Arcade": "152.53.1.222",
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


def finddomains(pages):
    global domainlist, domainnames
    for i in range(pages):
        html = req.get(
            "https://freedns.afraid.org/domain/registry/?page="
            + str(pages + 1)
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


finddomains(10)

print("ready")


def generate_random_string(length):
    """Generates a random string of letters of given length."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def login():
    while True:
        try:
            print("getting captcha")
            image = Image.open(BytesIO(client.get_captcha()))
            print("showing captcha")
            image.show()
            capcha = input("Enter the captcha code: ")
            print("generating email")
            stuff = req.get(
                "https://api.guerrillamail.com/ajax.php?f=get_email_address"
            ).json()
            email = stuff["email_addr"]
            print("email address generated")
            print(email)
            print(stuff)
            print("creating account")
            username = generate_random_string(13)
            client.create_account(
                capcha,
                generate_random_string(13),
                generate_random_string(13),
                username,
                "pegleg1234",
                email,
            )
            print("activation email sent")
            print("waiting for email")
            hasnotreceived = True
            while hasnotreceived:
                nerd = req.get(
                    "https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token="
                    + str(stuff["sid_token"])
                ).json()

                if int(nerd["count"]) > 0:
                    print("email received")
                    mail = req.get(
                        "https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id="
                        + str(nerd["list"][0]["mail_id"])
                        + "&sid_token="
                        + str(stuff["sid_token"])
                    ).json()
                    match = re.search(r'\?([^">]+)"', mail["mail_body"])
                    if match:
                        print("code found")
                        print("verification code: " + match.group(1))
                        print("activating account")
                        client.activate_account(match.group(1))
                        print("accout activated")
                        time.sleep(3)
                        print("attempting login")
                        client.login(email, "pegleg1234")
                        print("login successful")
                        hasnotreceived = False
                    else:
                        print("no match")
                        print("error!")

                else:
                    print("checked email")
                    time.sleep(3)
        except:
            print("login error!")
            continue
        else:
            break


def createmax():
    login()
    print("logged in")
    print("creating domains")
    createdomain()
    time.sleep(3)
    createdomain()
    time.sleep(3)
    createdomain()
    time.sleep(3)
    createdomain()
    time.sleep(3)
    createdomain()
    time.sleep(3)


def createdomain():
    while True:
        try:
            print("creating domain")
            image = Image.open(BytesIO(client.get_captcha()))
            image.show()
            capcha = input("Enter the captcha code: ")
            random_domain_id = random.choice(domainlist)
            subdomainy = generate_random_string(10)
            client.create_subdomain(capcha, "A", subdomainy, random_domain_id, ip)
            print("domain created")
            print(
                "link: http://"
                + subdomainy
                + "."
                + domainnames[domainlist.index(random_domain_id)]
            )
            domainsdb = open("domainlist.txt", "a")  # append mode
            domainsdb.write(
                "\nhttp://"
                + subdomainy
                + "."
                + domainnames[domainlist.index(random_domain_id)]
            )
            domainsdb.close()
        except:
            continue
        else:
            break


def init():
    global ip, iplist
    chosen = chooseFrom(iplist, "Choose an IP to use:")
    match chosen:
        case "custom":
            ip = input("Enter the custom IP: ")
        case _:
            ip = iplist[chosen]
    for _ in range(int(input("how many accounts? "))):
        createmax()


def chooseFrom(dictionary, message):
    print(message)
    for i, key in enumerate(dictionary.keys()):
        print(f"{i+1}. {key}")
    choice = int(input("Choose an option by number: "))
    return list(dictionary.keys())[choice - 1]


init()
