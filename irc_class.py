# irc_class

import ssl
import sys
import time
import socket
import datetime
from botConfig import *

class IRC:
 
    irc = socket.socket()
  
    def __init__(self):
        self.lineCount = 0
        self.delayMsgs = [] 
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
        self.BotServer=BotServer
        self.BotPortPre=BotPortPre        
        self.BotRealName=BotRealName
        self.BotNickpass=BotNickpass
        self.BotServerPass=BotServerPass
        self.msgThreshold = msgThreshold
        self.pingThreshold = pingThreshold

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
        if BotServerPass != '':
            self.ircsend(f'PASS {BotServerPass}')            
        self.ircsend(f'USER {BotIdent} * * :{BotRealName}') 
        self.ircsend(f'NICK {BotNick}')                     
        if BotNickpass != '':
            self.ircsend(f'NICKSERV IDENTIFY {BotNickpass}')     
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
        
        # If ircmsg.find("PING") != -1: # Reply to PINGs.
        if ircmsg.startswith('PING :') or (ircmsg.find('PING :') != -1 and ircmsg.lower().find('must') == -1): 
            nospoof = ircmsg.split(' ', 1)[1]
            self.ircsend(f'PONG {nospoof}')
            self.setLastPing()    
            
        # just so it doesned index error for some reason 
        elif len(msgSplit) > 0 : 
            # If nick in use
            if msgSplit[1] == '433':
                self.ircsend(f'NICK {self.BotNick}_') 
                if self.BotNickpass != '':   
                    self.ircsend(f'NICKSERV GHOST {self.BotNick} {self.BotNickpass}') 
                    self.ircsend(f'NICK {self.BotNick}')                     
                    self.ircsend(f'NICKSERV IDENTIFY {self.BotNickpass}')  

        # If last PING was longer than set threshold, try and reconnect.
        elif (time.time() - self.lastPing) >= self.pingThreshold: 
            print('PING was longer than set threshold, reconnecting')
            self.connect()    
        return ircmsg
