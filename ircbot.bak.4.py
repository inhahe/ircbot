# -*- coding: latin-1 -*-

#this program requires a slightly modified twisted irc.py that returns
#nick!ident@host instead of nick for joins, parts and quits.


#todo: users[nick] instead of users[ih]
#todo: draw rules http://www.chessvariants.com/fidelaws.html
#todo: better timing for reconnect tryings
#todo: chess takebacks?
#todo: a decimal expansion from .base that's too long will quit with flood. and why doesn't anti-flood work there?
#todo: add passwords to servers/networks?
#todo: fingerresponse and versionresponse
#bug: chad did aq and it added mine not his most recent


from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
import time, sys, os.path, re, random, string, StringIO
import pysqlite2.dbapi2 as sql
import twisted.internet.task, WConio
import pythonica2, factor3, math



ircrowwidth = 80
finterval = 1
fwindow = 0
logfilename = "zebot.log"
id = "zebot"
realname = "[][=][]=[][=][]=[][=][]=[][=][]"
quitmessage = '"yields falsehood when appended to its own quotation,"'
fingerresponse = "i do not want to go to the N th power of a matrix: is the number of a man: and a Woman a woman is a Woman. Une Femme est Une femme. A Woman Is a Woman. who is not a good Idea. by the way) is a solid result and weƒ ll be in the way of a Pilgrim, And the Pilgrim Continues HIS Way. Translated By RM French. New York: Harper and Row, Publishers. Inc. New York. NY."
versionresponse = "Python IRC bot by inhahe using Twisted IRC.  Python 2.5/Win XP"
class network: pass
networks = []
#n = network()
#n.name = "freenode"
#n.joins = ["#JesusBot"]
#n.nicks = ["JesusBot"]
#n.hosts = [("irc.freenode.net",6667)]
#n.onconnect = lambda c: c.msg("nickserv", "identify a0a9oeuhu") 
#networks.append(n)
n = network()
n.name = "dalnet"
n.joins = ["#prometheus", "#freethinkers"]
n.joins = ["#freethinkers"]
#n.joins = ["#mytest"]
n.nicks = ["PyBot", "PyBot_", "PyBot__"]
n.hosts = [("irc.dal.net",6667)]
networks += [n]
n = network()
n.name = "undernet"
n.joins = ["#thinkers"]
n.nicks = ["PyBot","PyBot_", "PyBot__"]
n.hosts = [("irc.undernet.org",6667)]
networks += [n]

#n = network()
#n.name="local"
#n.joins = ["test"]
#n.nicks = ["Jesusbot"]
#n.hosts = [("localhost",6667)]
#networks += [n]
#n = network()
#n.name = "efnet"
#n.joins = ["#JesusBot"]
#n.nicks = ["JesusBot"]
#n.hosts = [("irc.efnet.net",6667)]
#networks += [n]
#n = network()
#n.name = "organelle"
#n.joins = ["#organelle"]
#n.hosts = [("irc.organelle.org", 6667)]
#n.nicks = ["JesusBot"]
#networks += [n]

chesscs = [ [0,1,10,10,4,4], [0,1,3,3,13,13], [0,15,12,12,3,3],
            [0,15,12,12,6,6], [0,15,3,3,6,6], [0,15,12,12,4,4],
            [0,15,12,12,6,6], [0,15,12,12,1,1], [0,15,10,10,4,4],
            [0,15,6,6,1,1], [0,15,3,3,1,1], [0,14,4,4,1,1],
            [2,3,11,11,13,13], [2,3,0,0,13,13], 
            [0,8,3,3,1,1], [0,8,4,4,1,1], [10,3,0,0,1,1],
            [10,3,8,8,1,1], [4,1,0,0,12,12], [15,14,4,4,1,1],
            [15,14,12,12,1,1], [15,14,12,12,4,4], [0,14,12,12,1,1],
            [0,14,14,0,1,1], [10,12,0,0,4,4] ]


numerals = string.digits + string.uppercase

def lastseen(conn, target, channel, params):
  query = "select * from lastseen where "
  qparams = []
  if "!" in params[0]:
    nick, identhost = params[0].split("!",1)
    query += "nick like ? and identhost like ? "
    qparams += [nick.replace("*", "%"), identhost.replace("*", "%")]
  else:
    query += "nick = ?"
    qparams += [nick]
  if channel and len(params)>1 and params[1]=="here":
    query += "and channel = ? "
    qparams += [channel]
  if not (len(params)>1 and params[1]!="anywhere"):
    query += "and network = ? "
    qparams += [network]
  cursor.execute(query+" order by time", params)
  s = set()
  results = []
  for result in cursor.fetchall()[::-1]:
    ident = result.split("!")[0]
    domain = result.split(".")[-2:]
    if (ident, domain) not in s:
      results += result
      s.add((ident,domain))
  for result in results[::-1]:
    message = result['nick']+'!'+result["identhost"]+'was lats seen '
    if len(params)>1:
      if params[1]=="anywhere":
        message += 'in '+result['network']+" "+result['channel']
    else:
      message += 'in '+result['channel'] + ' ' 
    now = time.time()
    then = result['time']
    delta = now-then
    days = delta / (60*60*24)
    hours = (delta % (24*3600)) / 3600
    minutes = (delta % 3600) / 60
    seconds = delta % 60
    ml = []
    if days: ml += [str(days)+'days']
    if hours: ml += [str(hours)+'hours']
    if minutes: ml += [str(minutes)+'minutes']
    if seconds: ml += [str(seconds)+'seconds']
    conn.msg(target, message + ', '.join(ml) + ' ago.')

def getanswer(number, frombase, tobase):
  number, fraction = (number+".").split(".",1)
  fraction = fraction.replace(".","")
  result = 0
  answer = ""
  if number:
    value = int(number, frombase)
    scratchvalue = value
    for place in range(math.log(value, tobase),-1,-1):
      answer += numerals[scratchvalue / tobase**place]
      scratchvalue -= scratchvalue / tobase**place * tobase**place
  vinculum=0
  if fraction != "":
    answer += "."
    num = int(fraction, frombase)*tobase
    den = frombase**len(fraction)
    nums = []
    while num>0:
      v = num/den
      if v < tobase:
        answer += numerals[v]
        num = (num-den*v)*tobase
      if num in nums:
        return answer, len(nums)-nums.index(num)
      nums += [num]
    return answer, 0
  return answer, 0

def cmdbase(conn, target, params):
  if len(params)<2:
    conn.msg(target, "Must specify a number and a base to convert to.")
    return
  params[0]=params[0].upper()
  if len(params)==2: params.insert(1, "10")
  try:
    tobase = int(params[2])
    frombase = int(params[1])
    assert 2 <= tobase <= 36 and 2 <= frombase <= 36
  except:
    conn.msg(target, "Bases must be integers between 2 and 36.")
    return
  try:
    map((numerals[:frombase]+".").index, params[0])
  except:
    conn.msg(target, "Valid numerals for base %d are: %s" % (frombase, numerals[:frombase]))
    return
  answer1, vin1 = getanswer(params[0], frombase, 10)
  answer2, vin2 = getanswer(params[0], frombase, tobase)
  middle = " in base %d is " % tobase
  string2 = answer1 + middle + answer2
  if vin1 or vin2:
    string1=("_"*vin1).rjust(len(answer1))+" "*len(middle)+("_"*vin2).rjust(len(answer2))
    conn.msg(target, ''.join(["" + x + "\n" + y +"\n" for (x, y) in zip(re.findall(".{1,100}",string1), re.findall(".{1,100}",string2))]))
  else:
    for x in re.findall(".{1,100}",(answer1+middle+answer2)):
      conn.msg(target, x)


