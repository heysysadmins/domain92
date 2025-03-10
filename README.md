# domain92
A cool little program I wrote to automate link creation
## about
This script simplifies account creation and domain making on freedns.afraid.org.
It uses ading2210's [freedns client](https://github.com/ading2210/freedns-client) and the guerrillamail.com api.
All you have to do is sit there and solve captchas!
## Usage
### normal, easy way
#### download and use the latest executable
- go to [releases](https://github.com/sebastian-92/domain92/releases) and download the latest executable for your platform
- run it
### command line arguments
do this to see them
```bash
./main-linux-64 -h
```
### for development or to use latest version
#### requirements
- I used python Python 3.12.3 while making this, anything lower and you might have some problems
#### running
install dependencies
```bash
pip install -r requirements.txt
```
run the program
```bash
python3 main.py -h
```
### auto solving captchas
To use the automatic captcha solving feature, you need tesseract installed. Go install it.
## notes
- if use it enough, you might get ip blocked from creating accounts on freedns, see -h for how to fix

- please star if you use it!
# License
This project is licensed under the [GNU AGPL v3.0](LICENSE) :)
