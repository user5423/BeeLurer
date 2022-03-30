## Custom exceptions provided to client-side code

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
             


        