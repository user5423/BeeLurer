from re import template
from stem.control import Controller
from stem.descriptor import parse_file
import stem.process
import pprint
import os
import datetime
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

##TODO: Implement try and except argument with the custom errors used by stem

##We need a way to allow the user to show how to create the request


class baitConnector:
	def __init__(self, torrcConfig=None):
		self._setTorrcConfiguration(torrcConfig)
		self._initiateTorProcess()
		self._initiateTorController()

		self._initiatePycurlHandle()
		self._initateCredentialGenerator()

		self.sleepTime = 5
		##This Datastructure will use fingerprint: { datetime: (username, password)}
		self.baitConnections = {}
		self.shutdownEvent = threading.Event()

		##TODO: Consider allowing multiple request formats after MVP developed
		self.loadRequestFormat()


	def _initateCredentialGenerator(self):
		self.credentialGenerator = credentialGenerator()


	def _initiatePycurlHandle(self):
		self.curlHandle = pycurl.Curl()
		self.curlHandle.setopt(self.curlHandle.CAINFO, certifi.where())
		self.curlHandle.setopt(pycurl.PROXY, 'localhost')
		##TODO: Tor may be listening on a different port --> Remove hardcoded values
		self.curlHandle.setopt(pycurl.PROXYPORT, 9050) 
		self.curlHandle.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
		

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
		try:
			self.controller.set_caching(False)
			self.controller.authenticate()
			print("tor controller created")
		except Exception as e:
			print(e)


	def shutdownTorProcess(self):
		self.tor_process.kill()

	def shutdownTorController(self):
		self.controller.close()


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
		print(requestTemplate)
		return requestTemplate


	##TODO: When we introduce more authentication methods we'll need to make this more extensive
	def generateVariables(self, requestFormat):
		for templateValue, type in requestFormat["variables"].items():
			if type == "cg.username":
				requestFormat["variables"][templateValue] = self.credentialGenerator.generateUsername()
			elif type == "cg.password":
				requestFormat["variables"][templateValue] = self.credentialGenerator.generatePassword()

		return requestFormat

	
	def templateReplaceVariables(self, requestFormat):
		##Here we loop over the URL, Headers, and Body and perform replacement on {defaultVal}
		for key, value in requestFormat["variables"].items():
			template = "{" + key + "}"
			requestFormat["url"].replace(template, value)

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


	def testExitNode(self, fingerprint):
		##First we need to reload tor with the new torrc that has the exit node we want
		##TODO: It's possible that a fingerprint we had no longer exists, so we need proper exception handling here
		try:
			print(fingerprint)
			self.controller.set_conf("ExitNodes", fingerprint)
		except Exception as e:
			print(e)
			return None

		httpTemplateRequest = self.craftHTTPTemplateRequest()
		
		##The request crafting is dependent on the service that hides behind the proxy. We'll generate it in a compatible method
		##Therefore we require the user who decides on the service to create a json configuration file

		##NOTE: Pycurl is using a cached version of the results, so we will initate the pycurl handle for every connection just to be sage
		##NOTE: FRESH_CONNECT is an option in libcurl that might help us
		self._initiatePycurlHandle()

		encodedURL = httpTemplateRequest["url"]
		headers = httpTemplateRequest["headers"]
		# body = httpTemplateRequest["body"]

		try:
			##TODO: Allow for more requests than just get and post
			result = self.getHTTPResourceThroughTor(encodedURL, customHTTPHeaders=headers)
		except Exception:
			return None

		## Since the connection was succesful, we now store it in our data structure
		# self.storeExitNodeBaitCreds(fingerprint, username, password)


	##NOTE: Currently we are storing our bait requests in memory
	##TODO: However, we want to end up storing this in a database 
	def storeExitNodeBaitCreds(self, fingerprint, username, password):
		baitConnection = [username, password, datetime.datetime()]
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

		return



def main():
	bc = baitConnector()
	# print(len(bc.retrieveExitNodes()))
	bc.runBaitConnector()
	bc.shutdownTorController()
	bc.shutdownTorProcess()

if __name__ == "__main__":
	main()
