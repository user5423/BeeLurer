import random
import secrets
##We need to generate credentials so that the server can use in their bait connection to itself via the tor network

##We need to make the credentials look genuine:
# 1. Usernames -- using random chars looks a bit weird
# 2. Passwords -- using random characters could imply that a user would want to protect something well.

## Therefore, for now we'll use a wordlist with usernames, and generate random strings for passwords
## We'll be using wordlists from secLists on github and jeanphorn for now
## NOTE: There may be tuning we can do to make passwords and usernames more realistic. e.g. following basic rules that most
## sites on the web use such as 8letters min, use numbers, capitals, etc.



# VULNERABILITY: If an adversary finds our project and an instance running on it.
# --> Currently we are using passwordlists. However, since the project is open-source, they could use the passwordlist and userlist to 
# fuzz the website. An adversary could fuzz the site, and if they get enough combinations right, they could manage to raise false positives for other exit nodes.
# --> This would render any data as useless, as we wouldn't know which exit nodes are malicious or not

# ==> Therefore, the passwords generated for our users cannot be easily predicted. That means basic passwords, and passwords from open-source wordlists are a no go.
# ==>For now we'll just stick with variable length strings made of random characters. The solution we want 


##TODO: We need to expand this from a simple username, password credential generation after PoC developed
class credentialGenerator:
    def __init__(self):
        self.usernamesUsed = 0
        self.credentialsUsed = []

    def generateUsername(self):
        with open("wordlists/jeanphorn-wordlist-usernames.txt") as infile:
            for i in range(self.usernamesUsed+1):
                username = infile.readline()
            
            return username.strip("\n")

    def generatePassword(self):
        return secrets.token_urlsafe(random.randint(8, 12))
            

    def generateCredentials(self):
        while True:
            userpassCreds = self.generateUsername(), self.generatePassword()
            if userpassCreds not in self.credentialsUsed:
                self.credentialsUsed.append(userpassCreds)
                break

        return userpassCreds





## Once we have generated user credentials we use stem to send them to the tor network

if __name__ == "__main__":
    cg = credentialGenerator()
    print(cg.generateCredentials())