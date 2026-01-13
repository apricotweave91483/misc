#!/opt/homebrew/bin/python3

from fractions import Fraction
from numpy import array

x = array(list(map(Fraction, input().split())))
x /= x[0]
print(x)
