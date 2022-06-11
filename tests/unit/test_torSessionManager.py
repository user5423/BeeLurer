import sys
import unittest
sys.path.insert(0, 'src/client/')

from torSessionManager import torSessionManager


class Test_TorSessionManager:

	## These unittests should test: 
	## 1. torSessionManager._setTorrcConfiguration()
	## 2. torSessionManager._initiateTorProcess()

	def test_init_Default(self):
		...

	def test_init_EmptyDict(self):
		...

	def test_init_AbsentConfigKeys(self):
		...

	def test_init_IncorrectValueConfigKey(self):
		...

	def test_init_IncorrectValueConfigKeys(self):
		...

	def test_init_NonexistentConfigKeys(self):
		...

	def test_init_IncorrectFormatConfigValue(self):
		...

	def test_init_IncorrectFormatConfigValues(self):
		...

	def test_init_IncorrectValueConfigValues(self):
		...

	def test_init_IncorrectValuesConfigValues(self):
		...


	## These unittests should test
	## 1. torSessionManager._initiateTorProccess()

	def test_init_ProcessAlreadyListeningOnPort(self):
		...

	def test_init_TorNotInstalled(self):
		...

	def test_init_TorProcessFailedToStartup(self):
		...

	def test_init_torSessionManagerObjectKilled(self):
		...

	def test_init_torSessionManagerProcessKilled(self):
		...


	## These unittests should test:
	## 1. torSessionManager._initiateTorController(self):

	def test_init_TorControlPortAlreadyListened(self):
		...

	def test_init_TorControlPortNotListened(self):
		...

	def test_init_TorControlFailedToAuthenticate(self):
		...


	## These unittests should test all functions called by torSessionManager.__init__():
	## 1. torSessionManager._setTorrcConfiguration()
	## 2. torSessionManager._initiateTorProcess()
	## 3. torSessionManager._initiateTorController(self):

	def test_init_defaultSuccess(self):
		...

	def test_init_customSuccess(self):
		...


	def test_retrieveExitNodes(self):
		...

	def test_changeExitNode(self):
		...

	def test_shutdown(self):
		...

