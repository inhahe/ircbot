##by Richard A. Nichols III, 2007
## 
##factor() returns the factorization of a given number.
## 
##primes.txt should be a newline-separated list of all prime numbers to
##an arbitrary limit.  i got my primes from
##http://primes.utm.edu/lists/small/millions/ and converted them to the above
##format.
## 
##it runs pretty fast up to a certain size input (10**19, for me) and then 
##it goes into diskswapping hell.



# optimize reading from file

import sys, cPickle
inf = open('primesexp.pkl','rb')
primes = [2]
primesset = set(primes)

def factor(number, factors=[], lpi=0):
  global primes, primesset, lp
  if number in primesset:
    return factors+[number]
  sqrt = int(number ** .5)
  pi = lpi
  prime = primes[pi]
  lenprimes = len(primes)
  while prime <= sqrt:
    if pi==lenprimes:
      if lenprimes >= 2715521:
        raise ValueError("The number could not be factored because it contains prime factors that are > 44955397.")
      tp = cPickle.load(inf)
      primes += tp
      primesset.update(tp)
      lenprimes += len(tp)

    else:
      prime = primes[pi]
    if number % prime == 0:
      return factor(number/prime, factors+[prime], pi)
    pi += 1
  return factors+[number]


if __name__ == "__main__":


  if len(sys.argv)==2:
    try: factors = factor(int(sys.argv[1]))
    except ValueError, e: print e
    else: print '['+', '.join(str(f) for f in factors)+']' if factors else "prime"
  else:
    for x in range(18):
      number = int('1'*(x+1))
      print
      print number
      try: factors = factor(number)
      except ValueError, e: print e
      else: print '['+', '.join(str(f) for f in factors)+']' if factors else "prime"
