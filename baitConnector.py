from stem.control import Controller
from stem.descriptor import parse_file
import stem.process
import pprint
import os

##TODO: Implement try and except argument with the custom errors used by stem



class baitConnector:
	def __init__(self, config=None):
		self._setTorrcConfiguration(config)
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
		try:
			self.controller.set_caching(False)
			self.controller.authenticate()
		except Exception as e:
			print(e)
			return

		print("tor controller created")


	def shutdownTorProcess(self):
		self.tor_process.kill()


	def shutdownTorController(self):
		self.controller.close()


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
	
		return exit_fingerprints


def main():
	bc = baitConnector()
	print(len(bc.retrieveExitNodes()))

	bc.shutdownTorController()
	bc.shutdownTorProcess()

if __name__ == "__main__":
	main()
