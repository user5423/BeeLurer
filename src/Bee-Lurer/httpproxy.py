import yarl
import aiohttp
import asyncio
import logging
import contextlib

from aiohttp import web
from aiohttp.log import web_logger
from aiohttp.client import ClientSession
from aiohttp.web_urldispatcher import UrlDispatcher
from aiohttp.web_middlewares import middleware, _Middleware

from types import TracebackType
from typing import Any, Callable, Iterable, List, Mapping, Sequence, Optional, Type
from dataclasses import dataclass, field


@dataclass
class httpproxyHandler:
    clientSession: Optional[aiohttp.ClientSession]
    responseCallbacks: Sequence[Callable] = field(default_factory=list)
    requestCallbacks: Sequence[Callable] = field(default_factory=list)
    SCHEME: str = field(init=False, default="http")
    PROXYHOST: str = field(default="127.0.0.1")
    PROXYPORT: int = field(default=80)
      
              
    async def __aenter__(self) -> None:
        async with contextlib.AsyncExitStack() as stack:
            await stack.enter_async_context(self.clientSession)
            self._stack = stack.pop_all()


    async def __aexit__(self, exc_type: Optional[Type[BaseException]],
                              exc: Optional[BaseException],
                              traceback: Optional[TracebackType]) -> Optional[bool]:
        await self._stack.aclose()


    async def handler(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        '''The coroutine that accepts a request and performs the neccessary computations to return the result'''
        ##We can then provide the ability to execute callbacks that were loaded into the handler
        await self._executeRequestCallbacks(request)
        ##We take the request and send it via http
        proxyResponse = await self._retrieveProxyResource(request)
        ##We can then provide the ability to execute callbacks that were loaded into the handler
        await self._executeResponseCallbacks(proxyResponse)
        ##Finally return the response
        return self._formatClientResponse(proxyResponse)


    async def _executeResponseCallbacks(self, response: aiohttp.ClientResponse) -> None:
        '''This executes async callback functions that proess the aiohttp.ClientResponse object, (where
        the callbacks were defined on the instantiation of the httpproxyHandler class.'''
        [await callback(response) for callback in self.responseCallbacks]


    async def _executeRequestCallbacks(self, response: aiohttp.web.Request) -> None:
        '''This executes async callback functions that proess the aiohttp.web.Request object, (where
        the callbacks were defined on the instantiation of the httpproxyHandler class.'''
        [await callback(response) for callback in self.requestCallbacks]


    async def _retrieveProxyResource(self, request: aiohttp.web.Request) -> aiohttp.ClientResponse:
        '''Using the aiohttp.web.request object, this asynchronously modifies the request in order
        to forward it to the proxy server and retrieve the resource.'''
        return await self.clientSession.request(method=request._method, url=self._createProxyURL(request._rel_url), headers=request._headers)


    def _createProxyURL(self, rel_url: yarl.URL) -> yarl.URL:
        '''Using the relative url that is contained in the aiohttp.web.request, we build a new URL
        with replaced information including PROXYHOST and PROXYPORT values.'''
        return yarl.URL.build(scheme=self.SCHEME, host=self.PROXYHOST, port=self.PROXYPORT).join(rel_url)
        

    def _formatClientResponse(self, proxyResponse: aiohttp.ClientResponse) -> aiohttp.web.Response:
        '''This converts the clientResponse object (client) to the web.Response object (server) so
        that the return object can be used to return to the client.'''
        return aiohttp.web.Response(
            body = proxyResponse.content,
            status = proxyResponse.status,
            reason = proxyResponse.reason,
            headers = proxyResponse.headers)


class httpproxy(web.Application):
    def __init__(self, logger: logging.Logger = web_logger,
                       router: Optional[UrlDispatcher] = None,
                       middlewares: Iterable[_Middleware] = (),
                       handler_args: Optional[Mapping[str, Any]] = None,
                       client_max_size: int = 1024 ** 2,
                       loop: Optional[asyncio.AbstractEventLoop] = None,
                       debug: Any = ...,  # mypy doesn't support ellipsis
                       clientSession: Optional[aiohttp.ClientSession] = None,
                       httpHandler: Optional[httpproxyHandler] = None
                ) -> None:

        super().__init__(logger=logger, router=router, middlewares=middlewares, handler_args=handler_args,
                         client_max_size=client_max_size, loop=loop, debug=debug)

        self.clientSession = aiohttp.ClientSession() if clientSession == None else clientSession()
        self.handler = httpproxyHandler(self.clientSession) if httpHandler == None else httpHandler(self.clientSession)
        self.router.add_route("*", "/{tail:.*}", self.handler.handler)


def main():
    ##NOTE: If you want to customoize the clientSession or httpproxyHandler, you can use functools.partial on ClientSession. Add all the arguments you want, and pass the return value to the httpproxy()
    ##NOTE: httpproxy is a subclass of aiohttp.web.Application -- therefore all inherited methods should still be available
    aiohttp.web.run_app(httpproxy())
    
if __name__ == "__main__":
    main()


