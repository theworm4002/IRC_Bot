
from irc_class import *
from botConfig import *

irc = IRC()


def main():
    irc.connect(BotServer, BotPortPre, BotNick, BotIdent, BotRealName, BotNickpass, BotServerPass)

    while True:
        irc.delayMsgCheck()
        ircmsg = irc.get_response()
        try: print(ircmsg)
        except: dontprint = 'okay'      
        
        # if ircmsg.find('somthing') != -1: 
        #     irc.sendmsg(botChannel, "Hello!")
        # if "PRIVMSG" in text and "hello" in text:
        #     irc.sendmsg(channel, "Hello!")


try: 
    main()
    
except KeyboardInterrupt: # Kill Bot from CLI using CTRL+C / SIGINT
    irc.ircsend('QUIT {quitMsg}')
    sys.exit()