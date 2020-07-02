import requests
import re
from json.decoder import JSONDecodeError

CSRF_NONCE_REGEX_1 = re.compile("'csrfNonce': \"(.*)\"")
CSRF_NONCE_REGEX_2 = re.compile('name="nonce" value="(.*)"')


class CtfdApi:
    def __init__(self, base_url):
        self.session = requests.session()
        self.base_url = base_url

    def login(self, username, password):
        get_req = self.session.get(f"{self.base_url}/login")
        nonce_search = CSRF_NONCE_REGEX_1.search(
            get_req.text
        ) or CSRF_NONCE_REGEX_2.search(get_req.text)
        nonce = nonce_search.group(1)

        post_req = self.session.post(
            f"{self.base_url}/login",
            data={"name": username, "password": password, "nonce": nonce},
            allow_redirects=False,
        )
        if post_req.status_code != 302:
            raise Exception("Login failed")

    def get_challenges(self):
        api_res = self.session.get(f"{self.base_url}/api/v1/challenges")
        try:
            res = api_res.json()
        except JSONDecodeError as err:
            raise Exception(api_res.text)
        if res.get("success"):
            return res["data"]

    def get_solves(self):
        res = self.session.get(f"{self.base_url}/api/v1/teams/me/solves").json()
        if not res.get("success"):
            res = self.session.get(f"{self.base_url}/api/v1/users/me/solves").json()
        if res.get("success"):
            return res["data"]

    def get_challenge_details(self, challenge_id):
        res = self.session.get(
            f"{self.base_url}/api/v1/challenges/{challenge_id}"
        ).json()
        if res.get("success"):
            return res["data"]

    def submit_flag(self, challenge_id, flag):
        get_req = self.session.get(f"{self.base_url}/challenges")
        nonce_search = CSRF_NONCE_REGEX_1.search(
            get_req.text
        ) or CSRF_NONCE_REGEX_2.search(get_req.text)
        nonce = nonce_search.group(1)

        res = self.session.post(
            f"{self.base_url}/api/v1/challenges/attempt",
            json={"challenge_id": challenge_id, "submission": flag},
            headers={"CSRF-Token": nonce},
        ).json()
        return res["data"]["status"]
