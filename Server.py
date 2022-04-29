from socket import *

from grpc import server
from HttpMsg import RespMsg, ReqMsgReader 

class Server:
  acceptMethod = ["GET", "HEAD", "PUT", "POST"]
  def __init__(self, ip, port):
    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.bind((ip,port))
    self.socket.listen(1)
    self.connection, self.addr = self.socket.accept()
  
  def service(self):
    req = self.connection.recv(1024)

    try: 
      req = ReqMsgReader(req.decode("utf-8"))
    except: # 메시지 해석이 안되면 클라이언트가 요청을 잘못보낸 것으로 간주
      self.send400()
      return 
    try: 
      
      if not req.method in Server.acceptMethod:
        self.send405() # get, head, put, post만 허용. 이외에는 405
        return 
      if req.method == "GET":
        self.doGet(req)
      if req.method == "HEAD":
        self.doHead(req)
      if req.method == "PUT":
        self.doPut(req)
      if req.method == "POST":
        self.doPost(req)
    except:
      self.send500() # 서버에서 오류 발생
  
  # 서버업무
  def doGet(self,req):
    print("Get")
  def doPost(self,req):
    print("Post")
  def doPut(self,req):
    print("Put")
  def doHead(self,req):
    print("Head")
    
  # 이하는 에러 코드 발신메서드
  def send405(self):
    print("405")
    resp = RespMsg(405, "Method Not Allowed")
    self.send(resp)
  def send404(self):
    print("404")
    resp = RespMsg(404, "Not Found")
    self.send(resp)
  def send400(self):
    print("400")
    resp = RespMsg(400, "Bad Request")
    self.send(resp)
  def send500(self):
    print("500")
    resp = RespMsg(500, "Server error")
    self.send(resp)
  
  # 소켓 전송, close
  def send(self, resp):
    print(resp.getStr())
    self.connection.send(resp.getCode())
  
  def close(self):
    self.socket.close()

class ZeroSocketError(Exception):
  def __init__(self) :
    super.__init__("클라이언트와의 연결이 끊어졌습니다")
    pass

if __name__ == "__main__":
  server = Server("127.0.0.1", 8080)
  try:
    for _ in range(5):
      server.service()
  except:
    server.close()       
  server.close()