import sys
import pytest
sys.path.insert(0, "src/client/")

from baitConnector import httpBaitConnector

class Test_httpBaitConnector:
	def test_init_invalidTorrcConfig(self):
		...

	def test_init_invalidRequestFormatPath(self):
		...

	def test_init_invalidRequestArgument(self):
		...


	## TODO: Expand this from the httpRequestBuilder tests
	def test_createRequestObject_invalidArguments(self):
		...

	## TODO: Expand this from the httpRequestBuilder tests
	def test_createRequestObject_invalidRequestTemplate(self):
		...



	## NOTE: We assume that the requestObject has been built correctly
	## --> See httpRequestObject and httpRequestBuilder tests
	def test_performBaitHttpRequest_2xxRequest(self):
		...

	def test_performBaitHttpRequest_3xxRequest(self):
		...

	def test_performBaitHttpRequest_4xxRequest(self):
		...

	def test_performBaitHttpRequest_5xxRequest(self):
		...

	def test_performBaitHttpRequest_RejectedConnection(self):
		...

	def test_performBaitHttpRequest_DroppedConnection(self):
		...

	def test_performBaitConnection_RequestTimeout(self):
		...

	def test_performBaitHttpRequest_2xxRequestThroughTor(self):
		...

	def test_performBaitHttpRequest_3xxRequestThroughTor(self):
		...

	def test_performBaitHttpRequest_4xxRequestThroughTor(self):
		...

	def test_performBaitHttpRequest_5xxRequestThroughTor(self):
		...

	def test_performBaitHttpRequest_TorRequestTimeout(self):
		...

	def test_performBaitHttpRequest_TorRejectedConnection(self):
		...

	def test_performBaitHttpRequest_TorDroppedConnection(self):
		...



	def test_performBaitConnection(self):
		...




	def test_isSuccessfulHTTPCode_1xxCode(self):
		...

	def test_isSuccessfulHTTPCode_2xxCode(self):
		...

	def test_isSuccessfulHTTPCode_3xxCode(self):
		...

	def test_isSuccessfulHTTPCode_4xxCode(self):
		...

	def test_isSuccessfulHTTPCode_5xxCode(self):
		...


	## Entrypoint method
	def test_run_behaviour(self):
		...

	def test_run_shutdown(self):
		...
