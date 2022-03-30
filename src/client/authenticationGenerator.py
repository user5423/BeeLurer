import random
import secrets
from typing import Iterator, TextIO, NamedTuple

## TODO: We need to expand this from a simple username, password credential generation
## after PoC developed to a range of authentication methods

class authenticationGenerator:
	_usernameWordlistFile = "wordlists/jeanphorn-wordlist-usernames.txt"
	_userpassFormat = NamedTuple("userpass", ["username", "password"])


	def __init__(self) -> None:
		self.credentialsUsed = []
		self.usernameGenerator = None


	def generateUserpass(self) -> "authenticationGenerator._userpass":
		while True:
			userpass = authenticationGenerator._userpassFormat(self.generateUsername(), self.generatePassword())
			if userpass not in self.credentialsUsed:
				self.credentialsUsed.append(userpass)
				break

		return userpass


	def _generateUsername(self) -> str:
		try:
			return next(self.usernameGenerator)
		except StopIteration:
			self.usernameGenerator = self._getUsernameFromFile()
			return next(self.usernameGenerator)


	def _getUsernameFromFile(self, minLength: int = 5, maxLength: int = 13) -> Iterator[str]:
		with open(authenticationGenerator._usernameWordlistFile, "r") as infile:
			while True:
				username = self._jumpForwardInFile(infile)
				if minLength <= len(username) <= maxLength and username not in self.credentialsUsed:
					yield username                


	def _jumpForwardInFile(self, fd: TextIO(), lines: int = random.randint(170, 250)) -> str:
		for _ in range(lines):
			username = fd.readline().strip("\n")
		return username


	def _generatePassword(self, minLength: int = 8, maxLength: int = 12) -> str:
		return secrets.token_urlsafe(random.randint(minLength, maxLength))
			
