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
    
    if not os.path.isdir("./content"):
      os.makedirs("./content")
  
  def service(self):
    req = self.connection.recv(65536)
    print("#####################################################################")
    print("받은 HTTP 요청 메시지 :\n" + req.decode('utf-8'))
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
  
  # 파일 입출력 관련 메서드
  def isFile(self, path): # 파일이 있는 지 확인
    return os.path.isfile("./content" + path)
  
  def fileReader(self, path): # 파일에 있는 내용 읽기
    ret = ""
    with open("./content" + path, "r") as f:
      ret = f.read()
    return ret

  def fileWriter(self, path, body): # 파일에다가 쓰기
    with open("./content" + path, "w") as f:
      f.write(body)

  # 이 아래는 요청 method에 따른 업무를 실제로 수행하는 메서드
  def doGet(self,req):
    path = req.path
    if self.isFile(path):
      resp = RespMsg(200, "OK")
      respBody = self.fileReader(path)
      resp.addBody(respBody)
      resp.setHeader("Content-Type", "text/plain")
      resp.setHeader("Content-Length", resp.bodyLength())
      self.send(resp)
    else: 
      self.send404(path) # 파일이 없으므로 404      
  
  def doPost(self,req):
    path = req.path
    if self.isFile(path):
      # 파일이 이미 있는 경우에는 수정
      respBody = self.fileReader(path)
      respBody += req.body
      self.fileWriter(path, respBody) 
      resp = RespMsg(200, "OK")
    else:
      # 파일이 없으면 새로 만들어야함
      respBody = req.body
      self.fileWriter(path, respBody)  
      resp = RespMsg(201, "Created")
    resp.addBody(respBody)
    resp.setHeader("Content-Type", "text/plain")
    resp.setHeader("Content-Length", resp.bodyLength())
    self.send(resp)

  def doPut(self,req):
    path = req.path
    self.fileWriter(path, req.body)
    resp = RespMsg(201, "Created")
    resp.addBody(req.body)
    resp.setHeader("Content-Type", "text/plain")
    resp.setHeader("Content-Length", resp.bodyLength())
    self.send(resp)
    
  def doHead(self,req):
    path = req.path
    if self.isFile(path):
      resp = RespMsg(200, "OK")
      respBody = self.fileReader(path)
      with open("./content" + path,"r") as f:      
        respBody = f.read()
      # HEAD method는 body가 없으니까 탑재 X
      resp.setHeader("Content-Type", "text/plain")
      resp.setHeader("Content-Length", str(len(respBody.encode('utf-8'))))
      self.send(resp)      
    else: 
      self.send404(path)

    
  # 이하는 에러 코드 발신메서드
  def send405(self):
    resp = RespMsg(405, "Method Not Allowed")
    resp.addBody("해당 메서드는 지원하지 않습니다")
    resp.setHeader("Content-Type", "text/plain")
    resp.setHeader("Content-Length", resp.bodyLength())
    self.send(resp)
  
  def send404(self, path):
    resp = RespMsg(404, "Not Found")
    resp.addBody("요청하신 {}가 존재하지 않습니다".format(path))
    resp.setHeader("Content-Type", "text/plain")
    resp.setHeader("Content-Length", resp.bodyLength())
    self.send(resp)
    
  def send400(self):
    resp = RespMsg(400, "Bad Request")
    resp.addBody("요청이 잘못되었습니다")
    resp.setHeader("Content-Type", "text/plain")
    resp.setHeader("Content-Length", resp.bodyLength())
    self.send(resp)
  
  def send500(self):
    resp = RespMsg(500, "Server error")
    resp.addBody("서버 문제로 인해 요청을 수행할 수 없습니다")
    resp.setHeader("Content-Type", "text/plain")
    resp.setHeader("Content-Length", resp.bodyLength())
    self.send(resp)
  
  # 소켓 전송, close
  def send(self, resp):
    print("↓")
    print("보낼 HTTP 응답 message :\n" + resp.getStr())
    self.connection.send(resp.getCode())
  
  def close(self):
    self.socket.close()

if __name__ == "__main__":
  IP = input("INSERT IP\n")
  server = Server(IP, 8080)
  try:
    for _ in range(8):
      server.service()
  except:
    server.close()       
  server.close()