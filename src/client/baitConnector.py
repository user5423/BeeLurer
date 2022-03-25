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
	def __init__(self, torrcConfig):
		self._setTorrcConfiguration(torrcConfig)
		self._initiateTorProcess()
		self._initiateTorController()

	def _setTorrcConfiguration(self, config):
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


	def _initiateTorProcess(self, config=None):
		config = config if config != None else self.config
		self.tor_process = stem.process.launch_tor_with_config(config)
		print("tor process created")


	def _initiateTorController(self, port=9051):
		self.controller = Controller.from_port(port=port)
		self.controller.set_caching(False)
		self.controller.authenticate()
		print("tor controller created")


	def _initiatePycurlHandle(self):
		self.curlHandle = pycurl.Curl()
		self.curlHandle.setopt(self.curlHandle.CAINFO, certifi.where())
		self.curlHandle.setopt(pycurl.PROXY, 'localhost')
		##TODO: Tor may be listening on a different port --> Remove hardcoded values
		self.curlHandle.setopt(pycurl.PROXYPORT, 9050) 
		self.curlHandle.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)


	def retrieveExitNodes(self):
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


	def changeExitNode(self, fingerprint):
		self.controller.set_conf("ExitNodes", fingerprint)


	def shutdownTorProcess(self):
		self.tor_process.kill()


	def shutdownTorController(self):
		self.controller.close()



class baitConnector(torSessionManager, credentialGenerator):
	def __init__(self, torrcConfig=None):
		torSessionManager.__init__(self, torrcConfig)
		credentialGenerator.__init__(self)

		self._initiatePycurlHandle()

		self.sleepTime = 5
		##This Datastructure will use fingerprint: { datetime: (username, password)}
		self.baitConnections = {}
		self.shutdownEvent = threading.Event()

		##TODO: Consider allowing multiple request formats after MVP developed
		self.loadRequestFormat()


	def loadRequestFormat(self):
		with open("requestFormat.json") as fp:
			self.requestFormat = json.load(fp)


	def craftHTTPTemplateRequest(self):
		##First we need the reqFormat loaded into a variable in the object
		requestFormat = copy.deepcopy(self.requestFormat)
		##We first start by generating the values for the variables
		requestFormat = self.generateVariables(requestFormat)
		##Then we find the variable in the template for url, headers, and body and replace them
		requestTemplate = self.templateReplaceVariables(requestFormat)
		##Return the requestTemplate to be used in the requestThroughTor methods
		return requestTemplate


	##TODO: When we introduce more authentication methods we'll need to make this more extensive
	def generateVariables(self, requestFormat):
		for templateValue, type in requestFormat["variables"].items():
			if type == "cg.username":
				requestFormat["variables"][templateValue] = self.generateUsername()
			elif type == "cg.password":
				requestFormat["variables"][templateValue] = self.generatePassword()

		return requestFormat

	
	def templateReplaceVariables(self, requestFormat):
		##Here we loop over the URL, Headers, and Body and perform replacement on {defaultVal}
		for key, value in requestFormat["variables"].items():
			template = "{" + key + "}"
			requestFormat["url"] = requestFormat["url"].replace(template, value)
			for index in range(len(requestFormat["headers"])):
				requestFormat["headers"][index] = requestFormat["headers"][index].replace(template, value)

			##TODO: Once we allow http post requests, we will need a way to deal with that because
			##there are numerous possible encodings that we would have to potentially deal with when performing
			##replacement strings

			##NOTE: The best way would most likely be to make the body into a string and perform replacement that way

		return requestFormat


	##TODO: Provide more options with the request, instead of just URL
	def getHTTPResourceThroughTor(self, encodedURL, customHTTPHeaders=[]):
		output = io.BytesIO()
		self.curlHandle.setopt(pycurl.URL, encodedURL)
		self.curlHandle.setopt(pycurl.HTTPHEADER, customHTTPHeaders)
		self.curlHandle.setopt(pycurl.FOLLOWLOCATION, True)
		self.curlHandle.setopt(pycurl.WRITEDATA, output)
		self.curlHandle.perform()
		return output.getvalue()




	def testExitNode(self, fingerprint):
		##First we need to reload tor with the new torrc that has the exit node we want
		##TODO: It's possible that a fingerprint we had no longer exists, so we need proper exception handling here
		self.changeExitNode(fingerprint)
		httpTemplateRequest = self.craftHTTPTemplateRequest()
		##The request crafting is dependent on the service that hides behind the proxy. We'll generate it in a compatible method
		##Therefore we require the user who decides on the service to create a json configuration file
		##NOTE: Pycurl is using a cached version of the results, so we will initate the pycurl handle for every connection just to be safe
		##NOTE: FRESH_CONNECT is an option in libcurl that might help us
		self._initiatePycurlHandle()
		encodedURL = httpTemplateRequest["url"]
		headers = httpTemplateRequest["headers"]

		try:
			##TODO: Allow for more requests than just get and post
			result = self.getHTTPResourceThroughTor(encodedURL, customHTTPHeaders=headers)
		except Exception:
			return None

		## Since the connection was succesful, we now store it in our data structure
		self.logExitNodeConnection(fingerprint, httpTemplateRequest["variables"])


	##NOTE: Currently we are storing our bait requests in memory
	##TODO: However, we want to end up storing this in a database 
	def logExitNodeConnection(self, fingerprint, variables):
		##Here we sift through the variables that are used for authentication
		##TODO: This will be a more extensive function once we allow for other forms of http authentication
		baitConnection = (variables["username"], variables["password"], datetime.now())
		if self.baitConnections.get(fingerprint) == None:
			self.baitConnections[fingerprint] = [baitConnection]
		else:
			self.baitConnections[fingerprint].append(baitConnection)

		
	def runBaitConnector(self):
		##NOTE: Is there a reason to store all scans for exit nodes
		##First we get the exit nodes fingerprints
		while self.shutdownEvent.is_set() == False:
			self.retrieveExitNodes()
			for exitNodeFingerprint in self.exitNodes:
				self.testExitNode(exitNodeFingerprint)
				time.sleep(self.sleepTime)
		
		##We then loop through each fingerprint (waiting a set period to avoid overloading the network)
		##we create a circuit with that exit node as our network
		##We then send the bait connection over via the tor port


def main():
	bc = baitConnector()
	# print(len(bc.retrieveExitNodes()))
	bc.runBaitConnector()
	bc.shutdownTorController()
	bc.shutdownTorProcess()

if __name__ == "__main__":
	main()