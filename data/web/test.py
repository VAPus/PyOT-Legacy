# A test frontpage hander.

class Frontpage(WebPage):
    def render_GET(self, request):
        return 'This is the frontpage'

@register('webPage', '') # Empty trigger = no childpage.
def index(**k):
    return Frontpage()
