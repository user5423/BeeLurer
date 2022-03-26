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
