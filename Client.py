from socket import *

from HttpMsg import ReqMsg, RespMsgReader

class Client:
  def __init__(self, ip, port):
    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.connect((ip, port))
    ReqMsg.host = "{}:{}".format(ip,port)
  
  def request(self, method, path, body):
    # 요청 메시지 생성
    msgMaker = ReqMsg(method, path)
    msgMaker.addBody(body)
    
    # 요청 메시지 전송
    req = msgMaker.getCode()
    self.socket.send(req)
    
    # 응답 받기
    resp = self.socket.recv(1024)

    # 응답 해석하기
    print("아니시발",len(resp.decode('utf-8')))
    return RespMsgReader(resp.decode('utf-8'))

  def close(self):
    self.socket.close()

if __name__ == "__main__":
  # 서버와 통신 가능한지 확인
  client = Client("127.0.0.1", 8080)
  resp = client.request("PUT", "/testFile.txt", "테스트파일에 입력할 내용")
  resp = client.request("PUT", "/testFile.txt", "테스트파일에 입력할 내용")
  input()
  client.close()
  