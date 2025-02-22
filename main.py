from PIL import Image
from io import BytesIO
import time
import requests as req
import re
import random
import string
import freedns

# proxies = {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}
client = freedns.Client()
# print("setting proxy through tor")
# client.session.proxies.update(proxies)
print("cleint initialized")
domainlist = [
    202912,
    1034777,
    862650,
    602483,
    1003196,
    736103,
    653235,
    717627,
    797323,
    639192,
    922846,
    870227,
    1151062,
    852689,
    377240,
    1000189,
    833343,
    738607,
    191996,
    267705,
    1025303,
    1057091,
    1231748,
    421353,
    756296,
    1075157,
    1014292,
    743443,
    882849,
    339528,
    422641,
    231146,
    724332,
    788252,
    1124405,
    739468,
    857964,
    767341,
    986903,
    851500,
    670881,
    911466,
    686932,
    998693,
    794917,
    902289,
    716468,
    1207773,
    791036,
    568087,
    537582,
    1020808,
    916709,
    590150,
    770445,
    366168,
    774473,
    403035,
    845371,
    375723,
    695508,
    946361,
    904452,
    1373070,
    816402,
    1106393,
    417734,
    1092455,
    833441,
    685486,
    779172,
    678837,
    816188,
    714344,
    717501,
    660820,
    718956,
    838289,
    973068,
    843131,
    904451,
    1062960,
    902488,
    265565,
    726612,
    766506,
    830174,
    1053378,
]
domainnames = [
    "rpcthai.com",
    "sachhot.com",
    "sacrebl.eu",
    "stanharvell.com",
    "taufonua.to",
    "thejaq.net",
    "thetachiusf.com",
    "tth.com.pk",
    "vvvrm.net",
    "xy-solutions.com",
    "2gfkitchen.com",
    "arfotoarte.com",
    "bellyfatcat.com",
    "chucktam.com",
    "cmr.com.ar",
    "dirtchicvt.com",
    "donnaspa.net",
    "egood-tw.com",
    "fiat500.li",
    "insilico.at",
    "itzzm.com",
    "jnussbaum.com",
    "justminers.com",
    "kancilja.si",
    "labgarreguevara.com.ar",
    "rocketpride.com",
    "shankillweather.com",
    "shredstreet.com",
    "smwilliams.com",
    "thesqueakandoilchart.com",
    "thsa.com.ar",
    "utrealestatedreamteam.com",
    "vinoniv.com",
    "ausnetwebhosting.com",
    "botar.co.uk",
    "conveyancingmonkey.com",
    "dmazzola.com",
    "kowaileet.com",
    "ltelink.at",
    "mobil-ray.ru",
    "mycrossfire.net",
    "remulon.com",
    "rileytree.org",
    "servidorlocal.pt",
    "shanetrainfitness.com",
    "stpetersandstpauls.org",
    "thinairtech.com",
    "vivandex.com",
    "vsltech.net",
    "westlondon-escorts.net",
    "a-pratama.com",
    "abwild.net",
    "albacetediario.com",
    "assuregloves.com",
    "carrard.org",
    "clickandmortar.ca",
    "cyberdine.ca",
    "danleevogler.net",
    "edah.us",
    "etranslator.eu",
    "generaloweb.com",
    "gridtoroad.com",
    "kandla.com",
    "kick.sh",
    "npmpt.com",
    "parcomunica.com",
    "periodico.am",
    "protelecon.com",
    "sgmlguru.org",
    "skam.co",
    "southwestvoodoo.com",
    "stockcity.ru",
    "tuoitrevn.nl",
    "vikingbild.se",
    "wesseldijkstra.com",
    "zlotecentrum.com",
    "50friends.com.mx",
    "asiaherewe.com",
    "atf.com.np",
    "changamuka.com",
    "chowpatty.com",
    "cthchile.com",
    "cwqso.net",
    "daniellaporter.cl",
    "designjobs.eu",
    "etaxichile.cl",
    "gradientking.com",
    "jasoncoyne.com",
]


def generate_random_string(length):
    """Generates a random string of letters of given length."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def createmax():
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
        except:
            continue
        else:
            break


def createdomain():
    print("creating domain")
    image = Image.open(BytesIO(client.get_captcha()))
    image.show()
    capcha = input("Enter the captcha code: ")
    random_domain_id = random.choice(domainlist)
    subdomainy = generate_random_string(10)
    client.create_subdomain(capcha, "A", subdomainy, random_domain_id, "104.36.86.105")
    print("domain created")
    print(
        "link: http://"
        + subdomainy
        + "."
        + domainnames[domainlist.index(random_domain_id)]
    )
    domainsdb = open("domainlist.txt", "a")  # append mode
    domainsdb.write(
        "\nhttp://" + subdomainy + "." + domainnames[domainlist.index(random_domain_id)]
    )


for _ in range(int(input("how many accounts? "))):
    createmax()
domainsdb.close()
