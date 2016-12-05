__author__ = 'Administrator'
import types
def Fibonacci(n):
    assert n > 0
    V = [1, 1]
    for i in range(2, n):
        V.append(V[i-1] + V[i-2])
    for i in range(0, n):
         print V[i]
    return V

def Fb(max):
    a,b,n = 0,1,1
    while n <= max:
        a, b = b, a + b
        print a
        n = n + 1
    return a

class Fab(object):
    def __init__(self, max):
        assert max > 0
        self._a, self._b, self._n, self._max = 0, 1, 1, max

    def next(self):
        if self._n <= self._max:
            self._a, self._b = self._b, self._a + self._b
            print self._a
            self._n += 1
            return self._a
        #raise StopIteration()

    def __iter__(self):
        return self


def yFab(max):
    a, b, n= 0, 1, 1
    while n <= max :
        yield b
        a, b = b, a+b
        #yield a
        n += 1

print isinstance(yFab, types.GeneratorType)
print isinstance(yFab(5), types.GeneratorType)
print isinstance(Fab(5), types.GeneratorType)



#for n in Fab(5):
#    print n

f = Fab(5)
f.next()
f.next()
f.next()
f.next()
f.next()
#f.next()












