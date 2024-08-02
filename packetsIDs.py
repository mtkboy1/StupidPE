import socket
import struct
PongTime=0
MAGIC=0x00ffff00fefefefefdfdfdfd12345678
def Pong():
    global PongTime
    Buff=struct.pack("B",0x1c)
    PongTime+=1
    Buff+=struct.pack("!q",PongTime)
    Buff+=struct.pack("!q",0x00000000372cdc9e)
    Buff+=(MAGIC).to_bytes(16, byteorder='big') #MAGIC
    MOTD="MCPE;Dedicated Server;390;0.13.0;0;10;13253860892328930865;Bedrock level;Survival;1;19132;19133;"
    MOTD = MOTD.encode('ascii')
    Buff+=struct.pack("!h",len(MOTD))
    Buff+=MOTD
    #print(Buff)
    return Buff
#ПЕРВЫЙ ЭТАП ПОДКЛЮЧЕНИЯ
def ReplyToConnect1():
    Buff=struct.pack("B",0x06)
    Buff+=(MAGIC).to_bytes(16, byteorder='big') #MAGIC
    Buff+=struct.pack("!q",0x00000000372cdc9e)
    Buff+=struct.pack("?",False)
    Buff+=struct.pack("!h",1447)
    return Buff
#ВТОРОЙ ЭТАП
def ReplyToConnect2(addr):
    Buff=struct.pack("B",0x08)
    Buff+=(MAGIC).to_bytes(16, byteorder='big') #MAGIC
    Buff+=struct.pack("!q",0x00000000372cdc9e)
    hostname_parts: list = addr[0].split('.')
    for i in range(0,len(hostname_parts)):
        Buff+=struct.pack("B",int(hostname_parts[i]))
    Buff+=struct.pack("!h",1447)
    #print(addr[0])
    return Buff
#70 Байтов пакета адрессов
def putDataArray(): #COPY
    Result=[0x00]*7
    BufferedArray = [0xf5,0xff,0xff,0xf5]  # 4 bytes NOT USE
    BufferedArray1 = [0xff,0xff,0xff,0xff]  # 4 bytes NOT USE
    Result[0]=len(BufferedArray)
    Result[1]=0x00
    Result[2]=0x00
    Result[3]=0xf5
    Result[4]=0xff
    Result[5]=0xff
    Result[6]=0xf5
    
    for i in range(0,9):
        Result.append(len(BufferedArray1))
        Result.append(0x00)
        Result.append(0x00)
        Result.append(0xff) #BufferedArray1
        Result.append(0xff)
        Result.append(0xff)
        Result.append(0xff)
    return bytes(Result)
pack=0
def ACK(req):
    global pack
    Buff=struct.pack("B",0xC0)
    Buff+=struct.pack("!h",1)
    Buff+=struct.pack("?",True) #is single?
    Buff+=struct.pack("<I",req[1])
    pack=req[1]
    #print(Buff)
    #Buff=struct.pack("<I",4)
    return Buff
#ИНКАСПСУЛИРУЕМ ПАКЕТ
def EncasulatePack(req):
    global pack
    Buff=struct.pack("B",0x80)
    Buff+=struct.pack("<I",pack)
    Buff+=struct.pack("!h",len(req)*8)
    Buff+=req
    #print(Buff)
    return Buff
#ФИНАЛЬНЫЙ ЭТАП
def ReplyToConnect3(req, addr):
    Buff=struct.pack("B",0x10)
    hostname_parts: list = addr[0].split('.')
    for i in range(0,len(hostname_parts)):
        Buff+=struct.pack("B",int(hostname_parts[i]))
    Buff+=struct.pack("!h",0x00)
    Buff+=putDataArray()
    Buff+=req
    Buff+=struct.pack("B",0x00)
    Buff+=struct.pack("B",0x00)
    Buff+=struct.pack("B",0x00)
    Buff+=struct.pack("B",0x00)
    Buff+=struct.pack("B",0x04)
    Buff+=struct.pack("B",0x44)
    Buff+=struct.pack("B",0x0b)
    Buff+=struct.pack("B",0xa9)
    #print(addr[0])
    return Buff
#PONG IF CONNECTED
def ConnectedPong(req):
    Buff=struct.pack("B",0x03)
    Buff+=req
    Buff+=req
    return Buff
#СЕРВЕР
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.168.0.110', 19132))
while True:
    c, addr = s.recvfrom(65535)
    print('Got connection from', addr)
    req = c
    if req[0]==0x01:
        print("1 req")
        s.sendto(bytes(Pong()), addr)
    if req[0]==0x05:
        print("5 req")
        s.sendto(bytes(ReplyToConnect1()), addr)
    if req[0]==0x07:
        print("7 req")
        s.sendto(bytes(ReplyToConnect2(addr)), addr)
    if req[0]==0x84:
        print("84 req")
        #if req[4]==0x00 and req[8]==0x09:
        s.sendto(bytes(ACK(req)),addr)
        s.sendto(bytes(EncasulatePack(ConnectedPong(req[len(req)-9:len(req)]))), addr)
        #   s.sendto(bytes(EncasulatePack(ReplyToConnect3(req[len(req)-9:len(req)],addr))), addr)
        if req[4]==0x00 and req[10]==0x00:
            s.sendto(bytes(ACK(req)),addr)
        else:
            s.sendto(bytes(ACK(req)),addr)
            s.sendto(bytes(EncasulatePack(ReplyToConnect3(req[len(req)-9:len(req)],addr))), addr)
        #if req[4]==0x60 and req[13]==0x09:
         #   s.sendto(bytes(EncasulatePack(ReplyToConnect3(req[len(req)-9:len(req)],addr))), addr)
    if req[0]!=0x05:
        stroke=""
        byts=""
        for i in range(0,len(req)):
            stroke+=str(req[i] & 0xFF)+","
            byts+=str(req[i])+","
        #print(len(req), " "+stroke)
        print(byts)
        print(req)
