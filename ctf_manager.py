from ctfd_api import CtfdApi
from dataclasses import dataclass
from typing import List


@dataclass
class Challenge:
    name: str
    score: int
    solves: int
    category: str
    description: str
    tags: List[str]
    files_exist: bool
    solved: bool


class CtfManager:
    def __init__(self):
        self.username = None
        self.password = None
        self.url = None
        self.ctfd_api = None
        self.challenges = {}

    def fetch(self):
        if self.username is None:
            raise Exception("Please set a username with $set username <username>")
        if self.password is None:
            raise Exception("Please set a password with $set password <password>")
        if self.url is None:
            raise Exception("Please set a url with $set url <url>")

        if self.ctfd_api is None:
            self.ctfd_api = CtfdApi(self.url)
            self.ctfd_api.login(self.username, self.password)

        challs = self.ctfd_api.get_challenges()
        solves = self.ctfd_api.get_solves()

        for chal in challs:
            chal_id = chal["id"]
            details = self.ctfd_api.get_challenge_details(chal_id)
            self.challenges[chal_id] = Challenge(
                name=details["name"],
                score=details["value"],
                solves=details["solves"],
                category=details["category"],
                description=details["description"],
                tags=details["tags"],
                files_exist=len(details["files"]) > 0,
                # check if obj with "challenge_id" == chal_id is in solves
                solved=next((s for s in solves if s["challenge_id"] == chal_id), None)
                is not None,
            )

        return self.challenges

    def submit_flag(self, challenge_id, flag):
        res = self.ctfd_api.submit_flag(challenge_id, flag)
        if res != "correct":
            raise Exception(res)
