class HttpMsg: #헤더랑 바디는 똑같은 구조니까 상속받아서 요청/응답메시지를 생성하도록함
  def __init__(self):
      self.header = {}
      self.body = ""

  def setHeader(self, idx, val): 
    # 헤더영역에 들어갈 헤더값 입력받기
    self.header[idx] = val

  def addBody(self, body): 
    # body 영역에 들어갈 내용 입력받기
    self.body += body

  def bodyLength(self):  # content-length 헤더용 바이트 크기 계산함수
    return str(len(self.body.encode('utf-8'))) 
    # wireshark는 content-length를 byte단위로 계산
    # python의 len은 문자의 개수로 계산 
    # encode함수를 적용해야 wireshark에서 제대로 감지가능

  def getStr(self):
    # head line, body line 생성
    ret = ""
    for idx in self.header:# dict에서 하나씩 꺼내서 헤더로 삽입
      ret += "{}:{}\r\n".format(idx,self.header[idx])
        
    ret += "\r\n" # head-body 분할. 
      
    ret += self.body
    return ret
  
  def getCode(self): # http 메시지를 encode해서 내보냄
    return self.getStr().encode('utf-8')


class RespMsg(HttpMsg):
  # 응답메시지 작성을 위해 사용
  # 상속받은 HttpMsg에서 head, body line을 작성하였으니 그거는 super class 호출받아서 해결
  # status line만 직접 작성하는 코드
  
  def __init__(self, sCode, sMsg):
    self.responseLine = "HTTP/1.1 {} {}\r\n".format(sCode, sMsg)
    super().__init__()    
  
  def getStr(self):
    ret = self.responseLine + super().getStr()
    return ret

class ReqMsg(HttpMsg):
  # 응답메시지 작성을 위해 사용
  # 상속받은 HttpMsg에서 head, body line을 작성하였으니 그거는 super class 호출받아서 해결
  # status line만 직접 작성하는 코드
  
  host = "localhost:8080" # host 헤더의 디폴트값
  
  def __init__(self, method, path):
    self.requestLine = "{} {} HTTP/1.1\r\n".format(method.upper(), path)
    super().__init__()
  
  def getStr(self):
    ret = self.requestLine
    ret += "Host:{}\r\n".format(ReqMsg.host) # http/1.1버전은 요청메시지 헤더에 Host가 필수로 있어야함
    ret += super().getStr() # super-class httpMsg에서 작성된 head-body 영역을 받아옴
    return ret

class MsgReader:
  # HTTP 형식으로 작성된 메시지를 분리하고 정보 제공하는 class
  # 요청 메시지와 응답 메시지는 첫 줄을 제외하면 같은 정보를 가지고 있음(head, body)
  # 따라서 super class인 MsgReader는 head, body line만 분석하고 
  # 첫번째 line은 subclass를 통해 분석
  
  def __init__(self, msg):
    self.httpVersion = ""
    self.header = {}
    
    headBodySplit = msg.split("\r\n\r\n") # 헤더와 body를 구분
    
    self.body = headBodySplit[-1]
  
    startHeadSplit = headBodySplit[0].split("\r\n")
    # \r\n을 기준으로 line이 나뉘어지므로
    
    self.splitStartLine(startHeadSplit[0]) # \r\n으로 구분된 첫 줄 = 요청라인 or 응답 라인
    self.splitHeaderLine(startHeadSplit[1:]) # 그 이외의 줄 = 헤더 
  
  def splitStartLine(self, startLine):
    return # 상속받아서 구현. java로 치면 추상메서드같은 기능
  
  def splitHeaderLine(self,headerLine):
    # 헤더라인의 정보를 분할하는 함수
    # 헤더라인은 header-name : header-value의 형식으로 전송된다
    # ':'을 기준으로 문자열을 분할하면 헤더의 이름과 헤더의 값을 분해할 수 있다 
    for line in headerLine:
      tmp = line.split(":")
      idx, val = tmp[0], ":".join(tmp[1:]) 
      # host: "localhost:8080" 
      self.header[idx] = val

  def __str__(self): 
    # 단순 테스트용 출력코드
    ret = "\nHEADER"
    headerFormat = "{}:{}"
    for idx in self.header:
      ret += "\n- " + headerFormat.format(idx, self.header[idx])
    ret += '\nBODY = "'
    ret += self.body +'"'
    return ret

class ReqMsgReader(MsgReader): # 요청 메시지 해석
  def splitStartLine(self, startLine):
    self.method, self.path, self.httpVersion = startLine.split(" ") 
    # GET /path http/1.1
    # 한칸의 공백으로 각 정보가 구분되므로 공백을 기준으로 문자열을 분할

  def __str__(self):
    ret = ""
    ret += "\nMETHOD = " + self.method
    ret += "\nPATH = " + self.path
    ret += "\nHTTP-VERSION = " + self.httpVersion
    return ret + super().__str__()

class RespMsgReader(MsgReader): # 응답 메시지 해석
  def splitStartLine(self, startLine):
    tmp = startLine.split(" ")
    self.httpVersion, self.sCode, self.sMsg = tmp[0], tmp[1], ' '.join(tmp[2:])
    # http/1.1 200 OK
    # 한칸의 공백으로 각 정보가 구분되므로 공백을 기준으로 문자열을 분할

  def __str__(self):
    ret = ""
    ret += "\nHTTP-VERSION = " + self.httpVersion
    ret += "\nSTATUS-CODE = " + self.sCode
    ret += "\nSTATUS-MSG = " + self.sMsg
    return ret + super().__str__()



if __name__ == "__main__":
  # 테스트용 
  req = ReqMsg("get", "/asdf")
  req.addBody("asdf")
  print("--요청메시지--")
  print(req.getStr())
  reqReader = ReqMsgReader(req.getStr())
  print("==요청 메시지 해석==")
  print(reqReader.method, "|",reqReader.path, "|",reqReader.httpVersion)
  print(reqReader.header)
  print(reqReader.body)
  
  resp = RespMsg("404", "not found")
  resp.addBody("asdf")
  print("--응답메시지--")

  print(resp.getStr())
  respReader = RespMsgReader(resp.getStr())
  print("==응답 메시지 해석==")
  print(respReader.httpVersion, "|", respReader.sCode, "|",respReader.sMsg)
  print(respReader.header)
  print(respReader.body)