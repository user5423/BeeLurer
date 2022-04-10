import sys
import pytest
sys.path.insert(0, "src/client/")

from baitConnector import baitConnector


class Test_baitConnector:
	## TODO: Expand these tests from torSessionManager init tests
	def test_init_baitConnector_invalidTorrcConfig(self):
		...

	def test_init_baitConnector_validTorrcConfig(self):
		...



	## TODO: Currently we are storing the exit node in memory instead of a
	## persistent database
	def test_logExitNodeConnection_noConnection(self):
		...

	def test_logExitNodeConnection_singleConnection(self):
		...

	def test_logExitNodeConnection_multipleConnections(self):
		...

	def test_logExitNodeConnection_previouslyConnected(self):
		...



	## TODO: These will be modified to abc.abstractmethods later so we want
	## to test for that
	def test_performBaitOperation(self):
		...

	def test_createRequestObject(self):
		...



	def test_testExitNode(self):
		...

	def test_run(self):
		...

	