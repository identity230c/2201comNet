from socket import *

from HttpMsg import ReqMsg, RespMsgReader

class Client:
  def __init__(self, ip, port):
    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.connect((ip, port))
    ReqMsg.host = "{}:{}".format(ip,port)
  
  def request(self, method, path, body=""):
    print("#####################################################################")
    # 요청 메시지 생성
    msgMaker = ReqMsg(method, path)
    if body:
      msgMaker.addBody(body)
      msgMaker.setHeader("Content-Type", "text/plain")  
      msgMaker.setHeader("Content-Length", msgMaker.bodyLength())
    # 요청 메시지 전송
    req = msgMaker.getCode()
    print("보낸 HTTP 요청 메시지 :\n" + msgMaker.getStr())
    self.socket.send(req)
    
    # 응답 받기
    resp = self.socket.recv(65536)

    # 응답 해석하기
    print("↓")
    print("받은 HTTP 응답 메시지 :\n" + resp.decode('utf-8'))

  def close(self):
    self.socket.close()

if __name__ == "__main__":
  # 서버와 통신 가능한지 확인
  IP = input("INSERT HOST IP\n")
  client = Client(IP, 8080)
  client.request("PUT", "/testFile.txt", "PUT")
  client.request("GET", "/What.txt")
  client.request("POST", "/testFile.txt", "POST")
  client.request("HEAD", "/testFile.txt")
  client.close()
  