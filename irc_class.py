# irc_class

import ssl
import sys
import time
import socket
import base64
import datetime
from botConfig import *

class IRC:
 
    irc = socket.socket()
  
    def __init__(self):
        self.lineCount = 0
        self.delayMsgs = [] 
        self.connecting = False 
        self.connectingTime = 0
        self.lastPing = time.time()        
        self.lastMsgTime = time.time()
        self.ircSocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
 

    def ircsend(self, msg):        
        msg=msg.replace('\r',' ')
        # Simple catch for flooding (not fully tested. not done yet, for big lines this will need more work)
        # Can send if msg new more then 2sec after last one.
        if (time.time() - self.lastMsgTime) >= self.msgThreshold:
            self.lineCount = 1
            self.lastMsgTime = time.time()
            self.ircSocket.send(bytes(f'{msg} \r\n', 'UTF-8')) 
            print(f'Sending: {msg}')            
        else: # if last msg was sent under 2sec ago
            if self.lineCount >= 9:
                self.delayMsgs.append(msg)
            else:
                self.lineCount += 1
                self.lastMsgTime = time.time()
                self.ircSocket.send(bytes(f'{msg} \r\n', 'UTF-8'))
                print(f'Sending: {msg}')


    def delayMsgCheck(self):
        if self.delayMsgs != []:
            if (time.time() - self.lastMsgTime) >= self.msgThreshold:
                self.lineCount = 0
                delayMsgs = self.delayMsgs
                self.delayMsgs = []
                for line in delayMsgs:
                        self.ircsend(line)
                

    def sendmsg(self, target, msg): # Sends messages to the target.
        # Catch to make sure line is not too long
        # Msg to server can be 512 char, im not checking the full msg I.E "PRIVMSG target", so im making smaller chuncks
        n = 350
        lineChunks = [msg[i:i+n] for i in range(0, len(msg), n)]
        for msg in lineChunks:        
            self.ircsend(f'PRIVMSG {target} {msg}')  


    def setLastPing(self):
        self.lastPing = time.time()
        # Write watchdog file
        with open(f'/tmp/IRC.wtc', 'a+') as fp:
            timeStamp = datetime.datetime.now() + datetime.timedelta(minutes=5)
            timeStamp = timeStamp.strftime('%H%M')
            fp.seek(0) 
            fp.truncate()
            fp.write(str(timeStamp)) 
        return
 

    def connect(self):
        # Connect to the server        
        self.BotNick=BotNick
        self.BotIdent=BotIdent
        self.NickServ=NickServ
        self.BotServer=BotServer
        self.BotPortPre=BotPortPre        
        self.BotRealName=BotRealName
        self.BotNickpass=BotNickpass
        self.msgThreshold=msgThreshold
        self.pingThreshold=pingThreshold
        self.BotServerPass=BotServerPass

        print("Connecting to: " + BotServer)
        try:
            #self.ircSocket.shutdown(socket.SHUT_WR)
            self.ircSocket.close()
            self.ircSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        except :
            self.ircSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        if str(BotPortPre)[:1] == '+':
            self.ircSocket = ssl.wrap_socket(self.ircSocket)
            BotPort = int(BotPortPre[1:])
        else:
            BotPort = int(BotPortPre)
        self.ircSocket.settimeout(self.pingThreshold+2)
        self.ircSocket.connect_ex((BotServer, BotPort))  
        if BotNickpass != '':  
            self.ircsend('CAP REQ :sasl')             
            self.ircsend('AUTHENTICATE PLAIN') 
            self.connecting = True  
            self.connectingTime = time.time()+5             
            
        elif BotServerPass != '':
                self.ircsend(f'PASS {BotServerPass}')            
        self.ircsend(f'USER {BotIdent} * * :{BotRealName}') 
        self.ircsend(f'NICK {BotNick}')      
        self.setLastPing()
 

    def get_response(self):
        # Get the response
        try: text = self.ircSocket.recv(4096)
        except: text = self.ircSocket.recv(2048)        
        try: ircmsg = text.decode('utf-8')
        except UnicodeDecodeError:     
            try: ircmsg = text.decode('iso-8859-15')
            except UnicodeDecodeError: 
                #should realy only be the first 2 but why not
                try: ircmsg = text.decode('latin1')
                except UnicodeDecodeError:             
                    ircmsg = text.decode('cp1252')		         
        ircmsg = ircmsg.strip('\n\r')
        msgSplit = ircmsg.split(' ',2)

        try: 
            print(ircmsg)
            print(msgSplit[1])
        except: dontprint = 'okay' 
        
        # If ircmsg.find("PING") != -1: # Reply to PINGs.
        if ircmsg.startswith('PING :') or (ircmsg.find('PING :') != -1 and ircmsg.lower().find('must') == -1): 
            nospoof = ircmsg.split('ING :', 1)[1]
            if nospoof.find(' ') != -1: nospoof = nospoof.split()[0]
            self.ircsend(f'PONG :{nospoof}')
            self.setLastPing()    
            
        # Try to use SASL to Auth to network else Identify to NickServ     
        if self.connecting:
            if self.connectingTime > time.time():
                print(f'{self.connectingTime} > {time.time()}')
                if ircmsg.find('AUTHENTICATE +') != -1:
                    authPass = f'{self.BotNick}\x00{self.BotNick}\x00{self.BotNickpass}'
                    ap_encoded = str(base64.b64encode(authPass.encode("UTF-8")), "UTF-8")
                    self.ircsend(f'AUTHENTICATE {ap_encoded}') 
                elif (len(msgSplit) >= 2 and msgSplit[1] == '903'
                  or ircmsg.find('SASL authentication successful') != -1
                  ):
                    self.connecting = False
                    self.ircsend('CAP END') 
                elif (len(msgSplit) >= 2 and msgSplit[1] == '904'
                  or ircmsg.find(':SASL authentication failed') != -1
                  ):
                    self.connecting = False
                    self.ircsend('CAP END') 
                    self.ircsend(f'{self.NickServ} IDENTIFY {BotNickpass}') 
            else:
                self.connecting = False
                self.ircsend('CAP END')
                self.ircsend(f'{self.NickServ} IDENTIFY {BotNickpass}') 

        # just so it doesned index error for some reason 
        elif len(msgSplit) >= 2 : 
            # If nick in use
            if msgSplit[1] == '433':
                self.ircsend(f'NICK {self.BotNick}_') 
                if self.BotNickpass != '':   
                    self.sendmsg(self.NickServ, f'GHOST {self.BotNick} {self.BotNickpass}') 
                    self.ircsend(f'NICK {self.BotNick}')                     
                    self.sendmsg(self.NickServ, f'IDENTIFY {self.BotNickpass}')  

        # If last PING was longer than set threshold, try and reconnect.
        elif (time.time() - self.lastPing) >= self.pingThreshold: 
            print('PING was longer than set threshold, reconnecting')
            self.connect()    
        return ircmsg


# ERROR :Closing Link:
