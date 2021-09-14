"""
 Copyright Mykola Rabchevskiy 2021
 Distributed under the Boost Software License, Version 1.0.
 (See http://www.boost.org/LICENSE_1_0.txt)
 
_______________________________________________________________________________


 Proof-of-concept for algorithm of causality discovering described in 
 
   https://agieng.substack.com/p/agi-causality
 
 
 On the output:   +  means hits only
                  -  means no hits
                  :  means presence both hits and non-hits
 
 
 NOTE: Data generated randomly, so each run of the script produces different 
       output; run script a few times to evaluate real algorithm behavior.
      

_______________________________________________________________________________
"""

from math import *

from datetime import datetime
from random   import seed
from random   import random


seed( datetime.now() )

Rt = 3.0   # :visibility radius
Ro = 1.0   # :sum of radiuses of th controlled object and external one

STOP_AT_HIT = 50  #: limit for number of hits (collisions)

X = 'X'
Y = 'Y'
R = 'R'
A = 'A'
H = 'H'

Q = { X:0.1, Y:0.1, R:0.1, A:0.1 }  # :discretization quants

def randomSituation():
  '''
  Compose random situation:
  '''
  while True:
    x = Rt*( -1.0 + 2.0*random() )
    y = Rt*( -1.0 + 2.0*random() )
    r = sqrt( x**2 + y**2 )
    if r <= Rt: 
      return { X:x, Y:y, R:r, A:atan2( x, y ), H: r < Ro } 
  
experience = []        


def valueRange( data ):
  '''
  Calculation of data range:
  '''
  Vmin = None                  # :min discrete value
  Vmax = None                  # :max discrete value
  for value in data:
    if Vmin is None:
      Vmin = value
      Vmax = value
    else:
      if value > Vmax: Vmax = value
      if value < Vmin: Vmin = value
  return Vmin, Vmax
  

def test( f ):
  '''
  Test the whole current samples set: 
  '''
  assert( f in Q )
  M = {} # :maps discrete value -> { False:num of non-hit, True: num of hit }
  for sample in experience:
    '''
    Discretization: ( 0.0 .. 1.0 ] mapped to 0
                    ( 1.0 .. 2.0 ] mapped to 1
                         ....
    '''
    i = int( round( -0.5 + sample[f]/Q[f] ) )  # :discretized `f` value 
    if i not in M: M[i] = { False: 0, True: 0 }
    M[i][ sample[H] ] += 1
  pattern = ''
  C       = []
  Vmin, Vmax = valueRange( M )
  for i in range( Vmin, Vmax + 1 ):
    if i in M:
      Mi = M[i]
      if Mi[ True ] > 0 and Mi[ False ] > 0 : 
        pattern += ':'
      elif Mi[ True ] > 0: 
        pattern += '+'
        C.append( i )
      else: 
        pattern += '-'
    else:
      pattern += ' '
  parted = True      
  L = len( pattern )
  if L > 2:
    for i in range( 1, L-1 ):
      Si = pattern[i]
      if Si != ':': continue
      if pattern[i-1] == ':' or pattern[i+1] == ':' : parted = False
  return parted, pattern, C


def intervals( cause, C ):
  '''
  Convert list of discretized value into list of intervals:
  '''
  data = []  
  q = Q[ cause ]
  
  def add( head, tail ):
    data.append( "[ %.2f .. %.2f ]" % ( q*float( head ), q*( 1.0 + float( tail ) ) ) )
  
  last = C[-1]
  head = None
  tail = None
  for i in C:
    if tail is None:
      if i == last: 
        add( i, i )
      else:
        head = i
        tail = i
    else:
      if i == last:
        tail = last
        add( head, tail )
      elif i > tail + 1:
        add( head, tail )
        head = i
        tail = i
      else: 
        tail = i
  return ' or '.join( data )

        
def causality(): 
  '''
  Discover causality:
  '''
  print( "\n      Possible causes: %s" % { X, Y, R, A } )
  i   = 0
  hit = 0
  while hit < STOP_AT_HIT:
    i += 1
    Si = randomSituation()
    experience.append( Si ) 
    if Si[H]: 
      hit += 1
      '''
      Try to detect hit cause:
      '''
      print( "\n %4d samples, %2d hits  x:%f Y:%f R:%f A:%f" 
             % ( i, hit, Si[X], Si[Y], Si[R], Si[A] ) )
      hypotheses = set()
      C = {}
      for potentialCause in [ X, Y, R, A ]: 
        parted, pattern, C[ potentialCause ] = test( potentialCause )
        if parted: hypotheses.add( potentialCause )
        print( "      %s [%s]" % ( potentialCause, pattern ) )        
      if len( hypotheses ) == 1 : 
        cause = sorted( hypotheses )[0]                
        print( "      CAUSE: %s in %s" % ( cause, intervals( cause, C[ cause ] ) ) )
      else: 
        print( "      Possible causes: %s" % hypotheses )
"""
_______________________________________________________________________________
"""    

if __name__ == "__main__":    
  causality()