def shutdown():
  print "[Shutting down]"
  db.commit()
  cursor.close()
  db.close()
  for b in botinstances:
    b.quit(quitmessage)

class chanmsg:
  def __init__(self, type=None, text=None, nick=None, ident=None, host=None, time=None,
       nick2=None, server1=None,
       server2=None, userid=None, username=None):
    self.text=text
    self.nick=nick
    self.ident=ident
    self.host=host
    self.time=time
    self.type=type
    self.nick2=nick2
    self.server1=server1
    self.server2=server2
    self.userid=userid
    self.username=username

def cplace(x1,y1,x2=None,y2=None):
  a=chr(ord('a')+x1)+str(8-y1)
  if x2 is not None: a+=chr(ord('a')+x2)+str(8-y2)
  return a

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DictCursor(sql.Cursor):
    def __init__(self, *args, **kwargs):
        sql.Cursor.__init__(self, *args, **kwargs)
        self.row_factory = lambda cur, row: dict_factory(self, row)

class DictConnection(sql.Connection):
    def __init__(self, *args, **kwargs):
        sql.Connection.__init__(self, *args, **kwargs)

    def cursor(self):
        return DictCursor(self)

#[4,1,0,0,8,8], [0,3,12,12,1,1], [10,3,0,0,12,12],[10,3,12,12,1,1], 

