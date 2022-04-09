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
	def test_setQueries_settingNew(self):
		...

	def test_setQueries_overwriting(self):
		...

	def test_removeQuery_nonQuery(self):
		...

	def test_removeQuery_existingQuery(self):
		...


class test_url:
	def test_setUrl_settingNew(self):
		...

	def test_setUrl_overwriting(self):
		...

	def test_setUrl_invalidUrlFormat(self):
		...


class test_httpRequest:
	## NOTE: HTTP Url setting
	def test_init_createUrl_settingNew(self):
		...

	def test_init_createUrl_invalidUrlFormat(self):
		...

	
	## NOTE: HTTP Method setting
	def test_init_setHttpMethod_unsupportedMethod(self):
		...

	def test_init_setHttpMethod_invalidMethod(self):
		...

	def test_init_setHttpMethod_supportedMethod(self):
		...


	## NOTE: HTTP Header setting
	def test_init_createHeaders_settingNew(self):
		...


	## NOTE: HTTP Body setting
	def test_init_createBody_settingNew(self):
		...

	def test_init_createBody_mismatchingType(self):
		...


	## NOTE: HTTP Query setting
	def test_init_createQuery_settingNew(self):
		...


	## NOTE: Auth setting
	def test_init_setAuth_settingNew(self):
		...

	def test_init_setAuth_unsupportedType(self):
		...

	def test_init_setAuth_invalidType(self):
		...

	## NOTE: Testing redundancy mismatches
	def test_init_contentTypeMismatch(self):
		...


class test_httpRequestBuilder:
	...