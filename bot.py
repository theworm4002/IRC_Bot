
from irc_class import *
from botConfig import *

irc = IRC()

def main(): 
    irc.connect()

    while True:
        try:
            irc.delayMsgCheck()
            ircmsg = irc.get_response()
            try: print(ircmsg)
            except: dontprint = 'okay'    
                
            # Stuff to help you while coding your IRC bot 
            # ":[server] PING :[message]"
            # ":[server] [numeric] [message]"
            # ":[Nick]!~[hostname]@[IPAddress] AWAY"
            # ":[Nick]!~[hostname]@[IPAddress] PART [channel]"
            # ":[Nick]!~[hostname]@[IPAddress] QUIT :[message]"
            # ":[Nick]!~[hostname]@[IPAddress] JOIN :[channel]"         
            # ":[Nick]!~[hostname]@[IPAddress] INVITE :[channel]"
            # ":[Nick]!~[hostname]@[IPAddress] TOPIC [channel] :[message]"
            # ":[Nick]!~[hostname]@[IPAddress] NOTICE [channel] :[message]"
            # ":[Nick]!~[hostname]@[IPAddress] PRIVMSG [channel] :[message]"
            # ":[Nick]!~[hostname]@[IPAddress] KICK [channel] [user2BeKicked] :[message]"   
            # ":[Nick]!~[hostname]@[IPAddress] PRIVMSG [channel] :ACTION [message]"  ** Note: \001 ctcp action 
            
            # if ircmsg.find('somthing') != -1: 
            #     irc.sendmsg(botChannel, "Hello!")
            # if "PRIVMSG" in text and "hello" in text:
            #     irc.sendmsg(channel, "Hello!")
        except:
            # Should add loggin and better checked before just reconnceting but it is what it is for now
            print('crashed reconnecting')
            irc.connect()
            
try: 
    main()
    
except KeyboardInterrupt: # Kill Bot from CLI using CTRL+C / SIGINT
    irc.ircsend('QUIT {quitMsg}')
    sys.exit()
