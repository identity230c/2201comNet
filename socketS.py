from multiprocessing import connection
from socket import *

def makeResponse(statusCode):
  return "HTTP/1.1 200 OK\r\n\r\n<h1>isBody?</h1>".encode('utf-8')

serverSock = socket(AF_INET, SOCK_STREAM) 
# 소켓 객체 생성. 차례로 IP타입, 소켓타입 스트림이 TCP
serverSock.bind(('', 8081)) # 차례로 :port 앞에껀 잘 모르겠음
serverSock.listen(0) # 접속 대기. 0은 auto 1은 1대만 액세스

connectionSock, addr = serverSock.accept()
# 접속이 있을 때 비로소 작동하는 함수임
# 클라이언트의 소켓, AF 리턴

print(addr, "에서 접속하였음")

msg = connectionSock.recv(1024)
with open("reqPost.txt", "w") as f:
  f.write(msg.decode('utf-8'))
print("서버로 도착한 메시지 = ", msg.decode('utf-8'))
# 1024바이트만큼의 크기를 가진 메시지를 받는다 


connectionSock.send(makeResponse(404))
  
connectionSock.close()
  # 메시지를 보낸다

