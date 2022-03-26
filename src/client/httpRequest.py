import yarl
import validators
import requests.utils.quote
from typing import Dict, Any, List, ClassVar, Set
from dataclasses import dataclass, field


class InvalidHeaderFormat(Exception):
    def __init__(self):
        super().__init__("Invalid Header Format provided (i.e. no : seperator)")

class UnsupportedHttpMethod(Exception):
    def __init__(self):
        super().__init__("Unsupported HTTP Method")  

class InvalidUrlValue(Exception):
    def __init__(self):
        super().__init__("Invalid URL Value")  


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

    def setBody(self, body: Any, contentType: str) -> None:
        self._body = body
        self._content = contentType


@dataclass
class httpQuery:
    _query: Any = field(init=False, default_factory=dict)

    def setQueries(self, query: Dict[str, str]) -> None:
        for k,v in query.items():
            _query[k] = v
    

@dataclass
class url:
    _url: yarl.URL = field(init=False)

    def setUrl(self, url: str):
        ## We need to encode and then validate, then create a yarl
        if validators.url(url):
            self._url = yarl.URL(url)
        else:
            raise InvalidUrlValue


@dataclass
class httpRequest:
    url: str
    method: str = field(default="GET")
    headers: dict[str,str] = field(default_factory=dict)
    body: Any = field(default_factory=dict)
    query: dict[str,str] = field(default_factory=dict)
    _contentType: str = field(default='application/json')
    _supportedMethods: ClassVar[Set[str]] = {"GET", "POST", "PUT", "DELETE", "PATCH", "UPDATE", "HEAD", "CONNECT", "TRACE", "OPTIONS"}

    def __post_init__(self):
        self.url = self.createUrl(url)
        self.headers = self.createHeaders(self.headers)
        self.body = self.createBody(self.body, self._contentType)
        self.headers.setHeaders({"content-type": self._contentType})
        self.query = self.createQuery(self.query)
    
    def setHttpMethod(self, method: str) -> None:
        if method not in httpRequest._supportedMethods:
            raise UnsupportedHttpMethod
        else:
            self.method = method

    def createUrl(self, url: str) -> None:
        self.url = url().setUrl(url)

    def createBody(self, data: Any, contentType: str) -> None:
        self.body = httpBody().setBody(body, contentType)

    def createHeaders(self, headers: Dict[str, str]) -> None:
        self.headers = httpHeaders().setHeaders(headers)

    def createQuery(self, query: Dict[str, str]) -> None:
        self.query = httpQuery().setQuery(query)


    ## NOTE: After the http request has been fully set, we need to be able to generate
    ## a datastructure to return values
    def getMethod(self):
        return self.method

    ## TODO: This needs to be significantly more robust
    def getUrl(self):
        ## THis needs to get the url from YARL object and the parameters in Query
        querystring = ""
        for k,v in self.query.items():
            querystring += f"{k}={v}"
        return requests.utils.quote(f"{self.url}?{querystring}")

    def getBody(self):
        return self.body

    def getHeaders(self):
        headers = []
        for k,v in self.headers.items():
            headers.append(f"{k}: {v}")
        return headers
