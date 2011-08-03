# A file where we store all error excetions, work a bit like otserv's return values


class BaseError(Exception):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        if self.value:
            return repr(self.value)

class ImpossibleMove(BaseError): pass
class Cheat(BaseError): pass
class SolidTile(BaseError): pass