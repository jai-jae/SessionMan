import requests
import rsa
import uuid
from lzstring import LZString

USER_AGENTS = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"


def _generate_message(nid: str, npw: str, curr_key: str) -> bytes:
    message: str = ""
    lst: list = [curr_key, nid, npw]
    for item in lst:
        message += (chr(len(item)) + item)
    # print("message to be encoded : ", message.encode())
    return message.encode()


def _encrypt(nid: str, npw: str, naver_keys: str) -> (str, str):
    try:
        curr_key, encnm, e_str, n_str = naver_keys.split(',')
    except Exception as e:
        print("at encrypt() : ", e)

    e = int(e_str, 16)
    n = int(n_str, 16)
    # print(curr_key)
    # print(encnm)
    # print(e_str)
    # print(n_str)
    message = _generate_message(nid, npw, curr_key)
    pubkey = rsa.PublicKey(e, n)
    encrypted_message = rsa.encrypt(message, pubkey).hex()
    print(encrypted_message)
    return (encnm, encrypted_message)


def encrypt_account(nid, npw) -> (str, str):
    try:
        response = requests.get('https://nid.naver.com/login/ext/keys.nhn')
    except HTTPError as e:
        print("at encrypt_account() : ", e)
    naver_keys = response.content.decode("utf-8")
    encnm, encpw = _encrypt(nid, npw, naver_keys)
    return (encnm, encpw)


def get_bvsd(nid) -> str:
    bvsd_uuid: str = uuid.uuid4()
    encData_json: str = '{"a":"%s-4","b":"1.3.4","d":[{"i":"id","b":{"a":["0,%s"]},"d":"%s","e":false,"f":false},{"i":"pw","e":true,"f":false}],"h":"1f","i":{"a":"%s"}}' \
        % (bvsd_uuid, nid, nid, USER_AGENTS)
    encData = LZString.compressToEncodedURIComponent(encData_json)
    
    bvsd: str = '{"uuid":"%s","encData":"%s"}' % (bvsd_uuid, encData)

    return bvsd


def generate_login_form(encnm: str, encpw: str, bvsd: str) -> dict:
    login_data: dict = {
        'encpw': encpw,
        'enctp': '1',
        'svctype': '1',
        'smart_LEVEL': '1',
        'bvsd': bvsd,
        'encnm': encnm,
        'locale': 'ko_KR',
        'url': 'www.naver.com',
        'id': '',
        'pw': ''
    }
    
    return login_data