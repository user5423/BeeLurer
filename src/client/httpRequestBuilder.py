from httpRequest import httpRequest
from authenticationGenerator import authenticationGenerator

from dataclasses import dataclass, field
from typing import Any, ClassVar, Set, Dict
import json

class httpRequestBuilder:
	"""Provides methods to build http request based on defined formats"""
	def __init__(self) -> None:
		self.ag = authenticationGenerator()

	def build(self, httpRequestTemplate: Dict[str, Any], arguments: Dict[str, str]) -> httpRequest:
		"""Creates a `httpRequest` object using an httpRequestTemplate and valid arguments"""
		## First we want to receive the httpRequestFormat json object
		## Then we start on the arguments - we need to check if it adheres to the definition
		httpRequestTemplate = self._variableReplace(httpRequestTemplate, arguments)
		## Then we work on generate the credentials
		httpRequestTemplate = self._authenticationGenerate(httpRequestTemplate)
		## TODO: we need to work on handling derived arguments
		httpRequestTemplate = self._handleDerivedArguments(httpRequestTemplate, arguments)
		## NOTE: Finally, we use the httpRequestTemplate arguments and auth to replace the other structures
		httpRequestTemplate = self._templateReplace(httpRequestTemplate)
		## Once the requestFormat has been filled properly, we can then build the httpRequest
		print(httpRequestTemplate, end="\n\n\n")
		return self._buildHttpRequest(httpRequestTemplate)


	def _variableReplace(self, httpRequestTemplate: Dict[str, Any], arguments: Dict[str, str]) -> Dict[str, Any]:
		## Here we validate the arguments
		templateVariableLen = len(httpRequestTemplate.get('variables', []))
		if len(arguments) != templateVariableLen:
			errorMsg = f"The arguments object was expected to have {templateVariableLen}, but only {len(arguments)} were received"
			# raise IncorrectArgumentSizeException(errorMsg)
			raise Exception(errorMsg)

		for k,v in arguments.items():
			if k in httpRequestTemplate['variables']:
				httpRequestTemplate['variables'][k] = v
			else:
				# raise InvalidArgumentException()
				errorMsg = f"The argument object should not have the '{k}' argument"
				raise Exception(errorMsg)

		return httpRequestTemplate


	def _authenticationGenerate(self, httpRequestTemplate: Dict[str, Any]) -> Dict[str, Any]:
		## NOTE: The only supported authentication method is userpass
		## ==> The plan is to support different authentication types later on
		print(httpRequestTemplate)
		if "userpass" in httpRequestTemplate['authentication']:
			httpRequestTemplate['authentication']['userpass'] = self.ag.generateUserPass()
		else:
			# raise AbsentAuthMethodException()
			raise Exception()

		return httpRequestTemplate


	def _handleDerivedArguments(self, httpRequestTemplate: Dict[str, Any], arguments: Dict[str, str]) -> Dict[str, Any]:
		## TODO: this mostly refers to content-type
		return httpRequestTemplate


	def _templateReplace(self, httpRequestTemplate: Dict[str, Any]) -> Dict[str, Any]:
		arguments = {}
		arguments.update(httpRequestTemplate.pop("variables"))
		arguments.update(httpRequestTemplate["authentication"].pop("userpass"))
		## NOTE: Once we provide more sofisticated authentication methods, this will change
		return self._iterateTemplateReplacement(httpRequestTemplate, arguments)


	def _iterateTemplateReplacement(self, template: Dict[str, Any], arguments: Dict[str, str]) -> None:
		print(arguments)
		for k, v in template.items():
			## If it is a dictionary, then we recurse into it (variables should only be observed in terminal values of a dict)
			if isinstance(v, dict):
				self._iterateTemplateReplacement(v, arguments)
			## if the value is a argument (i.e. starts with $)
			elif isinstance(v, list):
				## Here in case we wish to modify this later on
				pass
			elif isinstance(v, str):
				placeholders = self._getPlaceholderIndices(v)
				if len(placeholders) == 0:
					continue
				
				for positions in placeholders[::-1]:
					start = positions[0]
					end = positions[1]
					parameter = v[start+2:end]
					## check if it was provided (i.e. was it provided as an argument)
					if parameter in arguments:
						template[k] = template[k].replace(f"${{{parameter}}}", arguments[parameter])
					else:
						## We got a placeholder for which no argument was provided
						# raise TemplateArgumentError()
						errorMsg = ""
						raise Exception(f"{k}: {v}")
				## otherwise, we should have a constant value, so we leave it alone
				else: 
					pass
			
		return template

	def _getPlaceholderIndices(self, string):
		## NOTE: This will NOT support indented placeholders
		placeholders = []
		bProtected = False
		for index in range(len(string)):
			if bProtected == False:
				if string[index] == '$' and string[index+1] == '{':
					placeholders.append([index])
					bProtected = True
			else:
				if string[index] == '}':
					if index - placeholders[-1][0] < 3: ## You can't have a placeholder with 3chars ${}
						# raise EmptyPlaceholderException()
						raise Exception()
					else:
						placeholders[-1].append(index)
						bProtected = False
		return placeholders



	def _buildHttpRequest(self, httpRequestTemplate: Dict[str, Any]):
		## TODO: Fix the url and query attribute redundancy
		return httpRequest(
			url=httpRequestTemplate['url'],
			body=httpRequestTemplate['body'],
			method=httpRequestTemplate['method'],
			headers=httpRequestTemplate['headers'],
		)


		## We need to be able to fuzz certain attributes, 
		## --> This means that we require an httpRequestBuilder to easily create http request objects
		## --> Then using a definition, we define what attributes are constant, and which attributes
		## are generated randomly/dynamically

		## The way we need to define the format is as follows

		## We read a config file whose values are either constants or variables that
		## can are dynamically derived from the definitinos

		## There are 4 attributes:
		## 1. Method
		## 2. URL
		## 3. Body
		## 4. Headers
		## 4. Path Queries

		## TODO: In the future, we want to fuzz certain attributes to provide some variance
		## in the requests to make it more difficult for an adversary to blacklist requests

		## NOTE: What is required now, is that we are able to replace certain placeholder parameters
		## in the request with the arguments provided to the httpRequestBuilder class
		## --> This will be defined by the structure of the conf file

def main():
	arguments = {"host": "127.0.0.1"}
	with open("httpRequestFormat.json", "r") as infile:
		template = json.load(infile)

	hrb = httpRequestBuilder()
	req = hrb.build(template, arguments)


if __name__ == "__main__":
	main()