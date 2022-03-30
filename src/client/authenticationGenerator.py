from typing import Dict
import random
import secrets
##TODO: We need to expand this from a simple username, password credential generation after PoC developed to a range of authentication methods
class authenticationGenerator:
    def __init__(self):
        self.credentialsUsed = []

    def generateUserPass(self) -> Dict[str,str]:
        userpass = {
            "username": self.generateUsername(),
            "password": self.generatePassword()
        }

        return userpass

    def generateUsername(self):
        try:
            return next(self.usernameGenerator)
        except Exception:
            self.usernameGenerator = self.getUsernameFromFile()
            print("started again")
            return next(self.usernameGenerator)

    def getUsernameFromFile(self, minLength=5, maxLength=13):
        with open("wordlists/jeanphorn-wordlist-usernames.txt") as infile:
            while True:
                username = self.jumpForwardInFile(infile)
                if minLength <= len(username) <= maxLength and username not in self.credentialsUsed:
                    yield username                

    def jumpForwardInFile(self, fd, lines=random.randint(170, 250)):
        for i in range(lines):
            username = fd.readline().strip("\n")
        return username

    def generatePassword(self, minLength=8, maxLength=12):
        return secrets.token_urlsafe(random.randint(minLength, maxLength))
            
    def generateCredentials(self):
        while True:
            userpassCreds = self.generateUsername(), self.generatePassword()
            if userpassCreds not in self.credentialsUsed:
                self.credentialsUsed.append(userpassCreds)
                break

        return userpassCreds
