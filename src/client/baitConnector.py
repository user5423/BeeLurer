from typing import Union, Optional, Dict, List, NamedTuple, Tuple
import threading
import datetime

# import pycurl
# import certifi
import clientExceptions
from httpRequestBuilder import httpRequestBuilder
from torSessionManager import torSessionManager

configType = Dict[str, Union[str, List[str], Dict[str, str]]]


class baitConnector(torSessionManager):
	_connection = NamedTuple("baitConnection", ["username", "password", "datetime"])

	def __init__(self, torrcConfig: Optional[configType] = None) -> None:
		torSessionManager.__init__(self, torrcConfig)

		self.sleepTime = 5
		self.connectionLog = {}
		self.currentThread = threading.Event()


	def run(self) -> None:
		##NOTE: Is there a reason to store all scans for exit nodes
		##First we get the exit nodes fingerprints
		while self.shutdownEvent.is_set() is False:
			self.retrieveExitNodes()
			for exitNodeFingerprint in self.exitNodes:
				self._testExitNode(exitNodeFingerprint)
				self.currentThread.wait(self.sleepTime)


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


	##NOTE: Currently we are storing our bait requests in memory
	##TODO: However, we want to end up storing this in a database 
	def _logExitNodeConnection(self, fingerprint: str , connectionArgs: Dict[str]) -> None:
		##Here we sift through the variables that are used for authentication
		##TODO: This will be a more extensive function once we allow for other forms of http authentication
		connection = baitConnector._connection(connectionArgs["username"], connectionArgs["password"], datetime.now())
		if self.connectionLog.get(fingerprint) is None:
			self.connectionLog[fingerprint] = [connection]
		else:
			self.connectionLog[fingerprint].append(connection)

		return True


	def _performBaitOperation(self) -> Tuple[object, object]:
		## BUG: Pycurl is using a cached version of the results, so we will initate the pycurl handle for every connection just to be safe
		## NOTE: FRESH_CONNECT is an option in libcurl that might help us
		self._initiatePycurlHandle()

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
		requestObject = object()
		return requestObject


	def _performBaitConnection(self, requestObject: object) -> bool:
		return True



class baitHttpConnector(baitConnector, httpRequestBuilder):
	def __init__(self, requestFormatPath: str, torrcConfig: Optional[configType] = None) -> None:
		...


def main() -> None:
	bc = baitConnector()
	bc.run()
	bc.shutdown()

if __name__ == "__main__":
	main()
