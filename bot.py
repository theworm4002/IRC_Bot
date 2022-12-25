
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