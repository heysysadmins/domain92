# domain92
A totally rad cli tool to automate freedns link creation
## Function
This script simplifies account creation and domain making on freedns.afraid.org.
It uses ading2210's [freedns client](https://github.com/ading2210/freedns-client) and the guerrillamail.com api.
All you have to do is sit there and solve captchas!
## table of contents
- [domain92](#domain92)
  - [Function](#function)
  - [table of contents](#table-of-contents)
  - [Installation](#installation)
    - [with pip](#with-pip)
      - [install from pypi](#install-from-pypi)
      - [install from github repository](#install-from-github-repository)
  - [Usage](#usage)
    - [Arguments](#arguments)
      - [-h, --help](#-h---help)
      - [--number](#--number)
      - [--ip](#--ip)
      - [--webhook](#--webhook)
      - [--use\_proxy](#--use_proxy)
      - [--proxy](#--proxy)
      - [--silent](#--silent)
      - [--outfile](#--outfile)
      - [--type](#--type)
      - [--pages](#--pages)
      - [--subdomains](#--subdomains)
      - [--auto](#--auto)
  - [ip blocked?](#ip-blocked)
      - [please star on github if you use this!](#please-star-on-github-if-you-use-this)
- [License](#license)

## Installation
### with pip
#### install from pypi
```bash
pip install domain92
```
#### install from github repository
```bash
pip install git+https://github.com/sebastian-92/domain92
```
## Usage
### Arguments
#### -h, --help
Displays the help message.
```bash
domain92 -h
```

#### --number
Specifies the number of links to generate.
```bash
domain92 --number 5
```
This will generate 5 links.

#### --ip
Specifies the IP address to use.
```bash
domain92 --ip 192.168.1.1
```
This will use the IP address `192.168.1.1`.

#### --webhook
Specifies the webhook URL. Use "none" to not ask.
```bash
domain92 --webhook https://example.com/webhook
```
This will use the specified webhook URL.

#### --use_proxy
Uses a proxy (default uses 127.0.0.1:9050).
```bash
domain92 --use_proxy
```
This will use the default proxy `127.0.0.1:9050`.

#### --proxy
Specifies a custom SOCKS5 external proxy or a different port for Tor.
```bash
domain92 --proxy socks5://custom.proxy:1080
```
This will use the specified custom proxy.

#### --silent
Suppresses output other than showing the captchas.
```bash
domain92 --silent
```
This will suppress all output except for captchas.

#### --outfile
Specifies the output file for the domains (default is "domainlist.txt").
```bash
domain92 --outfile output.txt
```
This will save the output to `output.txt`.

#### --type
Specifies the type of record to make (default is "A").
```bash
domain92 --type AAAA
```
This will create an AAAA record.

#### --pages
Specifies the range of pages to scrape (default is the first ten).
```bash
domain92 --pages 3-5
```
This will scrape pages 3 to 5.
```bash
domain92 --pages 6
```
This will scrape the first six pages
```bash
domain92 --pages 14-17,6,43-43
```
This will scrape pages 14 to 17, 1 to 6, and page 43.

#### --subdomains
Specifies a comma-separated list of subdomains to use (default is random).
```bash
domain92 --subdomains sub1,sub2,sub3
```
This will use the specified subdomains.

#### --auto
Uses Tesseract to automatically solve the captchas. This requires Tesseract to be installed.
```bash
domain92 --auto
```
This will use Tesseract to automatically solve captchas.

## ip blocked?
if you are IP blocked, it will come up with an error along the lines of "Account does not exist" immediately after activating the account, while trying to log in.
- use `--use_proxy` and `--proxy` to avoid this

#### please star on [github](https://github.com/sebastian-92/domain92) if you use this!
# License
This project is licensed under the [GNU AGPL v3.0](LICENSE) :)