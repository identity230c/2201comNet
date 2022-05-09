from socket import *

from HttpMsg import ReqMsg, RespMsgReader

class Client:
  def __init__(self, ip, port): # 소켓설정
    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.connect((ip, port))
    ReqMsg.host = "{}:{}".format(ip,port)
  
  def request(self, method, path, body=""):
    # 요청메시지를 보내고
    # 응답메시지를 받는다 
    
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

  # PUT 메서드가 제대로 작동하는 지 테스트
  client.request("PUT", "/testPutMethod.txt", "Test Put Method\n") #1 PUT-201
  client.request("PUT", "/testPutMethod.txt", "Test Put Method\n") #2 PUT-201

  # POST가 제대로 작동하는 지 테스트
  client.request("POST", "/testPostMethod.txt", "Test Post Method\n")  #3 POST-201
  client.request("POST", "/testPostMethod.txt", "Test Post Method\n")  #4 POST-200

  # 404 메시지가 제대로 오는지 테스트
  client.request("HEAD", "/test404.txt")  #5  HEAD-404
  client.request("GET", "/test404.txt")   #6  GET-404
  
  # HEAD 메서드의 header 속성이 유효한지 테스트 + GET method 테스트
  client.request("HEAD", "/testPostMethod.txt")   #7  HEAD-200
  client.request("GET", "/testPostMethod.txt")    #8  GET-200
  
  client.close()
  