chessct = dict(R="#",N=chr(167),B="x",Q="*",K="+",P="i")
chessct["K"] = chr(177)
chessct[" "]=" "
db = sql.connect("zebot.db", factory=DictConnection)
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (userid integer primary key
                  autoincrement,
                  username char(30), password char(30), cchessid int)""")
cursor.execute("""create table if not exists quotes (time datetime,
                  text varchar(500), sbnick varchar(70), sbuserid int,
                  sbident varchar(70), sbhost varchar(70),
                  qbnih varchar(212), qbuserid int, type varchar(10),
                  channel varchar(100), network varchar(50), quoteid integer
                  primary key autoincrement, cchessid int)""")
cursor.execute("""create table if not exists chess (chessid integer primary
                  key autoincrement,
                  wuserid int, buserid int, board char(64), turn int, won int,
                  stalemate int, draw int, forfeit int, moves text,
                  wscolor int, bscolor int, wpwscolor int, wpbscolor int,
                  bpwscolor int, bpbscolor int, wcheck int, bcheck int)""")
cursor.execute("""create table if not exists convo (text varchar(500),
                  sbident varchar(70))""")
cursor.execute("""create table if not exists lastseen (nicklwr varchar(255),
                  nih varchar(255), networklwr varchar(255),
                  channel varchar(255), channellwr varchar(255),
                  time int)""")


class chan:
  backbuffer = []
  users = {}
class usr: pass


def fix(a):
  return a.replace("\\","\\\\").replace("'","\\'")


def clr(piece):
        return [piece==piece.lower(), None][piece==" "]
def pc(piece):
        return piece.upper(), clr(piece)

def checkline(p1x,p1y,p2x,p2y,board):
        dx = (p2x>p1x)*2-1
        dy = (p2y>p1y)*2-1
        if p1x==p2x:
          return not ''.join([board[y*8+p1x] for y in range(p1y+dy, p2y, dy)]).strip()
        elif p1y==p2y:
          return not ''.join([board[p1y*8+x] for x in range(p1x+dx, p2x, dx)]).strip()
        else:
          return not ''.join([board[(p1y+n*dy+dy)*8+p1x+n*dx+dx] for n in range(abs(p2y-p1y)-1)]).strip()

def updateseen(nick, identhost, network, channel):
  cursor.execute("update lastseen set time = ? where nick =? and identhost=? and network=?"
                 " and channel=?", (int(time.time()), nick, identhost, network, channel))
  if cursor.rowcount==0:
    insertdict("lastseen", time=int(time.time()), nick=nick, 
               identhost=identhost, network=network, channel=channel)

#def insertdict(table, **dict):

##  cursor.execute("begin")
#  cursor.execute("insert into %s (%s) values (%s)" % (table,
#   fix(",".join([str(x[0]) for x in dict.items() if not x[1] is None])),
#   ",".join(["'%s'" % fix(str(x)) for x in dict.values() if not x is None])))
##  cursor.execute("end")

def insertdict(table, **dict):
  cursor.execute("insert into %s (%s) values (%s)" % (table,
   ",".join(dict.keys()), ",".join(["?"]*len(dict))), dict.values())

users = {}

def getid(ident, host):
  try: return users[ident+"@"+host].userid
  except: return None
def getuname(ident, host):
  try: return users[ident+"@"+host].username
  except: return None

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
        print message
   
    def close(self):
        self.file.close()


class bot(irc.IRCClient):

    def showboard2(self, nick, params): #debug
      params += ["0"]*(6-len(params))
      board =     ("rnbqkbnr"
                   "pppppppp"
                   "        "
                   "        "
                   "        "
                   "        "
                   "PPPPPPPP"
                   "RNBQKBNR")
      for x in range(8):
        m = str(8-x) + " "
        for y in range(8):
          piece = board[x*8+y]
          bp = piece.lower() == piece
          piece = piece.upper()
          m += chr(3) + params[2+bp*2+(x+y)%2] + "," + params[(x+y)%2] + \
               " " + chessct[piece] + " "
        self.msg(nick, m)
      self.msg(nick, "   a  b  c  d  e  f  g  h ")

    def docommandq(self):
      if self.commandqueue:
        cmd, args = self.commandqueue.pop(0)
        cmd(*args)
        self.lctime = time.time()
      else:
        if self.penalty>0: self.penalty -= 1 

    def __init__(self, *args, **kwargs):
      global botinstances
      botinstances += [self]
      self.channels = {}
      self.commandqueue = []
#      self.cmdtimes = []
      self.penalty = 0
#      self.lctime = None
      self.pmcbonce={}
      self.looper = twisted.internet.task.LoopingCall(self.docommandq)
      self.looper.start(finterval)


    def docommand(self, cmd, *args):

#sliding window method
#      self.cmdtimes = [t for t in self.cmdtimes
#           if not t < time.time()-finterval] + time.time()
#      if len(self.cmdtimes) > 1:

      if self.penalty > fwindow:   
        self.commandqueue += [(cmd, args)]
      else:
        self.penalty += 1
        cmd(*args)
#        self.lctime = time.time()
#        self.looper.stop()
#        self.looper.start(finterval) #todo: synchronize looper with this message

    def msg(self, target, text):
      msgs = text.split("\n")
      for m in msgs:
        self.docommand(self.msg2, target, m)

    def msg2(self, target, text):
        irc.IRCClient.msg(self, target, str(text))
        logger.log("privmsg to <%s> <%s> %s" % (self.net, target, text))

    def userJoined(self, user, channel):

      nick, rest = user.split("!",1)
      ident, host = rest.split("@",1)
      n = nick.lower()
      self.channels[channel.lower()].users[n]=usr()
      self.channels[channel.lower()].users[n].ident = ident
      self.channels[channel.lower()].users[n].host = host
      logger.log("<%s> <%s> joined: %s" % (self.net, channel, user))
      updateseen(nick, rest, self.net, channel)

    def userLeft(self, user, channel):
      nick, ih = user.split("!",1)
      del self.channels[channel.lower()].users[nick.lower()]
      if ih in users:
        if nick not in (x.users for y in self.channels for x in y):
          del users[ih]
      logger.log("<%s> <%s> parted: %s" % (self.net, channel, user))
      updateseen(nick, ih, self.net, channel)
    def userQuit(self, user, message):

      nick, ih = user.split("!",1)
      logger.log("<%s> quit: %s (%s)" % (self.net, user, message))
      if ih in users: del users[ih]
      for ch in self.channels.values():
        if nick.lower() in ch.users: del ch.users[nick.lower()]
      updateseen(nick, ih, self.net, None)

    def userKicked(self, kickee, channel, kicker, message):
      nick, ih = user.split("!",1)
      logger.log("<%s> <%s> %s kicked by %s" %
           (self.net, channel, kickee, kicker))
      if ih in users:
        if nick not in (x.users for y in self.channels for x in y):
          del users[ih]
      updateseen(nick, ih, self.net, channel)

    def userRenamed(self, nih, newname):
      oldname, ih = nih.split("!",1)
      for ch in self.channels.values():
        try:
          ch.users[newname.lower()]=ch.users[oldname.lower()]
          del ch.users[oldname.lower()]
        except: pass
      for x in users.values():
        if x.nick==oldname: x.nick=newname
      updateseen(nick, ih, self.net)

    def irc_RPL_NAMREPLY(self, prefix, params):
      for nick in params[3].split():
        nick = nick.lower()
        if nick[0] not in string.ascii_lowercase+"\|`^_": nick=nick[1:]
        self.channels[params[2].lower()].users[nick.lower()]=usr()
      updateseen(nick, None, self.net, params[2])


    def irc_ERR_NICKNAMEINUSE(self, prefix, params):
      o = self.factory.nickcycle
      self.factory.nickcycle = (self.factory.nickcycle+1) % len(self.factory.network.nicks)
      self.register(self.factory.network.nicks[self.factory.nickcycle])
      logger.log("<%s> [%s nick taken, trying %s]" % \
           (self.factory.network.name, self.factory.network.nicks[o],
           self.factory.network.nicks[self.factory.nickcycle]))
    def connectionMade(self):
        self.net = self.factory.network.name
        irc.IRCClient.connectionMade(self)
        logger.log("[Connected to %s]" % self.net)
        if hasattr(self.factory.network, "onconnect"):
          self.factory.network.onconnect(self)
        
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        logger.log("[Disconnected from %s]" % self.net)

        #todo: loop through all users on network and updateseen



    # callbacks for events
              
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for c in self.factory.network.joins: self.join(c)

    def joined(self, channel):
        logger.log("<%s> [I have joined %s]" % (self.net,channel))    
        self.channels[channel.lower()] = chan()

    def left(self, channel):
      ou = self.channels[channel.lower()].users
      del self.channels[channel.lower()]
      for n in ou:
        if ou[n].ident+"@"+ou[n].nick in users:
          if n not in (x for x in self.channels for y in x.users):
            del users[ou[n].ident+"@"+ou[n].nick]
      logger.log("<%s> [I have left %s]" % (self.net, channel))

    def kicked(self, channel, kicker, message):
      ou = self.channels[channel.lower()].users
      del self.channels[channel.lower()]
      for n in ou:
        if ou[n].ident+"@"+ou[n].nick in users:
          if n not in (x for x in self.channels for y in x.users):
            del users[ou[n].ident+"@"+ou[n].nick]
      logger.log("<%s> I was kicked from %s by %s (%s)" %
           (self.net, channel, kicker, message))

    def noticed(self, user, channel, message):
      try: nick, ih = user.split("!",1)
      except: nick, ih = user, None
      if channel in self.channels:
        logger.log("notice from <%s> <%s> <%s> %s" %
             (self.net, nick, channel, message))
      else:
        logger.log("notice from <%s> %s %s" %
             (self.net, ["","<"+nick+">"][bool(user)], message))
      updateseen(nick, ih, self.net, channel)

    def help(self, target, params):
      if len(params)==0:
        self.msg(target, "Usage: .help [topic]\n"
              "Help topics: accounts, chess, quotes, math, seen")
      elif len(params)==1:
        if params[0].lower()=="chess":
          self.msg(target,
               ".cn or .chessnew [colorscheme] <opponent> <user to play white>\n"
               "Creates a new chess game with the specified color scheme (or"
               " the default color scheme if none specified) against the user"
               " <opponent>.  <user to play white> must be either your"
               " username or your opponent's\n"
               "\n"
               ".csc or .chessshowcolors\n"
               "Shows available chess color schemes\n"
               "\n"
               ".cs or .chessshow [game number]\n"
               "Shows the game of the specified game number.  If"
               " no game number is specified, it shows the last game you "
               " created, viewed or moved in.\n"
               "\n"
               ".cm or .chessmove [gamenumber] <origin square> <destination square>\n"
               "Moves your piece from <origin square> to <destinatio square>.  A square is notated"
               " by its column lettered a-h followed by its row numbered 8-1.\n"
               " if gamenumber is omitted, the last game you created, viewed, or"
               " moved in is assumed.\n"
               "Ex.: .cm e2 e4\n"
               "(moves the king's pawn up two squares)\n"
               "\n"
               ".cl or .chesslist [user1] [user2]\n"
               "If one user is specified, lists all games in which that user"
               " is playing.  If two users are specified, lists all games in"
               " which both users are playing (order independent).  If no users"
               " are specified, lists all games.\n"
               "\n"
               ".cla or .chesslistactive [user1] [user2]\n"
               "Like .cl but lists only active games.\n"
               "\n"
               ".css or .chesssavestate [gamenumber]\n"
               "Saves the current game state to a new board.\n"
               "If no game number is specified, it saves the last game you"
               " created, viewed, or moved in.\n"
               "Will not work on a finished game.\n"
               "--End help--")

        elif params[0].lower()=="math":
          self.msg(target,
          ".calc <expression>\n"
          "Solves <expression>\n"
          "Valid functions are: Sqrt, Root, Exp, Abs, Mod, Round, Sin, Cos, Tan, ASin, ACos, ATan, Rad2Deg, Deg2Rad, and Complex\n"
          "Function parameters are enclosed by square brackets ([]).\n"
          "Valid symbols are: \n"
          "'(', ')'\n"
          "'[', ']'\n"
          "'+', '-', '*', '/'\n"
          "'^', '**' (Exponent)\n"
          "'=' (Set)\n"
          "'=;' (Unset)\n"
          "'==' (Compare)\n"
          "'->' (Rule)\n"
          "'j' (denotes an imaginary number)\n"
          "any arbitrary string of letters and/or numbers starting with a letter (Variable name)\n"
          "Lists are encased in square brackets ([]).\n"
          "A slice is written as                 [[args]] right after an expression and returns the component of the expression described by args. The first arg acts on the expression, the second arg acts on the result of the first, etc. \n"
          "A value of 0 returns a symbol for the head of the expression, a positive integer returns that component of the expression (as if the expression was a 1-based list) and a negative number returns the component that number from the end of the expression.\n"
          "\n"
          ".factor <number>\n"
          "Factors the given number\n"
          "\n"
          ".base <number> [base to convert from] <base to convert to>\n"
          "Converts a number from one base to another base.  Will convert "
          "non-integers.  If [base to convert from] is omitted, base 10 is "
          "assumed.  Bases must be in the range 2-36.\n"
          "--End help--")

        elif params[0].lower()=="quotes":
          self.msg(target,

          ".aq [nick][one or more words]\n"
          "With no parameters, adds the most recent action or message to the"
          " quotes database.\n"
          "With one paramater, adds the most recent action or message whose"
          " sender's nick matches the parameter or whose"
          " text contains the parameter.\n"
          "With two or more parameters, adds the most recent action or message"
          " whose text contains all the parameters given in the same order or"
          " whose sender's nick matches the first parameter"
          " and whose text contains all parameters after the first parameter in"
          "  the same order.\n"
          "\n"
          ".rq [quote id|nick|ident|username|two or more words]\n"
          "With no parameters, retrieves a random quote.\n"
          "With one parameter, retrieves a random quote whose quote id matches"
          " the parameter or whose sender's nick, ident or username matches the"
          " parameter.\n"
          "With 2 or more parameters, retrieves a random quote containing all the"
          " words in the same order.\n"
          "\n"
          ".dq quoteid\n"
          "Deletes the quote with the specified quote id.")

        elif params[0].lower()=="accounts":
          self.msg(target,
          ".login <username> <password>\n"
          "Logs you in with the given username and password.  Can only be done "
          " via a private message.  Will only work if you are in at least one"
          " channel that I am in.\n"
          "\n"
          ".logout\n"
          "Logs you out.\n"
          "\n"
          ".register <username> <password>\n"
          "Creates a new account with the given username and password.  Can"
          " only be done via a private message.\n"
          "--End help--")

        elif params[0].lower()=="seen":
          self.msg(target,
          ".seen <nick|nick!ident@hostmask> [here|anywhere]\n"
          "Tells you when the person named by nick "
          "or nick!ident@hostmask was last seen.  The latter may contain "
          "asterisks (wildcards).  'here' means only in the relevant channel."
          " 'anywhere' means on any network.")
            
        else:
          self.msg(target, "Sorry, I don't have any help on that topic.")
      else:
        self.msg(target, "Usage: .help [topic]")

    def chessnew(self, u, target, params):
      if u is None:
        self.msg(target, "You must be logged in to create a new chess game.")
        return
      cs = None
      if len(params)==3:
        cs = params.pop(0)
      if len(params) != 2:
        self.msg(target, "Usage: .cn [colorscheme] <opponent> <user to play white>\n"
             "(.csc to show available color schemes)")
        return
      cursor.execute("select * from users where lower(username) = '%s'" %
             params[0])
      d = cursor.fetchone()
      if not d:
        self.msg(target, "User %s not found." % params[0])
        return
      if cs:
        try:
          i = int(cs)
          assert 0 < i <= len(chesscs)
        except:
          self.msg(target, "That is not a valid color scheme "
               "index.\n.csc to show available color schemes")
          return
        v = chesscs[i-1]
      else:
        v = [15,14,12,12,4,4]
      if params[1] not in [u.username.lower(), params[0]]:
        self.msg(target, "White must be played by either you or your "
             "opponent.\nUsage: .cn or .chessnew [colorscheme] <opponent> <user to play white>\n"
             "(.csc to list color schemes)") 
        return
      userid2 = d["userid"]
      if params[1] == params[0]: wuserid, buserid = userid2, u.userid
      else: wuserid, buserid = u.userid, userid2

      insertdict('chess', 
           board = ("rnbqkbnr"
                    "pppppppp"
                    "        "
                    "        "
                    "        "
                    "        "
                    "PPPPPPPP"
                    "RNBQKBNR"),
           turn = 0, wuserid=wuserid, wscolor=v[0], buserid=buserid,
           bscolor=v[1],wpwscolor=v[2],wpbscolor=v[3],bpwscolor=v[4],
           bpbscolor=v[5],moves="",wcheck=0,bcheck=0)
      chessid=cursor.lastrowid
      self.msg(target, "Chess game #%s has been created." % chessid)
      self.msg(target, "")
      self.showboard(target, chessid)
      cursor.execute("update users set cchessid='%d' where userid='%d'" %
           (chessid, u.userid))
      cursor.execute("select cchessid from users where username = '%s'" %
            userid2)
      chessid = cursor.fetchone()["cchessid"]
      if chessid is None:
        cursor.execute("update users set cchessid=? where userid=?",
                      (chessid, userid2))

    def showcolors(self, target):
      self.msg(target, "Chess color schemes:")
      for x in range(0, len(chesscs), ircrowwidth/14): #adjust for self nick len
        self.msg(target, "")
        msg = ""
        P = chessct["P"]
        for y, v in enumerate(chesscs[x:x+ircrowwidth/14]):
          msg += '1,0 %2d: %s,%s %s %s,%s %s %s,%s %s ' % (y+x+1, v[5],
               v[1], P, v[4], v[0], P, v[5], v[1], P)
        self.msg(target, msg)
        msg = ""
        for v in chesscs[x:x+ircrowwidth/14]:
          msg += '1,0     0,%s   0,%s   0,%s   ' % (v[0], v[1],  v[0])
        self.msg(target, msg)
        msg = ""
        for v in chesscs[x:x+ircrowwidth/14]:
          msg += '1,0     %s,%s %s %s,%s %s %s,%s %s ' % (v[3],
               v[1], P, v[2], v[0], P, v[3], v[1], P)
        self.msg(target, msg)
      if len(chesscs) % (ircrowwidth/14) == 0:
        self.msg(target, "\nFin.")

    def showboard(self, target, chessid):
      cursor.execute("select * from chess where chessid = '%d'" % chessid)
      d = cursor.fetchone()
      cursor.execute("select username from users where userid='%s'" %
           d["wuserid"])
      wusername=cursor.fetchone()["username"]
      cursor.execute("select username from users where userid='%s'" %
           d["buserid"])
      busername=cursor.fetchone()["username"]
      sc = d["wscolor"], d["bscolor"]
      pc = d["wpwscolor"], d["wpbscolor"], d["bpwscolor"], d["bpbscolor"]
      for x in range(8):
        m = str(8-x) + " "
        for y in range(8):
          piece = d["board"][x*8+y]
          bp = piece.lower() == piece
          piece = piece.upper()
          m += chr(3) + "%d,%d %s " % (pc[bp*2+(x+y)%2], sc[(x+y)%2],
               str(chessct[piece]))
        if x==3: m += "1,0 Game #%d between %s (white) and %s (black)" % \
            (chessid, str(wusername), str(busername))
        if x==4:
          m += "1,0 "
          if not d["won"] is None:
            m += ["White","Black"][d["won"]] + " has won this game"
          elif d["draw"]:
            m += "The game was a draw"
          elif d["forfeit"] is not None:
            m += ["White","Black"][d["forfeit"]] + " has forfeited this game"
          elif d["stalemate"]:
            m += "This game is a stalemate"
          elif d["turn"] is not None:
            m += ["White", "Black"][d["turn"]] + "'s turn to move"
        if x==5:
          if d["wcheck"]:
            m += "1,0 White is in check"
          elif d["bcheck"]:
            m += "1,0 Black is in check"
        self.msg(target, m)
      self.msg(target, "   a  b  c  d  e  f  g  h")

    def showboard3(self, u, target, params):
      usage = ("Usage: .cs [gamenumber]\n"
             "You must be logged in and be in at least one"
             " chess game to omit the game number.")
      if len(params)>1:
        self.msg(target, usage)
        return
      if len(params)==1:
        if params[0][0]=="#": params[0] = params[0][1:]
        try: chessid=int(params[0])
        except:
          self.msg(target, usage)
          return
        cursor.execute("select * from chess where chessid='%d'" % chessid)
        if not cursor.fetchone():
          self.msg(target, "There is no chess game by that number.")
          return
      else:
        if u is None:
          self.msg(target, usage)
          return
        cursor.execute("select cchessid from users where userid='%s'" %
             u.userid)
        chessid = cursor.fetchone()["cchessid"]
        if chessid is None:
          self.msg(target, usage)
          return
      self.showboard(target, chessid)
      if u is not None:
        cursor.execute("update users set cchessid='%d' where userid='%d'" %
             (chessid, u.userid))

    def chesslist(self, u, target, params, unf):
      if len(params)==1:
        cursor.execute("select * from chess, users where (buserid = userid"
             " or wuserid = userid) and lower(username) = '%s'" % params[0])
        d = cursor.fetchall()
        if unf: d = [x for x in d if x["forfeit"] is None and x["won"] is None and
             (not x["stalemate"]) and (not x["draw"])]
        if not d:
          self.msg(target, "No %schess games with %s as a player were found." % (
               ["","active "][unf], params[0]))
      elif len(params)==2:
        cursor.execute("select * from chess where"
             "  (wuserid in"
             "   (select userid from users where lower(username) = '%s')"
             "   and buserid in"
             "    (select userid from users where lower(username) = '%s'))"
             "  or"
             "   (wuserid in"
             "    (select userid from users where lower(username) = '%s')"
             "   and"
             "   buserid in"
             "     (select userid from users where lower(username) = '%s'))" % \
             (params[0], params[1], params[1], params[0]))
        d = cursor.fetchall()
        if unf: d = [x for x in d if x["forfeit"] is None and x["won"] is None and
             (not x["stalemate"]) and (not x["draw"])]
        if not d:
          self.msg(target, "No %schess games between %s and %s were found." % \
               (["","active "][unf], params[0], params[1]))
      elif len(params)==0:
        cursor.execute("select * from chess")
        d = cursor.fetchall()
        if unf: d = [x for x in d if x["forfeit"] is None and x["won"] is None and
             (not x["stalemate"]) and (not x["draw"])]
        if not d:
          self.msg(target, "No %schess games were found." % ["","active "][unf])
      elif len(params)>2:
        self.msg(target, "Usage: .cl [user1 user2]")
        return
      m = ""
      for g in d:
        cursor.execute("select username from users where userid = '%d'" \
             % g["wuserid"])
        wuser = cursor.fetchone()["username"]
        cursor.execute("select username from users where userid = '%d'" \
             % g["buserid"])
        buser = cursor.fetchone()["username"]
        n = "%d: %s vs. %s" % (g["chessid"], wuser, buser)
        if g["stalemate"]:
          n += " (stalemate)"
        elif not g["won"] is None:
          n += " (" + ["white","black"][g["won"]] + " won)"
        elif not g["forfeit"] is None:
          n += " (" + ["white","black"][g["forfeit"]] + " forfeited)"
        elif g["stalemate"]:
          n += " (stalemate)"
        elif g["draw"]:
          n += " (draw)"
        else:
          n += " (%s's turn)" % ["white","black"][g["turn"]]
        if len(m)+len(n)+1 > ircrowwidth:
          self.msg(target, m)
          m = n
        else:
          if m: m += " "
          m += n
      self.msg(target, m)


    def chesscopy(self, u, target, params):
      if not u:
        self.msg(target, "You must be logged in to do that.")
        return
      usage = "Usage: .css [gamenumber]" 
      if len(params)>1:
        self.msg(target, usage)
        return
      elif len(params)==1:
        if params[0][0]=="#":
          params[0]=params[0][1:]
        try:
          chessid = int(params[0])
        except:
          self.msg(target, usage)
          return
        cursor.execute("select * from chess where chessid = '%d'" % chessid)
        g = cursor.fetchone()
        if not g:
          self.msg(target, "Error: That chess game does not exist.")
          return
        if g["wuserid"] != u.userid and g["buserid"] != u.userid:
          self.msg(target, "You can't copy that game because you're not in it.")
          return
      else:
        cursor.execute("select cchessid from users where userid = '%d'"
             % u.userid)
        l = cursor.fetchone()
        if not l:
          self.msg(target, "Please include the gamenumber parameter.")
          return
        chessid = l["cchessid"]
        cursor.execute("select * from chess where chessid = '%d'" % chessid)
        g = cursor.fetchone()
        if not g:
          self.msg(target, "Sorry, the game you were playing has been deleted.")
          return
      if g["stalemate"] or g["won"] is not None or g["forfeit"] is not None or g["draw"]:
        self.msg(target, "Error: Will not copy a finished game.")
        return
      del g["chessid"]
      insertdict("chess",**g)
      self.msg(target, "Chess game #%d has been saved as #%d." % (chessid,
           cursor.lastrowid))


    def domove(self, turn,p1x,p1y,p2x,p2y,recurse,do,b,moves,u=None,chessid=None,wcheck=False,bcheck=False):
        reason = ""
        piece = b[p1y*8+p1x]
        if piece == " ":
          return None, "There is no piece at square %s!" % cplace(p1x,p1y)
        piece, color = pc(piece)

        if color != turn:
          return None, "You can't move that piece because it is not yours."

        if not piece=="N":
          if not checkline(p1x, p1y, p2x, p2y,b):
            return None, "You can't move there."
        if piece=="P":
          b2 = b
          p1x2, p1y2, p2x2, p2y2 = p1x, p1y, p2x, p2y
          if turn:
            b2 = b[::-1]
            p1x2, p1y2, p2x2, p2y2 = 7-p1x, 7-p1y, 7-p2x, 7-p2y
          if p1x2==p2x2:
            if b2[p2x2+p2y2*8]!=" ":
              return None, "You can't move there."
            if p2y2==p1y2-2:
              if p1y2!=6:
                return None, "You can't move there.  Pawns may only move two squares on their first move."
            elif p2y2!=p1y2-1:
              return None, "You can't move there."
          else:
            if not (abs(p2x2-p1x2)==1 and p1y2-p2y2)==1:
              return None, "You can't move there."
            if b2[p2y2*8+p2x2]==" ":
              if moves[-2:]==cplace(
                   p2y+[-1,1][color],p2x,p2y+[1,-1][color],p2x) and \
                   place(p2y+[-1,1][color],p2x) not in moves[:-4]:
                reason="En passant."
                b[(p2y+[1,-1][color])*8+p2x]=" "
              else:
                return None, "You can't move there.  Pawns can only move diagonally when taking a piece."
          if p2y2==0:
            def finishpawn(self, user, channel, msg, chessid=chessid,
                 color=color, p1x=p1x,p1y=p1y,p2x=p2x,p2y=p2y,board=b):
              target = channel in self.channels and channel or user.split("!")[0]
              try: piece=dict(rook="R",knight="N",bishop="B",
                   queen="Q")[msg.lower()]
              except:
                self.msg(target, "Invalid response.")
                return
              board = board[:p1y*8+p1x] + " " + board[p1y*8+p1x+1:]
              board = board[:p2y*8+p2x] + [piece, piece.lower()][color] + \
                   board[p2y*8+p2x+1:]
              self.chessmove2(target, chessid, turn, board, cplace(p1x,p1y,p2x,p2y)+piece, "Promotion.")

            if do:
              self.pmcbonce[u.ident+"@"+u.host]=finishpawn
              return None, "What piece would you like to change your pawn to?  Type rook, knight, bishop or queen."
            else:
              return True, ""
        elif piece=="R":
          if not (p1x==p2x or p1y==p2y):
            return None, "You can't move there.  Rooks can only move straight."
        elif piece=="N":
          if not (abs(p1x-p2x),abs(p1y-p2y)) in ((1,2),(2,1)):
            return None, "You can't move there.  Knights don't move that way."
        elif piece=="B":
          if not abs(p1x-p2x)==abs(p1y-p2y):
            return None, "You can't move there.  Bishops can only move diagonally."
        elif piece=="Q":
          if not (p1x==p2x or p1y==p2y or abs(p1x-p2x)==abs(p1y-p2y)):
            return None, "You can't move there.  Queens can only move straight or diagonally."
        elif piece=="K":
          if p1y==p2y and p2y==[7,0][turn] and abs(p2x-p1x)==2 and p1x==4:
            if cplace(p1y,[0,7][p2x>4]) in moves or \
                 cplace(p1y,4) in moves:
              return None, "You can't move there.  Castling is only allowed when neither the king nor the rook has moved previously in the game."
            if not checkline([0,7][p2x>4], p1y, p1x, p1y, b):
              return None, "You can't move there.  Castling is only allowed when there are no pieces between the king and the rook."

            for px in range(8):
              for py in range(8):
                if domove(not turn,px, py, (p1x+p2x)/2,p2y,True,False,b,moves)[0]:
                  return None, "You can't move there.  Castling is not allowed when the king would pass over an attacked square."
                if domove(not turn,px, py, p1x+p1y,True,False,b,moves)[0]:
                  return None, "You can't move there.  Castling is not allowed when the king is in check."

            b = b[:p1y*8+[0,7][p2x>4]] + " " + b[p1y*8+[0,7][p2x>4]+1:]
            b = b[:p1y*8+[3,5][p2x>4]] + ["R","r"][turn] + b[p1y*8+[3,5][p2x>4]+1:] 
            reason = "Castling."
          else:
            if not abs(p1x-p2x)+abs(p1y-p2y) in (1,2):
              return None, "You can't move there.  Kings aren't that agile."
        if clr(b[p2y*8+p2x])==turn:
          return None, "You can't move there.  One of your pieces is on that square."

        b = b[:p2y*8+p2x] + b[p1y*8+p1x] + b[p2y*8+p2x+1:]
        b = b[:p1y*8+p1x] + " " + b[p1y*8+p1x+1:]

        if recurse:
          kp=b.index(["K","k"][turn])
          for tp1x in range(8):
            for tp1y in range(8):
              if self.domove(not turn, tp1x,tp1y, kp%8,kp/8,False,False,b,
                   cplace(p1x,p1y,p2x,p2y))[0]:
                if ((not turn) and wcheck) or (turn and bcheck):
                  return None, "You can't move there.  Your king is in check."
                else:
                  return None, "You can't move there.  That move would put your king in check."

        return b, reason

    def chessmove2(self, target, chessid, turn, board, move, reason):

      cursor.execute("select * from chess where chessid = '%d'" % chessid)
      d = cursor.fetchone()

      n = [x.nick for x in users.values() if x.userid ==
           [d["wuserid"], d["buserid"]][not turn]]
      if len(n):
        nick = n[0]
        if not (target not in self.channels or \
             nick not in self.channels[target].users):
          nick = None

      if nick: self.msg(nick, "On chess game #d %s made the following move: "
           "%s %s" % (chessid, ["white","black"][turn], move[:2], move[2:]))

      if reason:
        self.msg(target, reason)
        if nick: self.msg(nick, reason)

      kp = board.index(("K","k")[not turn])
      cursor.execute("select * from chess where chessid = '%d'" % chessid)
      d = cursor.fetchone()
      check = False
      try:
        for py in range(8):
          for px in range(8):
            assert not self.domove(turn,px,py,kp%8,kp/8,False,False,board,
                 d["moves"])[0]
      except AssertionError:
        check=True
      if not turn: wcheck, bcheck = d["wcheck"], check
      else: wcheck, bcheck = check, d["bcheck"]

      stalemate=True
      try:
        for p1y in range(8):
          for p1x in range(8):
            for p2x in range(8):
              for p2y in range(8):
                assert not self.domove(not turn, p1x,p1y,p2x,p2y,True,False,board,
                     d["moves"])[0]
      except AssertionError:
        stalemate = False
        bcheck = False
        wcheck = False

      won = None
      if check and stalemate:
        self.msg(target, "Checkmate.  %s wins" % ["White","Black"][turn])
        if nick: self.msg(nick, "Checkmate.  %s wins" % ["White","Black"][turn])
        won=turn
        wcheck, bcheck = False, False
        stalemate = False
      elif check:
        if not d[["bcheck","wcheck"][turn]]: 
          self.msg(target, "Check.")
          if nick: self.msg(nick, "Check.")
      elif stalemate:
        self.msg(target, "Stalemate")
        if nick: self.msg(nick, "Stalemate")

      cursor.execute("""update chess set moves='%s',stalemate='%d',turn='%d',
           board='%s',wcheck='%d',bcheck='%d' where chessid='%d'""" % (
           d["moves"]+move,stalemate,not turn, board, wcheck,bcheck,chessid))
      if won is not None:
        cursor.execute("update chess set won='%d' where chessid='%d'" %
             (won, chessid))

      self.showboard(target, chessid)
      if nick: self.showboard(nick, chessid)


    def chessmove(self, u, target, params):


      usage = "Usage: .cm [game number] <from position> <to position>\n" \
              "Example: .cm 10 e2 e4\n" \
              "You must be logged in and in at least one chess game to omit" \
              " the game number."

      if u is None:
        self.msg(target, "You must be logged in to do that.")
        return
      if len(params)==3:
        if params[0][0]=="#": params[0]=params[0][1:]
        try:
          chessid = int(params[0])
        except:
          self.msg(target, usage)
          return
      elif len(params)==2:
        cursor.execute("select cchessid from users where userid = '%s'" %
              u.userid)
        chessid = cursor.fetchone()["cchessid"]
        if chessid is None:
          self.msg(target, "Please include the gamenumber parameter.")
          return
      else:
        self.msg(target, usage)
        return
      cursor.execute("select * from chess where chessid='%s'" % chessid)
      d = cursor.fetchone()
      if not d:
        if len(params)==2:
          self.msg(target, "Sorry, the game you were playing has been deleted.")
          cursor.execute("update user set cchessid=none where userid='%s'" %
               userid)
          return
        else:
          self.msg(target, "Error: That chess game does not exist.")
          return
      turn = d["turn"]
      if d["draw"]:
        self.msg(target,"This game is a draw.")
        return
      if d["won"] is not None:
        self.msg(target,"This game was won by " + ["white","black"][d["won"]])
        return
      if d["forfeit"] is not None:
        self.msg(target, "This game was forfeited by " +
             ["white","black"][d["forfeit"]])
        return
      if d["stalemate"]:
        self.msg(target, "This game is a stalemate.")
        return
      if [d["wuserid"],d["buserid"]][turn] != u.userid:
        self.msg(target, "It is not your turn.")
        return
      if len(params)==3: del params[0]
      try:
        assert len(params[0])==2 and len(params[1])==2
        p1x = ord(params[0][0].lower()) - ord('a')
        p1y = 8-int(params[0][1])
        assert 0 <= p1x <= 7 and 0 <= p1y <= 7
        p2x = ord(params[1][0].lower()) - ord('a')
        p2y = 8-int(params[1][1])
        assert 0 <= p2x <= 7 and 0 <= p2y <= 7
      except:
        self.msg(target, "You entered an invalid coordinate.\n" + usage)
        return

      board, reason = self.domove(turn,p1x,p1y,p2x,p2y,True,True,
           str(d["board"]),d["moves"], u, chessid,d["wcheck"],d["bcheck"])

      if not board:
        self.msg(target, reason)
        return

      self.chessmove2(target, chessid, turn, board, cplace(p1x, p1y, p2x, p2y), reason)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        try:
          nick, ih = user.split('!', 1)
          ident, host = ih.split("@",1)
        except: ident, host, nick = None, None, user

        updateseen(nick, ih, self.net, channel)

        u = users.get(ih, None)
        if ih in self.pmcbonce:
          self.pmcbonce[ih](self, user, channel, msg)
          del self.pmcbonce[ih]
        try: fw = msg.split()[0].lower()
        except: fw = ""                                         
        if channel.lower() not in self.channels:
          logger.log("privmsg from <%s> %s %s" % (self.net,
               ["","<"+nick+">"][bool(nick)], msg))
          if nick and nick != "NickServ" and nick != "MemoServ":
            if fw in ["aq","rq",".aq",".rq", "dq",".dq"]:
              self.msg(nick,
                   "This command must be used in-channel.")
            elif fw == ".login" or fw == "login":
              params = msg.lower().split()
              if nick not in [x for ch in self.channels.values()
                   for x in ch.users]:
                self.msg(nick, "You must be in a channel I am in to log in.")
              else:
                if len(params) != 3:
                  self.msg(nick, "Usage: .login username password")
                else:
                  cursor.execute("""select * from users
                       where lower(username)='%s'""" % params[1])
                  d = cursor.fetchone()
                  if not d:
                    self.msg(nick, "Username not found.")
                  else:
                    if d["password"].lower()!=params[2]:
                      self.msg(nick, "INVALID PASSWORD")
                    else:
                      users[ident+"@"+host]=usr()
                      users[ident+"@"+host].userid=d["userid"]
                      users[ident+"@"+host].username=d["username"]
                      users[ident+"@"+host].ident = ident
                      users[ident+"@"+host].host = host

                      self.msg(nick, "You are now logged in.")
            elif fw== ".logout" or fw=="logout":
              try:
                del users[ident+"@"+host]
              except:
                self.msg(nick, "Confucius say: You must first log in before you log out.")
                return
              self.msg(nick, "You are now logged out.")
            elif fw== ".calc" or fw=="calc":
              if fw==msg.lower():
                self.msg(nick, "Usage: .calc <mathematical expression>")
              else:  
                try: output = pythonica2.mainLoop(msg.split(' ',1)[1])
                except ValueError, e: self.msg(nick, e)
                except: self.msg(nick, "Error.")
                else: self.msg(nick, output)
            elif fw==".base":
              cmdbase(self,nick, msg.split()[1:])


            elif fw==".factor":
              if fw==msg.lower() or not msg.split(' ',1)[1].isdigit():
                self.msg(nick, "Usage: .factor <some large number>")
              else:
                try: factors = factor3.factor(int(msg.split(' ',1)[1]))
                except ValueError, e: self.msg(nick, str(e))
                else: self.msg(nick, '['+', '.join(str(f) for f in factors)+']' if factors else "That number is prime.")


            elif fw ==".register" or fw=="register":
              params = msg.lower().split()
              if len(params)!=3:
                self.msg(nick, "Usage: .register username password")
              else:
                cursor.execute("select * from users where username = '%s'" %
                     params[1].lower())
                if cursor.fetchall():
                  self.msg(nick, "Sorry, that username is already taken.")
                else:
                  insertdict("users", username=params[1].lower(),
                       password=params[2])
                  if cursor.rowcount==0:
                     self.msg(nick, "There was an error creating your account.")
                  else:
                    self.msg(nick, "Your account has been created.")

            elif fw in [".csc","csc", "chessshowcolors", ".chessshowcolors"]:
              self.showcolors(nick)

            elif fw in [".cn","cn", ".chessnew", "chessnew"]:
              self.chessnew(u, nick, msg.lower().split()[1:])

            elif fw in [".cm","cm", ".chessmove","chessmove"]:
              self.chessmove(u, nick, msg.lower().split()[1:])

            elif fw in ["cs",".cs", ".chessshow","chessshow"]:
              self.showboard3(u, nick, msg.split()[1:])

            elif fw in ["cl",".cl", ".chesslist","chesslist"]:
              self.chesslist(u, nick, msg.split()[1:], False)

            elif fw in ["cla",".cla",".chesslistactive", "chesslistactive"]:
              self.chesslistu(u, nick, msg.split()[1:], True)

            elif fw in ["css",".css",".chesssavestate", "chesssavestate"]:
              self.chesscopy(u, nick, msg.split()[1:])

            elif fw in ["help",".help","!help"]:
              self.help(nick, msg.split()[1:])

            elif fw in ["seen", ".seen"]:
              if msg.lower()==fw:
                self.msg(nick, "Usage: .seen <nick|nick!ident@hostmask> [here|anywhere]")
              else:
                lastseen(self, nick, None, msg.split()[1:])

            elif fw[0]=="." and len(fw)>1 and fw[1] in string.ascii_letters:
              self.msg(nick, chr(199)+"a ne me dit rien.")

            else:
              cursor.execute("""select * from convo where sbident <> '%s'
                   order by random() limit 1""" % ident)
              t = cursor.fetchone()
              if not t:
                self.msg(nick, random.choice(open("2of12_b.txt","r").read().split()))
              else:
                self.msg(nick, t["text"])
              insertdict('convo', text=msg, sbident=ident)

        else:
  
          self.channels[channel.lower()].backbuffer.append(chanmsg(type="msg",
               time=time.time(),
               text=msg, nick=nick, ident=ident, host=host,
               userid=getid(ident, host), username=getuname(ident, host)))
          if len(self.channels[channel.lower()].backbuffer) > 50:
            del self.channels[channel.lower()].backbuffer[0]
          logger.log("privmsg from <%s> <%s> <%s> %s" % (self.net, channel, nick, msg))
          if fw == "aq" or fw==".aq":
            params = msg.lower().split()
            if len(params)==1:
              try:
                   mm=[x for x in self.channels[channel.lower()].backbuffer if x.type in \
                   ["msg","action"]][-2]

              except:
                self.msg(channel, "Sorry, there is nothing to quote.")
                return
            elif len(params)==2:
              for mm in [x for x in self.channels[channel.lower()].backbuffer[-2::-1] if \
                   x.type in ["msg","action"]]:
                if mm.nick.lower()==params[1]  or params[1] in mm.text.lower().split():
                  break
              else:
                self.msg(channel, "No message matching the criterion.")
                return
            else:
              for mm in [x for x in self.channels[channel.lower()].backbuffer[-2::-1] if x.type in ["msg","action"]]:
                if params[1]==mm.ident.lower() or params[1]==mm.nick.lower() \
                    or (mm.username and params[1]==mm.username.lower()):
                  del params[1]
                if len(params)==2:
                  if params[1] in mm.text.lower().split():
                    break
                else:
                  if re.search(".*".join(params[1:]), mm.text.lower()):
                    break
              else:                                                                   
                self.msg(channel, "No message matching the criteria.")
                return
            insertdict('quotes', time=time.time(),
                 text=mm.text, sbnick=mm.nick, sbident=mm.ident,
                 sbhost=mm.host, sbuserid=mm.userid, qbnih=user,
                 qbuserid=getid(ident, host), network=self.net,
                 channel=channel, type=mm.type)
            self.msg(channel, "Quote #%d by %s added." %
                 (cursor.lastrowid, mm.nick))
          elif fw == "rq" or fw==".rq":
            params=msg.lower().split()
            if len(params)==2:
              cursor.execute("""select * from quotes left join users
                   where
                   (quotes.quoteid = '%s' or lower(quotes.sbnick) = '%s' or
                   lower(quotes.sbident) = '%s' or
                   (users.username = '%s' and users.userid = quotes.quoteid))
                   and quotes.network = '%s' and quotes.channel = '%s'
                   and type='msg' or type='action'
                   order by random() limit 1""" % (params[1], params[1],
                   params[1], params[1], self.net, channel))
            elif len(params)>2:
              cursor.execute("""select * from quotes where lower(text) like
                   '%%%s%%' and network = '%s' and channel = '%s' and (type='msg'
                   or type='action') order by random()
                   limit 1""" % ("%".join(params[1:]), self.net, channel))


            elif len(params)==1:
              cursor.execute("""select * from quotes where channel = '%s' and
                   network = '%s' and (type = 'msg' or type='action') order by random()
                   limit 1"""  % (channel, self.net))
              
            d = cursor.fetchall()
            if not d:
              if len(params)==1:
                self.msg(channel, "Sorry, the quotes database is empty.")
              else:
                self.msg(channel,
                   "Sorry, I did not find any quotes matching your criteri%s." \
                   % ["on","a"][len(params)>2])
            else:
              for r in d:
                if r["type"]=="msg":
                  self.msg(channel, "%d: <%s> %s" %
                       (r["quoteid"], r["sbnick"], r["text"]))
                elif r["type"]=="action":
                  self.msg(channel, "%d: * %s %s" %
                        (r["quoteid"], r["sbnick"], r["text"]))
          elif fw=="dq" or fw==".dq":
            try:
              num = msg.split()[1]
              int(num)
            except:
              self.msg(channel, ".dq requires a quote number.")
              return
            cursor.execute("delete from quotes where quoteid='%s'" % num)
            if cursor.rowcount:
              self.msg(channel, "Quote #%d deleted." % num)
            else:
              self.msg(channel, "The specified quote was not found.")
          elif fw==".login":
            self.msg(channel, "Login must be done via private message.")
          elif fw==".logout":
            try:
              del users["ident"+"@"+host]
            except:
              self.msg(nick, "Confucius say: You must first log in before you log out.")
              return
            self.msg(nick, "You are now logged out.")

          elif fw== ".calc" or fw=="calc":
            if fw==msg.lower():
              self.msg(channel, "Usage: .calc <mathematical expression>")
            else:  
              try: output = pythonica2.mainLoop(msg.split(' ',1)[1])
              except ValueError, e: self.msg(channel, e)
              except: self.msg(channel, "Error.")
              else: self.msg(channel, output)

          elif fw==".base":
            cmdbase(self, channel, msg.split()[1:])




          elif fw==".factor":
            if fw==msg.lower() or not msg.split(' ',1)[1].isdigit():
              self.msg(channel, "Usage: .factor <some large number>")
            else:
              try: factors = factor3.factor(int(msg.split(' ',1)[1]))
              except ValueError, e: self.msg(channel, str(e))
              else: self.msg(channel, '['+', '.join(str(f) for f in factors)+']' if factors else "That number is prime.")




          elif fw==".register":
            self.msg(channel, "Registration must be done via private message.")
          elif fw==".csc":
            self.showcolors(channel)
          elif fw==".cn":
            self.chessnew(u, channel, msg.lower().split()[1:])
          elif fw == ".cm":
            self.chessmove(u, channel, msg.lower().split()[1:])
          elif fw == ".cs":
            self.showboard3(u, channel, msg.lower().split()[1:])
          elif fw == ".css":
            self.chesscopy(u, channel, msg.split()[1:])
          elif fw == ".cl":
            self.chesslist(u, channel, msg.lower().split()[1:],False)
          elif fw == ".cla":
            self.chesslist(u, channel, msg.lower().split()[1:],True)
          elif fw in (".help", "!help"):
            self.msg(channel, "%s: I am sending you private messages." % nick)
            self.help(channel, msg.lower().split()[1:])
          elif fw == ".seen":
            if msg.lower()==fw:
              self.msg(channel, "Usage: .seen <nick|nick!ident@hostmask> [here|anywhere]")
            else:
              lastseen(self, channel, channel, msg.split()[1:])
          elif fw == "sb":
            self.showboard2(channel, msg.split()[1:])
           
    def action(self, user, channel, msg):
        #apparently ctcp's don't show ident@host
        #todo: fix so that backbuffer knows the usr, otherwise .rq username won't work for actions
        logger.log("<%s> <%s> * %s %s" % (self.net, channel, user, msg))
        updateseen(user, None, self.net, channel)
        self.channels[channel.lower()].backbuffer.append(chanmsg(type="action",
               time=time.time(), text=msg, nick=user))
        if len(self.channels[channel.lower()].backbuffer) > 50:
          del self.channels[channel.lower()].backbuffer[0]

    def irc_NICK(self, prefix, params):
        old_nick, ih = prefix.split('!', 1)
        new_nick = params[0]
        logger.log("<%s> %s is now known as %s" % (self.net, old_nick, new_nick))
        updateseen(old_nick, ih, self.net, None)
        updateseen(new_nick, ih, self.net, None)




reconnect = True

class LogBotFactory(protocol.ClientFactory):


    def __init__(self, network):
      class blah(bot):
        nickname = network.nicks[0]
        realname = realname
        username = id
        netwrk = network
      self.protocol = blah
      self.network = network

      self.hostcycle = 0
      self.nickcycle = 0

      reactor.connectTCP(*self.network.hosts[0]+(self,))

    def clientConnectionLost(self, connector, reason):
        logger.log("<%s> Connection lost: %s" % (self.network.name, reason))
        if reconnect: connector.connect()

        #todo: updateseen all nicks in all channels


    def clientConnectionFailed(self, connector, reason):
        logger.log("<%s> Connection failed: %s" % (self.network.name, reason))
        self.hostcycle = (self.hostcycle+1) % len(self.network.hosts)
        reactor.connectTCP(*self.network.hosts[self.hostcycle]+(self,)) 


class identd(protocol.Protocol):
    
    def dataReceived(self, data):
        self.transport.write(data.strip() + " : USERID : UNIX : " + id + "\r\n" )

identf = protocol.ServerFactory()
identf.protocol = identd

def getkey():
  global reconnect, botinstances
  if WConio.kbhit():
    key = WConio.getkey()
    if key == "q":
       reconnect = False
       shutdown()
    elif key == "r":
      actualstdout, sys.stdout = sys.stdout, StringIO.StringIO()
      actualstdout.write(">")
      inp = raw_input().split(" ",1)
      if len(inp)==2:
        for bot in botinstances:
          if bot.__class__.netwrk.name.startswith(inp[0]):
            print "Sent message to <%s>" % bot.__class__.netwrk.name
            bot.sendLine(inp[1])
      actualstdout.write(sys.stdout.getvalue())
      sys.stdout = actualstdout

def pings():
  for bot in botinstances:
    bot.docommand(bot.sendLine, "Ping Santa Claus")


if __name__ == '__main__':
   # log.startLogging(sys.stdout)

    botinstances = []
    logger = MessageLogger(open(logfilename, "a"))
    reactor.addSystemEventTrigger('before','shutdown',shutdown)
    try: reactor.listenTCP(113,identf)
    except: print "Could not run identd server."
    clients = map(LogBotFactory, networks)
    call = twisted.internet.task.LoopingCall(getkey)
    call.start(.1)
    call2 = twisted.internet.task.LoopingCall(pings)
    call2.start(10)
    reactor.run()

