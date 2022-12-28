
from irc_class import *
from botConfig import *

irc = IRC()

def main(): 
    irc.connect()

    while True:
        irc.delayMsgCheck()
        ircmsg = irc.get_response()


        # try: print(ircmsg)
        # except: dontprint = 'okay'     

        if (' TOPIC ' in ircmsg 
            or ' NOTICE ' in ircmsg
            or ' PRIVMSG ' in ircmsg
            ):
            ircMsgSplit = ircmsg.split(' ',3)
            sender = ircMsgSplit[0]
            sendersCmd = ircMsgSplit[1]
            target = ircMsgSplit[2]
            message = ircMsgSplit[3]
            if message.startswith(':'): message = message[1:]

            if 'NOTICE' == sendersCmd or 'PRIVMSG' == sendersCmd:
                # msgType
                if target.startswith('#'):
                    msgType = 'channel'

                elif target == BotNick :
                    msgType = 'dm'



ShutingDown = False
try: 
    main()
    
except KeyboardInterrupt: # Kill Bot from CLI using CTRL+C / SIGINT
    ShutingDown = True
    irc.ircsend(f'QUIT {quitMsg}')
    sys.exit()





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
#   
# ":[Nick]!~[hostname]@[IPAddress] PRIVMSG [channel] :ACTION [message]"  ** Note: \001 ctcp action 
