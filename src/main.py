## This main.py sets up the client and proxy together

import os
import sys
import json
import threading

sys.path.insert(0, "./client/")
sys.path.insert(0, "./proxies/")


import baitConnector

class beelurer:
	_supportedServices = baitConnector.supportedServices
	_beelurerConfigPath = "./fakeservice/"

	def __init__(self) -> None:
		self.beelurerConfiguration = self._readConfiguration()
		self._validateConfiguration()
		self._setup()


	def _readConfiguration(self) -> None:
		with open(beelurer._beelurerConfigPath, "r") as infile:
			return json.load(infile)
	

	def _validateConfiguration(self) -> None:
		...


	def _setup(self) -> None:
		...


	def run(self) -> None:
		... 
	





def main():
	beelurer().run()



main()