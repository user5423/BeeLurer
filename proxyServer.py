import socket
import threading
import socketserver


##TODO: Accomodate large post requestse that are greater than 1024 bytes


class proxyReqHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.callback = lambda data: None
        ##We create a new connection with the http server on the local machine
        self.setupLocalProxyConnection()

    def setTCPStreamCallback(self, callback):
        self.callback = callback
        return

    def setupLocalProxyConnection(self):
        self.proxyConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxyConn.settimeout(0.5)
        self.proxyConn.connect(("127.0.0.1", 80))


    def handle(self):
        ##We get the data from the user's request
        ##TODO: Consider using a HTTP parser to get port number address and other relevant information
        self.data = self.request.recv(1024).strip().replace(b"127.0.0.1:9999", b"127.0.0.1:80")

        ##For some reason, when performing curl to localhost:80, we are missing the termination sequence of chars for a http request
        self.data += b'\r\n\r\n'
        ## We then pass the data to the proxyConn that we setup
        retVal = self.proxyConn.sendall(self.data)

        ##TODO: We need to recv in a way that we hold data in variable, and remove parts of it once we have found a finished request
        proxyData = self.proxyConn.recv(1024).strip()
        
        ##NOTE: This function will be called on streams of data segmented into blocks of up to 1024 bytes.
        ##If the http request spans two blocks, or there is two http requests in a block, then the callback
        ##won't be able to handle individual http requests
        self.callback(proxyData)

        ##TODO: There shouldn't be an issue about having multiple protocols used on the same socket connection, unless an adversary
        ##is actively attempting to force it

        self.request.sendall(proxyData)


    def finish(self):
        self.proxyConn.close()



def main():
    HOST, PORT = "127.0.0.1", 9999
    with socketserver.ThreadingTCPServer((HOST, PORT), proxyReqHandler) as s:
        s.serve_forever()





if __name__ == "__main__":
    main()