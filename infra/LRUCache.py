from collections import defaultdict

class LRUCache:

    def __init__(self, capacity: int):
        
        from collections import OrderedDict
        
        self.pairs = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        
        if key in self.pairs:
            self.pairs.move_to_end(key)
            return self.pairs[key]
        else: 
            return None

    def put(self, key: int, value: int) -> None:
        
        if key not in self.pairs and len(self.pairs) == self.capacity:
            self.pairs.popitem(last = False)
        
        if key in self.pairs:
            self.pairs.move_to_end(key)

        self.pairs[key] = value
        
        return None
