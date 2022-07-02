## This main.py sets up the client and proxy together

import os
import sys
import json
import threading

from typing import Optional

sys.path.insert(0, "./client/")
sys.path.insert(0, "./proxies/")


import baitConnector

class beelurer:
	_supportedServices = baitConnector.supportedServices

	def __init__(self, serviceDefinitionPath: str) -> None:
		self._serviceDefinition = None
		self._clientServer = None
		self._proxyServer = None

		## We load in our definition
		self._readServiceDefinition(serviceDefinitionPath)

		## We then validate the configuration (NOTE: This should be validated before execution)
		# self._validateConfiguration()

		## We then need to setup the proxy and scanner
		self._setupClientServer()
		self._setupProxyServer()


	def _readServiceDefinition(self, path: str) -> None:
		with open(path, "r") as infile:
			self._serviceDefinition = json.load(infile)
	

	def _validateConfiguration(self) -> None:
		## NOTE: This should validate the service-definitions
		## NOTE: However, this should probably be done before creating the conatiner in the
		## `docker-setup.py` program
		...


	def _setupClientServer(self) -> None:
		## We need to read the service definition to define what baitConnectors we should use
		## TODO: The baitConnector subclasses are not ready to be integrated. We need to modify them
		## so that they can read several request types

		## NOTE: Our desire is that there is one thread for each protocol (and its encrypted version maybe)
		## Each protocol-specific baitConnector has access to multiple request formats
		...
	
	def _setupProxyServer(self) -> None:
		## NOTE: The proxy server is currently at an insufficient state to be integrated here
		## NOTE: Each protocol proxy should have its own thread (preferablly)
		...


	def run(self) -> None:
		## NOTE: This should run the threads for the baitconnectors and proxyserver
		... 


	def exit(self) -> None:
		## NOTE: After receiving a shutdown signal, this should shutdown the code running
		## inside of the threads (e.g. proxy or baitconnector)
		...
	
	





def main():
	## TODO: Define the arguments for the beelurer class, and then provide argument parsing
	serviceDefinitionPath = "../baitServices/default-httpservice/service-definitions.json"
	blr = beelurer(serviceDefinitionPath)
	blr.run()



if __name__ == "__main__":
	main()