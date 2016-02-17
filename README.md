This is an IRC bot I wrote in about 2006 for Python 2.x using Twisted.

It may or may not rely on custom modifications I had made to t.w.p.IRC which aren't included in this repository. Those possible modifications may or may not be the same as the ones made to irc.py that is included in my qtpyrc and qttmwirc repositories.

The bot isn't really meant to contend with the popular bots that are out there, it doesn't have features most would probably desire like ban lists and such, it just has a few features I personally wanted for a channel or two, such as chess (I think it actually implements every single rule of chess, and it supports 25 different color schemes) and saving/retrieving user quotes.

There are 13 different versions of the file, due to having made backups when modifying the program and to having made backups in different places at different times and then having retrieved them all at once, not knowing which ones completely supercede which other ones or may have been useful branches, etc. I honestly don't know which file is the best version of the program, you could diff them and in some cases the differences are probably minor enough to easily determine what's going on. 

A couple of them, ircbot_2.py and ircbot (3).py, have references to the weakref module which I had used before I figured out a better way of keeping references to connections across multiple networks, so these may be inferior/older versions of the file; the only problem is they're both over 1k larger than any of the other files, which would suggest that they were made later, along with the fact they have later timestamps, except for one (ircbot.chess.arlenfix.py), so it's possible that before ircbot_2.py and ircbot (3).py I simply hadn't even implemented the possibility for multiple network connections to access each other, and that my later revisions allowing this access without the need for weakref were completely lost. I have no idea. You'd have to examine the code.

ircbot.chess.arlenfix.py may or may not be a modification that I don't remember making to make the command interface for playing chess--or maybe just the help for it--simpler, for my friend arlen. I remember he had never wanted to play chess on my bot because he found the commands too complicated (they were needlessly complicated just in order to provide maximum flexibility in briefly or verbosely composing chess commands.)

ircbot imports a home-made module, factor3.py, for one totally unnecessary function: factoring large numbers quickly. I was kind of impressed with how quickly I was able to make it factor such large numbers with my algorithm. factor3.py loads a file called primesexp.pkl, which is a large pickled list of prime numbers, which I no longer have, but I'm including the programs that I think I used to create it, cpickleprimes3.py and convertprimes.py. convertprimes.py converts a list of primenumbers downloaded from  http://primes.utm.edu/lists/small/millions/ to a single newline-separated listand, and cpickleprimes3.py converts that list to the pickled file, primesexp.pkl. I have no idea if that link still works.

I actually have a factor4.py, which seems to be a slight improvement to factor3.py, which I apparently wrote after the latest available ircbot version was made, so I'll include that. You should probably rename factor4.py to factor3.py or have ircbot import and use factor4 instead of factor3. I'm not gonna do it because I'm too lazy to test it.



