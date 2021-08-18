import random
from stem.control import Controller
from stem.descriptor import parse_file
import stem.process
from datetime import datetime
from re import template

import pprint
import os
import threading
import time
import pycurl
import certifi
import io
import colorama
import json
import copy
from credentialGenerator import credentialGenerator
from credentialGenerator import credentialGenerator as cg


from typing import Any, Dict, List, Mapping, Optional, Sequence

## Firstly, we need a docker container that will handle all the communication between the client and the server
## This will include generating the unique credentials, updating a database, and alerting if credentials were used

## The basic workflow would be as follows

# 1. Client requests new credentials to be issued from server
# 2. Client sends these credentials in plaintext through the Tor network
# 3. Server receives the requests from the tor network, maps the credentials to the ip address receieved, with a date-time-stamp

## NOTE: IP addresses tend to be recycled, and it could be possible (unlikely) that another exit node has that IP address some time in the future, so we don't want to flag it accidentally

# 4. The server then in the future receieves a second request using those credentials (possibly from a different IP address), and maps it to the exit node
# 5. The server would then provide this information to the correct authorities to deal with as feels


## A better workflow is to eliminate the client from it
# The client's only job would be to setup the server from their machine, then the machine would handle all work
# This way an adversary wouldn't be able to intercept any requests on step 1, or would be able to generate their own credentials to cause mayhem through false reports

## Simplified workflow:
## NOTE: Assume that the server is setup

# 1. The server generates new credentials
# 2. The server then checks on its list of unused exit nodes where to route the request
# 3. The request is routed to self through the tor network
# 4. Once the request is receieved, the unique credentials are mapped to a ip address of an exit-node at a point in time
# 5. If the credentials are then used in a future request, then send an alert to a pre-configured location (e.g. email, phone, webhook)


## The potential architecture:

# 1a. "Proxy container" -- this container will handle receiving the request, talking to the database, and passing the request to the main honeypot container
# This can be considered a proxy server. However, we need to note that on file request

# 1b. "Log-inspector container" -- alternatively, this container will look at the logs of the main honeypot service via a socket or a shared volume
## The main honeyport server receieves the requests and logs them all, and every so often the log-inspector container will read it

# The first solution provides seperation of the honeypot from the beelurer container, but port scanning might show other information
# However, the second, would be a lot simpler to implemenent, but the first but be quite easy out of the box to configure



##TODO: Implement try and except argument with the custom errors used by stem
##We need a way to allow the user to show how to create the request
class torSessionManager:
	def __init__(self, torrcConfig: Optional[Dict[str, Any]] = None) -> None:
		self._initiateTorProcess(torrcConfig)
		self._initiateTorController()
		self._initiatePycurlHandle()

	def _setTorrcConfiguration(self, config: Optional[Dict[str, Any]] = None) -> None:
		##TODO: Consider adding error checking for Torrc config arguments
		defaultConfig = {
			'ControlPort' : '9051',
			'DataDirectory': '/tmp',
			'Log' : [
				'NOTICE stdout',
				'ERR file /tmp/tor_error_log'
			]
		}

		self.config = config if config != None else defaultConfig


	def _initiateTorProcess(self, config: Optional[Dict[str, Any]] = None) -> None:
		self._setTorrcConfiguration(config)
		self.tor_process = stem.process.launch_tor_with_config(self.config)
		print("tor process created")


	def _initiateTorController(self, port: int = 9051) -> None:
		self.controller = Controller.from_port(port=port)
		try:
			self.controller.set_caching(False)
			self.controller.authenticate()
			print("tor controller created")
		except Exception as e:
			print(e)


	def _initiatePycurlHandle(self) -> None:
		self.curlHandle = pycurl.Curl()
		self.curlHandle.setopt(self.curlHandle.CAINFO, certifi.where())
		self.curlHandle.setopt(pycurl.PROXY, 'localhost')
		##TODO: Tor may be listening on a different port --> Remove hardcoded values
		self.curlHandle.setopt(pycurl.PROXYPORT, 9050) 
		self.curlHandle.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)


	def retrieveExitNodes(self) -> None:
		exit_digests = set()
		exit_fingerprints = set()
		data_dir = self.controller.get_conf('DataDirectory')

		for desc in self.controller.get_microdescriptors():
			if desc.exit_policy.is_exiting_allowed():
				exit_digests.add(desc.digest(encoding='HEX'))

		for desc in parse_file(os.path.join(data_dir, 'cached-microdesc-consensus')):
			if desc.digest in exit_digests:
				exit_fingerprints.add(desc.fingerprint)

		##With the exit nodes we want to associate a datetime

		##The structure wants to take into account previous retrievals
		self.exitNodes = exit_fingerprints


	def changeExitNode(self, fingerprint: str) -> None:
		try:
			self.controller.set_conf("ExitNodes", fingerprint)
			print(fingerprint)
		except Exception as e:
			print(e)
			return None

		##BUG: Pycurl is using a cached version of the results, so we will initate the pycurl handle for every connection just to be safe
		##NOTE: However, pycurl by default shouldn't be returning cached results. This might be a bug todo with stem returning cached results
		##NOTE: FRESH_CONNECT is an option in libcurl that might help us
		self._initiatePycurlHandle()


	def shutdownTorProcess(self) -> None:
		self.tor_process.kill()


	def shutdownTorController(self) -> None:
		self.controller.close()



