out = open('primes.txt','w')
for x in xrange(1,16):
  print "...",
  inf = open('primes\\primes'+str(x)+'.txt','r')
  inf.readline()
  out.write('\n'.join(inf.read().split())+'\n')
  print x

