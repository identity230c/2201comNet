class HttpMsg: #헤더랑 바디는 똑같은 구조니까 상속받아서 요청/응답메시지를 생성하도록함
  def __init__(self):
      self.header = {}
      self.body = ""

  def setHeader(self, idx, val): 
    self.header[idx] = val

  def addBody(self, body): 
    self.body += body

  def bodyLength(self):
    return str(len(self.body))

  def getStr(self):
    #head line, body line 생성
    ret = ""
    for idx in self.header:# dict에서 하나씩 꺼내서 헤더로 삽입
      ret += "{}:{}\r\n".format(idx,self.header[idx])
        
    ret += "\r\n\r\n" # head-body 분할
      
    ret += self.body
    return ret
  
  def getCode(self): # http 메시지를 encode해서 내보냄
    return self.getStr().encode('utf-8')


class RespMsg(HttpMsg):
  def __init__(self, sCode, sMsg):
    self.responseLine = "HTTP/1.1 {} {}\r\n".format(sCode, sMsg)
    super().__init__()    
  
  def getStr(self):
    ret = self.responseLine + super().getStr()
    return ret

class ReqMsg(HttpMsg):
  host = "localhost:8080" 
  
  def __init__(self, method, path):
    self.requestLine = "{} {} HTTP/1.1\r\n".format(method.upper(), path)
    super().__init__()
  
  def getStr(self):
    ret = self.requestLine
    ret += "Host:{}\r\n".format(ReqMsg.host)
    ret += super().getStr()
    return ret

class MsgReader:
  def __init__(self, msg):
    self.httpVersion = ""
    self.header = {}
    
    headBodySplit = msg.split("\r\n\r\n") # 헤더와 body를 구분
    self.body = headBodySplit[-1]
  
    startHeadSplit = headBodySplit[0].split("\r\n")
    
    self.splitStartLine(startHeadSplit[0])
    self.splitHeaderLine(startHeadSplit[1:])
  
  def splitStartLine(self, startLine):
    return # 상속받아서 구현 
  
  def splitHeaderLine(self,headerLine):
    for line in headerLine:
      tmp = line.split(":")
      idx, val = tmp[0], "".join(tmp[1:]) # host: "localhost:8080"
      self.header[idx] = val

class ReqMsgReader(MsgReader): # 요청 메시지 해석
  def splitStartLine(self, startLine):
    print(startLine)
    self.method, self.path, self.httpVersion = startLine.split(" ") 

class RespMsgReader(MsgReader): # 응답 메시지 해석
  def splitStartLine(self, startLine):
    tmp = startLine.split(" ")
    print(tmp)
    self.httpVersion, self.sCode, self.sMsg = tmp[0], tmp[1], ''.join(tmp[2:])



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