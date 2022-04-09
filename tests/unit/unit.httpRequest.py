import sys
import pytest
sys.path.insert(0, "src/client/")

from httpRequest import httpAuthGen, httpHeaders, httpBody, \
						httpQuery, url, httpRequest, httpRequestBuilder



class test_httpAuthGen:
	...

class test_httpHeaders:
	def test_setHeader_noHeaders(self):
		...

	def test_setHeader_someHeaders(self):
		...

	def test_setHeader_existingHeader(self):
		...

	def test_setHeaders_noHeaders(self):
		...

	def test_setHeaders_someHeaders(self):
		...

	def test_setHeaders_existingHeaders(self):
		...

	def test_removeHeader_noHeaders(self):
		...

	def test_removeHeader_someHeaders(self):
		...

	def test_removeHeader_existingHeader(self):
		...

	def test_generateHeaderList_noHeaders(self):
		...

	def test_generateHeaderList_someHeaders(self):
		...

class test_httpBody:
	def test_setBody_settingNew(self):
		...

	def test_setBody_overwriting(self):
		...

	def test_setBody_mismatchingType(self):
		...


class test_httpQuery:
	...

class test_url:
	...





class test_httpRequest:
	...

class test_httpRequestBuilder:
	...