items = {}
items[106] = {'cid':4526, 'speed':1}
items[107] = {'cid':105}

class BaseItem:
     def cid(self):
         return items[self.itemId]['cid']


class Item(BaseItem):
     pass
