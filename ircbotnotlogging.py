# twisted imports
from twisted.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys

class network: pass
class channel: pass
id = "zebot"
realname = "[][=][]=[][=][]=[][=][]=[][=]"
networks = []
n = network()
n.name = "freenode"
n.joins = ["#test"]
n.nicks = ["zebot", "zebot_"]
n.hosts = [("irc.freenode.net",6667)]
networks.append(n)
n = network()
n.name = "dalnet"
n.joins = ["#freethinkers"]
n.nicks = ["JesusBot","JesusBot_"]
n.hosts = [("irc.dal.net",6667)]
networks.append(n)

class MessageLogger:
    """
    An independant logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class bot(irc.IRCClient):

    def irc_ERR_NICKNAMEINUSE(self, prefix, params):
      self.factory.nickcycle = (self.factory.nickcycle+1) % len(self.factory.network.nicks)
      self.register(self.factory.network.nicks[self.factory.nickcycle])

    def connectionMade(self):
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        irc.IRCClient.connectionMade(self)
        self.logger.log("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))


    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()

    # callbacks for events
              
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for c in self.factory.network.joins: self.join(c)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        
        # Check to see if they're sending me a private message

        # Otherwise check to see if it is a message directed at me

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))


class LogBotFactory(protocol.ClientFactory):


    def __init__(self, network):
      self.protocol = bot
      self.protocol.nickname = network.nicks[0]
      
      self.network = network
      self.hostcycle = 0
      self.nickcycle = 0
      self.filename = "zebot.log"

      reactor.connectTCP(*self.network.hosts[0]+(self,))

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        self.hostcycle = (self.hostcycle+1) % len(self.network.hosts)
        reactor.connectTCP(*self.network.hosts[self.hostyccle]+(self,)) 
        #reactor.stop()

class identd(protocol.Protocol):
    
    def dataReceived(self, data):
        self.transport.write(data.strip() + " : USERID : UNIX : " + id + "\r\n" )

identf = protocol.ServerFactory()
identf.protocol = identd

if __name__ == '__main__':
    log.startLogging(sys.stdout)

    try: reactor.listenTCP(113,identf)
    except: print "could not run ident server"
    
    clients = []
    for n in networks: clients.append(LogBotFactory(n))

    reactor.run()
