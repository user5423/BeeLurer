## Custom exceptions provided to client-side code


#### These are Tor related exceptions

class TorProcessCreationException(OSError):
	def __init__(self) -> None:
		super().__init__("The Tor Process was unsuccessfully created")


class TorProcessShutdownException(OSError):
	def __init__(self) -> None:
		super().__init__("The Tor Process was unsuccessfully shutdown")


class TorControllerCreationException(Exception):
	def __init__(self) -> None:
		super().__init__("The Tor Controller object was unsuccessfully created")

class TorControllerShutdownException(Exception):
	def __init__(self) -> None:
		super().__init__("The Tor Controller object was unsuccessfully shutdown")
			 



#### These are HTTP Request related exceptions

class InvalidHeaderFormat(Exception):
	def __init__(self):
		super().__init__("Invalid Header Format provided (i.e. no : seperator)")

class UnsupportedHttpMethod(Exception):
	def __init__(self):
		super().__init__("Unsupported HTTP Method")  

class InvalidUrlValue(Exception):
	def __init__(self):
		super().__init__("Invalid URL Value")  



#### These are HTTP Request Building related exceptions

class InvalidArgumentException(Exception):
	def __init__(self, msg):
		self.msg = msg
		super().__init__(msg)

class AbsentAuthMethodException(Exception):
	def __init__(self, msg):
		self.msg = msg
		super().__init__(msg)

class IncorrectArgumentSizeException(Exception):
	def __init__(self, msg):
		self.msg = msg
		super().__init__(msg)

class EmptyPlaceholderException(Exception):
	def __init__(self, msg):
		self.msg = msg
		super().__init__(msg)


#### These are Bait Connector related exceptions (higher-level ones that are caught and reraised)

class TemplateFailureException(Exception):
	def __init__(self) -> None:
		self.msg = "The connection template has failed to be instantiated"
		super().__init__(self.msg)

class ConnectionFailureException(Exception):
	def __init__(self) -> None:
		self.msg = "The connection has been failed to be performed properly"
		super().__init__(self.msg)

		