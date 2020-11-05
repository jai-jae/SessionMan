import requests
from time import sleep
import os
from requests import HTTPError
from lxml import etree
from NaverModule import naver_auth as na

SEARCH_URL = \
    "https://cafe.naver.com/ArticleSearchList.nhn?search.clubid=10050146&search.media=0&search.searchdate=all&search.exact=&search.include=&userDisplay=50&search.exclude=&search.option=0&search.sortBy=date&search.searchBy=1&search.searchBlockYn=0&search.includeAll=&search.query=%B9%D9%BD%C7%B8%AE%BD%BA%C5%A9&search.viewtype=title&search.page=1"

USER_AGENTS = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"

class Session(requests.Session):
    
    def __init__(self, nid: str, npw: str):
        super(Session, self).__init__()
        self.nid: str = nid
        self.npw: str = npw
        self.encnm, self.encpw = na.encrypt_account(self.nid, self.npw)
        self.bvsd: str = na.get_bvsd(self.nid)
        self.headers.update({'user-agent': USER_AGENTS})
        self.login_data: dict = na.generate_login_form(self.encnm, self.encpw, self.bvsd)


    def login(self):
        try:
            resp = self.post(
                'https://nid.naver.com/nidlogin.login',
                data=self.login_data,
                headers=self.headers
            )
        except HTTPError as e:
            print("at naver_login() : ", e)
            return None
        isvalid = self._verify_naver_session(resp)
        if isvalid:
            print("successfully logged in.")
        else:
            print("Log in failed. Please check the status in the browser.")


    def _verify_naver_session(self, resp):
        content: str = resp.text
        root = etree.HTML(content)
        # print(content)
        try:
            tmp = root.xpath('//script[@language="javascript"]/text()')[0]
        except Exception as e:
            print("at _verify_naver_session() : ", e)
        try:
            final_url = tmp.split('"')[1]
        except Exception as e:
            print("at verify_naver_session split()", e)
        print(final_url)
        if "finalize" in final_url:
            return True
        else:
            return False


    def logout(self):
        """
        send GET request to logout endpoint
        """
        try:
            resp = self.get("https://nid.naver.com/nidlogin.logout")
        except HTTPError as e:
            print("at naver_login() logout failed! : ", e)