class baitConnector(torSessionManager, credentialGenerator):
	def __init__(self, torrcConfig: Optional[Dict[str, str]] = None) -> None:
		torSessionManager.__init__(self, torrcConfig)
		credentialGenerator.__init__(self)

		##This Datastructure will use fingerprint: { datetime: (username, password)}
		self.baitConnections = {}
		self.defaultWaitTime = 5

		self.exitNodes = {}
		self.visitedNodes = {}

		self.suspensionEvent = threading.Event()
		self.shutdownEvent = threading.Event()

		self.requestFormat = self.loadRequestFormat()


	##TODO-F: Support multiple request types after MVP developed
	def loadRequestFormat(self) -> None:
		with open("requestFormat.json") as fp:
			return json.load(fp)


	def craftHTTPTemplateRequest(self) -> Mapping[str, str]:
		##First we need the reqFormat loaded into a variable in the object
		requestFormat = copy.deepcopy(self.requestFormat)
		##We first start by generating the values for the variables
		requestFormat = self.generateCredentials(requestFormat)
		##Then we find the variable in the template for url, headers, and body and replace them
		requestTemplate = self.templateReplaceVariables(requestFormat)
		##Return the requestTemplate to be used in the requestThroughTor methods
		return requestTemplate


	##TODO: When we introduce more authentication methods we'll need to make this more extensive
	def generateCredentials(self, requestFormat: Mapping[str, str]):
		for templateValue, type in requestFormat.pop("credentials").items():
			if type == "cg.username":
				requestFormat["variables"][templateValue] = self.generateUsername()
			elif type == "cg.password":
				requestFormat["variables"][templateValue] = self.generatePassword()

		return requestFormat


	## TODO: Change from default strings to customizable strings, otherwise its too easy to be blacklisted by user-string
	## The selection of values for headers in the future will be decided based on a selected "profile" for the baitConnector host.
	## e.g. we might pretend to be a linux machine, so our user string would show that, and stuff in tcp header that may suggest linux will reflect it, e.g. evading tools like pOf.
	def generateDefaultHeaders(self) -> Sequence[str]:
		defaultHeaders = []
		defaultHeaders.append(f"User-Agent: {self.generateUserAgent()}")
		defaultHeaders.append(f"Accept-Encoding: {self.generateAcceptEncoding()}")
		defaultHeaders.append(f"Accept-Language: {self.generateAcceptLanguage()}")
		defaultHeaders.append(f"Content-Type: {self.generateContentType()}")
		defaultHeaders.append(f"Connection: {self.generateConnection()}")
		return defaultHeaders

	def generateUserAgent(self) -> str:
		userStrings = ["Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.3",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/43.4",
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
		"Mozilla/5.0 (iPhone; CPU iPhone OS 11_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"]
		return random.choice(userStrings)

	def generateAcceptEncoding(self) -> str:
		acceptEncodings = ["*", "gzip", "compress", "deflate", "br"]
		return random.choice(acceptEncodings)

	def generateAcceptLanguage(self) -> str:
		return "en-us"

	def generateContentType(self) -> str:
		return "text/html; charset=UTF-8"

	def generateConnection(self) -> str:
		connections = ["Keep-Alive", "keep-alive", "close"]
		return random.choice(connections)


	##TODO: Once we allow http post requests, we will need a way to deal with that because thereare numerous possible methods
	##to populate the data within the request template
	##NOTE: The best way would most likely be to make the body into a string and perform replacement that way
	def templateReplaceVariables(self, requestFormat):
		##Here we loop over the URL, Headers, and Body and perform replacement on {defaultVal}
		for key, value in (requestFormat["variables"]).items():
			template = "{" + key + "}"
			requestFormat["url"] = requestFormat["url"].replace(template, value)
			for index in range(len(requestFormat["headers"])):
				requestFormat["headers"][index] = requestFormat["headers"][index].replace(template, value)

		return requestFormat


	##TODO: Provide more options with the request, instead of just URL
	def httpgetResourceViaTor(self, encodedURL: str, customHTTPHeaders: List = []) -> bytes:
		output = io.BytesIO()
		self.curlHandle.setopt(pycurl.URL, encodedURL)
		self.curlHandle.setopt(pycurl.HTTPHEADER, customHTTPHeaders)
		self.curlHandle.setopt(pycurl.FOLLOWLOCATION, True)
		self.curlHandle.setopt(pycurl.WRITEDATA, output)
		self.curlHandle.perform()
		return output.getvalue()

	def baitExitNode(self, fingerprint: str) -> None:
		##First we need to reload tor with the new torrc that has the exit node we want
		##TODO: It's possible that a fingerprint we had no longer exists, so we need proper exception handling here
		self.changeExitNode(fingerprint)

		##The request crafting is dependent on the service that hides behind the proxy. We'll generate it in a compatible method
		##Therefore we require the user who decides on the service to create a json configuration file
		httpTemplateRequest = self.craftHTTPTemplateRequest()
		httpTemplateRequest["headers"] = self.generateDefaultHeaders()

		encodedURL = httpTemplateRequest["url"]
		headers = httpTemplateRequest["headers"]

		try:
			##TODO: Allow for more requests than just get and post
			self.httpgetResourceViaTor(encodedURL, customHTTPHeaders=headers)
		except pycurl.error:
			return None

		## Since the connection was succesful, we now store it in our data structure
		self.logExitNodeConnection(fingerprint, httpTemplateRequest["credentials"])


	##NOTE: Currently we are storing our bait requests in memory
	##TODO: However, we want to end up storing this in a database 
	def logExitNodeConnection(self, fingerprint: str, variables: Dict[str, str]) -> None:
		##Here we sift through the variables that are used for authentication
		##TODO: This will be a more extensive function once we allow for other forms of http authentication
		baitConnection = (variables["username"], variables["password"], datetime.now())
		if self.baitConnections.get(fingerprint) == None:
			self.baitConnections[fingerprint] = [baitConnection]
		else:
			self.baitConnections[fingerprint].append(baitConnection)

		
	def runBaitConnector(self) -> None:
		##NOTE: Is there a reason to store all scans for exit nodes
		##First we get the exit nodes fingerprints
		while self.shutdownEvent.is_set() == False:
			self.retrieveExitNodes()
			for fingerprint in self.exitNodes:
				if fingerprint in self.visitedNodes:continue
				self.baitExitNode(fingerprint)
				self.suspensionEvent.wait(self.defaultWaitTime)
		


def main():
	bc = baitConnector()
	# print(len(bc.retrieveExitNodes()))
	bc.runBaitConnector()
	bc.shutdownTorController()
	bc.shutdownTorProcess()

if __name__ == "__main__":
	main()
