# Simple ring buffer implementation using deque
# written by vegaseat, originally acquired from:
# http://www.daniweb.com/forums/post202523-3.html
#
# I have no idea what licensing terms this would be distributed under,
# though I figure they're fairly liberal since the code was posted
# on a public forum.

from collections import deque

class RingBuffer(deque):
    """
    inherits deque, pops the oldest data to make room
    for the newest data when size is reached
    """
    def __init__(self, size):
        deque.__init__(self)
        self.size = size
        
    def full_append(self, item):
        deque.append(self, item)
        # full, pop the oldest item, left most item
        self.popleft()
        
    def append(self, item):
        deque.append(self, item)
        # max size reached, append becomes full_append
        if len(self) == self.size:
            self.append = self.full_append
    
    def get(self):
        """returns a list of size items (newest items)"""
        return list(self)
