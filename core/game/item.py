items = {}
items[106] = {'cid':4526}
items[107] = {'cid':4527}

class BaseItem:
     def cid(self):
         return items[self.itemId]['cid']


class Item(BaseItem):
     pass
