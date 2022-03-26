from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class httpHeaders:
    _headers: Dict[str, str] = field(init=False, default_factory=dict)
    
    def setHeader(self, header: str, value: str) -> None:
        self._headers[header] = value

    def setHeaders(self, headerDict: Dict[str, str]) -> None:
        for key, value in headerDict.items():
            self._headers[key] = value

    def removeHeader(self, header: str) -> None:
        try:
            del self._headers[header]
        except KeyError: pass

    def generateHeaderList(self) -> List[str]:
        return [": ".join(header) for header in self._headers]


@dataclass
class httpBody:
    _body: Any = field(init=False)
    _contentType: str = field(init=False)

    def setBody(self, body: Any, contentType: str):
        self._body = body
        self._content = contentType


@dataclass
class httpRequest:
    url: str
    method: str = field(default="GET")
    headers: dict = field(default_factory=dict)
    body: Any = field(default_factory=dict)
    _contentType: str = field(default='application/json')
    _supportedMethods: ClassVar[Set[str]] = {"GET", "POST", "PUT", "DELETE", "PATCH", "UPDATE", "HEAD", "CONNECT", "TRACE", "OPTIONS"}

    def __post_init__(self):
        self.url = self.createUrl(url)
        self.headers = self.createHeaders(self.headers)
        self.body = self.createBody(self.body, self._contentType)
        self.headers.setHeaders({"content-type": self._contentType})
    
    def setHttpMethod(self, method: str) -> None:
        if method not in httpRequest._supportedMethods:
            raise UnsupportedHttpMethod
        else:
            self.method = method

    def createUrl(self, url: str) -> None:
        self.url = yarl.URL(url)

    def createBody(self, data: Any, contentType: str) -> None:
        self.body = httpBody().setBody(body, contentType)

    def createHeaders(self, headers: Dict[str, str]) -> None:
        self.headers = httpHeaders().setHeaders(headers)
