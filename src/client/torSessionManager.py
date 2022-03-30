import os
import logging
from typing import Dict, List, Union, Optional

import pycurl
import certifi
import stem.process
from stem.control import Controller
from stem.descriptor import parse_file

import clientExceptions

logging.basicConfig(filename='client.log', encoding='utf-8', level=logging.DEBUG)

configType = Dict[str, Union[str, List[str], Dict[str, str]]]
## TODO: Implement try and except argument with the custom errors used by stem
## We need a way to allow the user to show how to create the request
class torSessionManager:
	def __init__(self, torrcConfig: Dict[str, str]) -> None:
		self.exitNodes = []
		self.curlHandle = None

		self._setTorrcConfiguration(torrcConfig)
		self._initiateTorProcess()
		self._initiateTorController()

	def _setTorrcConfiguration(self, config: Optional[Dict[str, str]] = None) -> None:
		## TODO: Consider adding error checking for Torrc config arguments
		defaultConfig = {
			'ControlPort' : '9051',
			'DataDirectory': '/tmp',
			'Log' : [
				'NOTICE stdout',
				'ERR file /tmp/tor_error_log'
			]
		}

		self.config = config if config is not None else defaultConfig


	def _initiateTorProcess(self) -> None:
		try:
			print("Creating Tor Process...")
			self.tor_process = stem.process.launch_tor_with_config(self.config)
			print("Tor Process created\n")
			logging.info("Tor Process created")
		except OSError as e:
			logging.debug("TorProcessCreationException: %s", e)
			raise clientExceptions.TorProcessCreationException from e


	def _initiateTorController(self, port: int = 9051) -> None:
		try:
			print("Creating Tor Controller...")
			self.controller = Controller.from_port(port=port)
			self.controller.set_caching(False)
			self.controller.authenticate()
			print("Tor Controller connected\n")
			logging.info("Tor Controller connected")
		except stem.connection.AuthenticationFailure as e:
			logging.debug("TorControllerCreationException: %s", e)
			raise clientExceptions.TorControllerCreationException from e

	def _initiatePycurlHandle(self) -> None:
		self.curlHandle = pycurl.Curl()
		self.curlHandle.setopt(self.curlHandle.CAINFO, certifi.where())
		self.curlHandle.setopt(pycurl.PROXY, 'localhost')
		## TODO: Tor may be listening on a different port --> Remove hardcoded values
		self.curlHandle.setopt(pycurl.PROXYPORT, 9050) 
		self.curlHandle.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)

	
	def _shutdownTorProcess(self) -> None:
		try:
			self.tor_process.kill()
			print("Tor Process has been killed")
			logging.info("Tor Process has been killed")
		except OSError as e:
			logging.debug("TorProcessShutdownException: %s", e)
			raise clientExceptions.TorProcessKillException from e


	def _shutdownTorController(self) -> None:
		try:
			self.controller.close()
			print("Tor Controller has been closed")
			logging.info("Tor Controller has been closed")
		except Exception as e:
			logging.debug("TorControllerShutdownException: %s", e)
			raise clientExceptions.TorControllerShutdownException from e


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
		self.controller.set_conf("ExitNodes", fingerprint)

	def shutdown(self) -> None:
		self._shutdownTorProcess()
		self._shutdownTorController()
		