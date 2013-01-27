# A test frontpage hander.

class Frontpage(WebPage):
    def render_GET(self, request):
        return 'This is the frontpage'

@register('webPage', '') # Empty trigger = no childpage.
def index(**k):
    return Frontpage()

# More effective design.
@registerClass('webPage', 'delay')
class SQL(WebPage):
    def _delayedRender(self, request):
        request.write("<html><body>Sorry to keep you waiting.</body></html>")
        request.finish()

    def render_GET(self, request):
        callLater(5, self._delayedRender, request)
        return NOT_DONE_YET
