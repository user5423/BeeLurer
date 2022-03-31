from typing import Dict, Any, List, ClassVar, Set, Optional, Iterator, TextIO, NamedTuple
from dataclasses import dataclass, field
import json
import random
import secrets

import yarl
import validators
import requests
import clientExceptions

## TODO: We need to expand this from a simple username, password credential generation
## after PoC developed to a range of authentication methods

class httpAuthGen:
	_usernameWordlistFile = "wordlists/jeanphorn-wordlist-usernames.txt"
	_userpassFormat = NamedTuple("userpass", ["username", "password"])


	def __init__(self) -> None:
		self.credentialsUsed = []
		self.usernameGenerator = None


	def generateUserpass(self) -> "httpAuthGen._userpass":
		while True:
			userpass = httpAuthGen._userpassFormat(self.generateUsername(), self.generatePassword())
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
		with open(httpAuthGen._usernameWordlistFile, "r") as infile:
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
			

@dataclass
class httpHeaders:
	_headers: Dict[str, str] = field(init=False, default_factory=dict)
	
	def setHeader(self, header: str, value: str) -> None:
		self._headers[header] = value

	def setHeaders(self, headerDict: Dict[str, str]) -> None:
		for key, value in headerDict.items():
			self._headers[key] = value

	def removeHeader(self, header: str) -> None:
		try:
			del self._headers[header]
		except KeyError: 
			pass

	def generateHeaderList(self) -> List[str]:
		return [": ".join(header) for header in self._headers]


@dataclass
class httpBody:
	_body: Any = field(init=False)
	_contentType: str = field(init=False)

	def setBody(self, body: Any, contentType: str) -> None:
		self._body = body
		self._contentType = contentType


@dataclass
class httpQuery:
	_query: Any = field(init=False, default_factory=dict)

	def setQueries(self, query: Dict[str, str]) -> None:
		for k,v in query.items():
			self._query[k] = v
	

@dataclass
class url:
	_url: yarl.URL = field(init=False)

	def setUrl(self, URL: str):
		## We need to encode and then validate, then create a yarl
		print(URL)
		if validators.url(URL):
			self._url = yarl.URL(URL)
		else:
			raise clientExceptions.InvalidUrlValue


@dataclass
class httpRequest:
	url: str = field(default=None)
	method: str = field(default="GET")
	headers: dict[str,str] = field(default_factory=dict)
	body: Any = field(default_factory=dict)
	query: dict[str,str] = field(default_factory=dict)
	auth: Optional[dict[str, Any]] = field(default=None)
	_contentType: str = field(init=False, default='application/json')
	_supportedMethods: ClassVar[Set[str]] = field(
		init=False,
		default={"GET", "POST", "PUT", "DELETE", "PATCH", "UPDATE", "HEAD", "CONNECT", "TRACE", "OPTIONS"}
	)

	def __post_init__(self):
		self.createUrl(self.url)
		self.createHeaders(self.headers)
		self.createBody(self.body, self._contentType)
		self.createQuery(self.query)

		self.headers.setHeaders({"content-type": self._contentType})
	
	def setHttpMethod(self, method: str) -> None:
		if method not in httpRequest._supportedMethods:
			raise clientExceptions.UnsupportedHttpMethod
		else:
			self.method = method

	def createUrl(self, URL: str) -> None:
		self.url = url()
		self.url.setUrl(URL)

	def createBody(self, body: Any, contentType: str) -> None:
		self.body = httpBody()
		self.body.setBody(body, contentType)

	def createHeaders(self, headers: Dict[str, str]) -> None:
		self.headers.setHeaders(headers)

	def createQuery(self, query: Dict[str, str]) -> None:
		self.query = httpQuery()
		self.query.setQueries(query)


	## NOTE: After the http request has been fully set, we need to be able to generate
	## a datastructure to return values
	def getMethod(self):
		return self.method

	## TODO: This needs to be significantly more robust
	def getUrl(self):
		## THis needs to get the url from YARL object and the parameters in Query
		querystring = ""
		for k,v in self.query.items():
			querystring += f"{k}={v}"
		return requests.utils.quote(f"{self.url}?{querystring}")

	def getBody(self):
		return self.body

	def getHeaders(self):
		headers = []
		for k,v in self.headers.items():
			headers.append(f"{k}: {v}")
		return headers


