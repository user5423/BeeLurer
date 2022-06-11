### Proxy Component

#### Introduction

The `proxy` component is used to listen on incoming requests intended for the fake service. There are three main actions performed:
- The request is intercepted
- The request is processed (e.g. by the HoneypotTester)
- The request is then passed to the fake service

The fake services that we would host for now would run using TCP. 
The problem with creating a TCP proxy, is that although we are able to:
- intercept and pass the stream of data
- TCP has no knowledge of higher-level protocols such as HTTP that have built ontop it using specific formats. (e.g. using \n\r\n\r as a seperator between HTTP requests)
- Therefore a TCP proxy would be unable to divide the TCP stream into higher-level protocol requests such as FTP, SMTP, or HTTP

Therefore, you'll VERY likely need to implement a component or integrate functionality that is able to understand each of the  different protocol requests (e.g. HTTP, SMTP, FTP)

NOTE: If you need a bit more of an explanation, ping me, and I'll provide a more in-depth explanation


#### Interface Definition

The interface definitions are considerably more relaxed compared to the `_database` module that Vincent is implementing

This is because the implementation design hasn't been fleshed out, so it is up to you (Kieran and Selorm) to decide how
you want to organize it. 


`class proxy` (required) - You want to implement this as a wrapper depending on if you choose to go the protocol-specific route

- `async startProxy(self, service: str,  port: Optional[int], interface: Optional[str]) -> None`
    - This should be an asynchronous method that receives
        - `service: str` - this should be a string of desired service to run a proxy on (e.g. "http", "ftp", "smtp")
        - `port: Optional[int]` - this should be a integer of the port to run the service on. If it is None, then use a default port (e.g. http=80, https=443, ftp=21, etc...
        - `interface: Optional[str] - this should be a string containing the ip-address we will listen on - e.g. 127.0.0.1, or 0.0.0.0, ...
    - This setups a proxy listener

- `async stopProxy(self, service: str, port: Optional[int], interface: Optional[str]) -> None`
    - This should be an asynchronous method that receives:
        - the same as `proxy.startProxy()`
    - This closes a proxy listener

- `async bindListener(self, service: str, port: Optional[int], interface: Optional[str], handler: Callable) -> None`
   - This should be an async method that receives
       - the same as `proxy.startProxy()`
       - `handler: Callable` this is a method/function that executes asynchronously whenever a specific request is received on that `port&&interface` combination.
   - This should bind a `handler` that receives a request object, and performs some async processing (e.g. testing whether credentials exist in it)
       - An example of this `handler` can be seen below.
    


`class requestTester` (optional depending on design decision)

- `async testRequest(self, protocol: str, request: obj) -> bool:`
    - This should be an async method that receives
        - `protocol: str` - this should be the protocol that is being listened on
        - `request: obj` - this should be the request (as a str, or in bytes), up to you
    - This method should test whether the request is using bait credentials
        - (This uses the `_database` class)
    - If the credentials have been used, then request an email to be sent via the `_email` class
        - (This uses the `_email` class)

The above methods are minimal and are only a guideline. You will need to design how this component works, and will likely need to implement
more methods (including helpers, constructors) as well as object attributes.



#### Potential Solution/Considerations

**Protocol-Specific Proxy**
- You could create a proxy server for each protocol supported (http, smtp, ftp)
- A basic http proxy has been provided in case you want to play around `src/proxy/httpproxy.py`

**Generic TCP Proxy**
- You could create a tcp proxy server, with "handlers" built ontop that is able to read the structured application layer data for each protocol (http, smtp, ftp)
- A basic tcp proxy has been provided in case you want to play around `src/proxy/tcpproxy.py`

NOTE: The proxy is up to you on how to implement (I've given you a starting point, with scripts for each).
- You can actually separate out the proxy into new GH repository (as it works a standalone)
- Let me know if you have any questions

------------------------

** Generic RequestTester** (I recommend this)
- You could create a generic requestTester, that includes application-layer specific handlers for the protocols
- This is so that the `RequestProxyTester` is able to break down the incoming request, and make correct calls to the `_database` module, in order to check whether the request contains credentials, and if so, have they been used in the past.

**Protocol-Specific RequestTester** (I would not recommend this)
- You could create a request specific


NOTE: I would recommend doing the generic requestTester, and then adding protocol support inside this class, as there shouldn't be too much that
differentiates each protocol version of the `requestTester` from each other. However, feel free, to go against this, if you find this suitable



**TODO**:

- Understand the basics of async in python (play around with it)
- Do some reasearch on aiolibs (as they provide easy async servers/clients for a lot of protocols (I built httpproxy.py with aiohttp)

- Once you have done some research, get into the design phase, and come up with a design implementation
- Take a look at pros/cons, and maybe come up with an entirely differently internal design

- Implement the design (and make sure to implement the functionality required by the above interfaces)
- Write tests for the component

