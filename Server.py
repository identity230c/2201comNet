from socket import *
import os
from HttpMsg import RespMsg, ReqMsgReader 

class Server:
  acceptMethod = ["GET", "HEAD", "PUT", "POST"]
  def __init__(self, ip, port):
    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.bind((ip,port))
    self.socket.listen(1)
    self.connection, self.addr = self.socket.accept()
  
  def service(self):
    req = self.connection.recv(65536)

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
    except Exception as e:
      print(e)
      self.send500() # 서버에서 오류 발생
  
  def isFile(self, path): # 파일이 있는 지 확인
    print("./content" + path)
    return os.path.isfile("./content" + path)
  
  def fileReader(self, path): # 파일 출력
    ret = ""
    with open("./content" + path, "r") as f:
      ret = f.read()
    return ret

  def fileWriter(self, path, body): # 파일 입력
    with open("./content" + path, "w") as f:
      f.write(body)

  # 서버업무
  def doGet(self,req):
    print("Get")
    path = req.path
    if self.isFile(path):
      resp = RespMsg(200, "OK")
      respBody = self.fileReader(path)
      resp.addBody(respBody)
      resp.setHeader("Content-Type", "text/plain")
      resp.setHeader("Content-Length", resp.bodyLength())
      self.send(resp)
    else: 
      self.send404() # 파일이 없으므로 404      
  
  def doPost(self,req):
    print("Post")
    path = req.path
    if self.isFile(path):
      # 파일이 이미 있는 경우에는 수정
      respBody = self.fileReader(path)
      respBody += req.body
      self.fileWriter(path, respBody) 
      resp = RespMsg(200, "OK")
    else:
      # 파일이 없으면 새로 만들어야함
      respBody = req.body()
      self.fileWriter(path, respBody)  
      resp = RespMsg(201, "Created")
    resp.addBody(respBody)
    resp.setHeader("Content-Type", "text/plain")
    resp.setHeader("Content-Length", resp.bodyLength())
    self.send(resp)

  def doPut(self,req):
    print("Put")
    path = req.path
    self.fileWriter(path, req.body)
    resp = RespMsg(201, "Created")
    resp.addBody(req.body)
    resp.setHeader("Content-Type", "text/plain")
    resp.setHeader("Content-Length", resp.bodyLength())
    self.send(resp)
    
  def doHead(self,req):
    print("Head")
    path = req.path
    if self.isFile(path):
      resp = RespMsg(200, "OK")
      resp = RespMsg(200, "OK")
      respBody = self.fileReader(path)
      with open("./content" + path,"r") as f:      
        respBody = f.read()
      # HEAD method는 body가 없으니까 탑재 X
      resp.setHeader("Content-Type", "text/plain")
      resp.setHeader("Content-Length", str(len(respBody)))
      self.send(resp)      
    else: 
      self.send404()

    
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
    for _ in range(4):
      server.service()
  except:
    server.close()       
  server.close()