class httpRequestBuilder:
	"""Provides methods to build http request based on defined formats"""
	def __init__(self) -> None:
		self.httpAuth = httpAuthGen()

	def build(self, httpRequestTemplate: Dict[str, Any], arguments: Dict[str, str]) -> httpRequest:
		"""Creates a `httpRequest` object using an httpRequestTemplate and valid arguments"""
		## First we want to receive the httpRequestFormat json object
		## Then we start on the arguments - we need to check if it adheres to the definition
		httpRequestTemplate = self._variableReplace(httpRequestTemplate, arguments)
		## Then we work on generate the credentials
		httpRequestTemplate = self._authenticationGenerate(httpRequestTemplate)
		## TODO: we need to work on handling derived arguments
		httpRequestTemplate = self._handleDerivedArguments(httpRequestTemplate, arguments)
		## NOTE: Finally, we use the httpRequestTemplate arguments and auth to replace the other structures
		httpRequestTemplate = self._templateReplace(httpRequestTemplate)
		## Once the requestFormat has been filled properly, we can then build the httpRequest
		return self._buildHttpRequest(httpRequestTemplate)


	def _variableReplace(self, httpRequestTemplate: Dict[str, Any], arguments: Dict[str, str]) -> Dict[str, Any]:
		## Here we validate the arguments
		templateVariableLen = len(httpRequestTemplate.get('variables', []))
		if len(arguments) != templateVariableLen:
			errorMsg = f"The arguments object was expected to have \
			{templateVariableLen}, but only {len(arguments)} were received"
			raise clientExceptions.IncorrectArgumentSizeException(errorMsg)

		for k,v in arguments.items():
			if k in httpRequestTemplate['variables']:
				httpRequestTemplate['variables'][k] = v
			else:
				errorMsg = f"The argument object should not have the '{k}' argument"
				raise clientExceptions.InvalidArgumentException(errorMsg)

		return httpRequestTemplate


	def _authenticationGenerate(self, httpRequestTemplate: Dict[str, Any]) -> Dict[str, Any]:
		## NOTE: The only supported authentication method is userpass
		## ==> The plan is to support different authentication types later on
		print(httpRequestTemplate)
		if "userpass" in httpRequestTemplate['authentication']:
			httpRequestTemplate['authentication']['userpass'] = self.httpAuth.generateUserPass()
		else:
			errorMsg = "There is no userpass authentication method provided in the httpRequestTemplate"
			raise clientExceptions.AbsentAuthMethodException(errorMsg)

		return httpRequestTemplate


	def _handleDerivedArguments(self, httpRequestTemplate: Dict[str, Any], arguments: Dict[str, str]) -> Dict[str, Any]:
		## TODO: this mostly refers to content-type
		return httpRequestTemplate


	def _templateReplace(self, httpRequestTemplate: Dict[str, Any]) -> Dict[str, Any]:
		arguments = {}
		arguments.update(httpRequestTemplate["variables"])
		arguments.update(httpRequestTemplate["authentication"]["userpass"])
		## NOTE: Once we provide more sofisticated authentication methods, this will change
		return self._iterateTemplateReplacement(httpRequestTemplate, arguments)


	def _iterateTemplateReplacement(self, template: Dict[str, Any], arguments: Dict[str, str]) -> None:
		print(arguments)
		for k, v in template.items():
			## If it is a dictionary, then we recurse into it (variables should only be observed in terminal values of a dict)
			if isinstance(v, dict):
				self._iterateTemplateReplacement(v, arguments)
			## if the value is a argument (i.e. starts with $)
			elif isinstance(v, list):
				## Here in case we wish to modify this later on
				pass
			elif isinstance(v, str):
				placeholders = self._getPlaceholderIndices(v)
				if len(placeholders) == 0:
					continue
				
				for positions in placeholders[::-1]:
					start = positions[0]
					end = positions[1]
					parameter = v[start+2:end]
					## check if it was provided (i.e. was it provided as an argument)
					if parameter in arguments:
						template[k] = template[k].replace(f"${{{parameter}}}", arguments[parameter])
					else:
						## We got a placeholder for which no argument was provided
						errorMsg = f"The httpRequestTemplate has a parameter for the key {k}, \
						where no argument was provided for it"
						raise clientExceptions.TemplateArgumentError(errorMsg)
				## otherwise, we should have a constant value, so we leave it alone
				else: 
					pass
				
		return template

	def _getPlaceholderIndices(self, string):
		## NOTE: This will NOT support indented placeholders
		placeholders = []
		bProtected = False
		for index in range(len(string)):
			if bProtected is False:
				if string[index] == '$' and string[index+1] == '{':
					placeholders.append([index])
					bProtected = True
			else:
				if string[index] == '}':
					if index - placeholders[-1][0] < 3: ## You can't have a placeholder with 3chars ${}
						# raise EmptyPlaceholderException()
						raise Exception()
					else:
						placeholders[-1].append(index)
						bProtected = False
		return placeholders



	def _buildHttpRequest(self, httpRequestTemplate: Dict[str, Any]):
		## TODO: Fix the url and query attribute redundancy
		## TODO: Fix the header redundancy between auth object and auth variables that have replaced the url, headers, or body
		return httpRequest(
			url=httpRequestTemplate['url'],
			body=httpRequestTemplate['body'],
			method=httpRequestTemplate['method'],
			headers=httpRequestTemplate['headers'],
			auth=httpRequestTemplate['authorization']
		)


		## We need to be able to fuzz certain attributes, 
		## --> This means that we require an httpRequestBuilder to easily create http request objects
		## --> Then using a definition, we define what attributes are constant, and which attributes
		## are generated randomly/dynamically

		## The way we need to define the format is as follows

		## We read a config file whose values are either constants or variables that
		## can are dynamically derived from the definitinos

		## There are 4 attributes:
		## 1. Method
		## 2. URL
		## 3. Body
		## 4. Headers
		## 4. Path Queries

		## TODO: In the future, we want to fuzz certain attributes to provide some variance
		## in the requests to make it more difficult for an adversary to blacklist requests

		## NOTE: What is required now, is that we are able to replace certain placeholder parameters
		## in the request with the arguments provided to the httpRequestBuilder class
		## --> This will be defined by the structure of the conf file

def main():
	arguments = {"host": "127.0.0.1"}
	with open("httpRequestFormat.json", "r") as infile:
		template = json.load(infile)

	hrb = httpRequestBuilder()
	req = hrb.build(template, arguments)


if __name__ == "__main__":
	main()