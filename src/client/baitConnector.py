from typing import Union, Optional, Dict, List, NamedTuple, Tuple
import threading
import datetime
import json
import io
import pycurl
# import certifi
import clientExceptions

from httpRequest import httpRequest, httpRequestBuilder
from torSessionManager import torSessionManager

configType = Dict[str, Union[str, List[str], Dict[str, str]]]


class baitConnector(torSessionManager):
	_connection = NamedTuple("baitConnection", [("username", str), ("password", str), ("datetime", datetime.datetime)])

	def __init__(self, torrcConfig: Optional[configType] = None) -> None:
		torSessionManager.__init__(self, torrcConfig)

		self.sleepTime = 5
		self.connectionLog = {}
		self.currentThread = threading.Event()

		self.requestTemplate = None

	def run(self) -> None:
		## NOTE: Is there a reason to store all scans for exit nodes
		## First we get the exit nodes fingerprints
		while self.shutdownEvent.is_set() is False:
			self.retrieveExitNodes()
			for exitNodeFingerprint in self.exitNodes:
				self._testExitNode(exitNodeFingerprint)
				self.currentThread.wait(self.sleepTime)


	def _loadRequestTemplate(self, requestTemplatePath: str) -> None:
		with open(requestTemplatePath, "r") as infile:
			self.requestTemplate = json.load(infile)


	def _testExitNode(self, fingerprint: str) -> None:
		## We start by modifying the exit node to the fingerprint we want to test
		## TODO: It is possible that the exit node no longer exists -- Add error handling to this
		self.changeExitNode(fingerprint)
		## We then perform the bait connection -- this could be http, smtp, or another protocol
		try:
			connectionArgs = self._performBaitOperation()
		except (clientExceptions.TemplateFailureException, 
			clientExceptions.ConnectionFailureException):
			return False
		
		return self.logExitNodeConnection(fingerprint, connectionArgs)


	## NOTE: Currently we are storing our bait requests in memory
	## TODO: However, we want to end up storing this in a database 
	def _logExitNodeConnection(self, fingerprint: str , connectionArgs: NamedTuple) -> None:
		## Here we sift through the variables that are used for authentication
		## TODO: This will be a more extensive function once we allow for other forms of http authentication
		connection = baitConnector._connection(connectionArgs["username"], connectionArgs["password"], datetime.datetime.now())
		if self.connectionLog.get(fingerprint) is None:
			self.connectionLog[fingerprint] = [connection]
		else:
			self.connectionLog[fingerprint].append(connection)

		return True

	## TODO: Add more specific Exceptions
	def _performBaitOperation(self) -> Tuple[object, object]:
		"""This is the default performOperation that works by subclasses overrideing the below methods used.
		   This can also be overrided instead if the protocol requires a workflow that doesn't conform to the below"""

		## 1. Performs the template replacement and argument generation
		try:
			requestObject = self._createRequestObject()
		except (Exception) as e:
			raise clientExceptions.TemplateFailureException from e

		## 2. Using the above arguments, perform a curl request
		try:  
			self._performBaitConnection(requestObject)
		except (Exception) as e:
			raise clientExceptions.ConnectionFailureException from e

		## 3. Return the unique credential set that were used
		return requestObject.auth


	def _createRequestObject(self) -> object:
		"""The `baitConnector` subclasses should override this function which should return a request object"""
		return object()


	def _performBaitConnection(self, requestObject: object) -> bool:
		"""The `baitConnector` subclasses should override this function which should return perform a request using a request object"""
		return True


class httpBaitConnector(baitConnector, httpRequestBuilder):
	def __init__(self, requestFormatPath: str, requestArguments: Dict[str, str], torrcConfig: Optional[configType] = None) -> None:
		baitConnector.__init__(self, torrcConfig)
		httpRequestBuilder.__init__(self)
		
		self.requestArguments = requestArguments
		self._loadRequestTemplate(requestFormatPath)


	def _createRequestObject(self) -> httpRequest:
		template = self.requestTemplate
		arguments = self.requestArguments
		return self.build(template, arguments)


	def _performBaitConnection(self, requestObject: httpRequest) -> bool:
		## BUG: Pycurl is using a cached version of the results, so we will initate the pycurl handle for every connection just to be safe
		## NOTE: FRESH_CONNECT is an option in libcurl that might help us
		self._initiatePycurlHandle()
		self._performBaitHttpRequest(httpRequest)
		## NOTE: There may require a more robust to check that we have communicating with our self via tor
		if self._isSuccessfulHTTPCode():
			return True
		return False


	def _isSuccessfulHTTPCode(self) -> bool:
		return self.curlHandle.getinfo(pycurl.RESPONSE_CODE) - 200 > 100


	def _performBaitHttpRequest(self, requestObject: httpRequest) -> bytes: 
		output = io.BytesIO()
		self.curlHandle.setopt(pycurl.URL, requestObject.url)
		self.curlHandle.setopt(pycurl.HTTPHEADER, requestObject.headers)
		self.curlHandle.setopt(pycurl.BODY, requestObject.body)
		self.curlHandle.setopt(pycurl.CUSTOMREQUEST, requestObject.method)

		self.curlHandle.setopt(pycurl.FOLLOWLOCATION, True)
		self.curlHandle.setopt(pycurl.WRITEDATA, output)
		self.curlHandle.perform()
		return output.getvalue()



def main() -> None:
	bc = baitConnector()
	bc.run()
	bc.shutdown()

if __name__ == "__main__":
	main()
