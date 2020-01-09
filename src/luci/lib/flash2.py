# Original published by Ansel at
# http://groups.google.com/group/turbogears/browse_thread/thread/c86f1c18d6e12a71
# Slighly edited to fit current version of TG2 and project requirements.

from tg import session
from paste.registry import StackedObjectProxy

__all__ = ['Flash2', 'flash2']


class _Flash2Message(object):
    def __init__(self, msg, cls='info', html=False, hideable=False):
        self.message = msg
        self.css = cls
        self.html = html
        self.hideable = hideable
        self.hash = id(self)

    def __repr__(self):
        return "<_Flash2Message: %s>" % self.__str__()

    def __str__(self):
        return  "%s [%s]" % (self.message, self.css)


class Flash2:
    """A more advanced replacement for TurboGears2 built-in ``flash'' functionality.

    It is intended to use this component in a local/request-local manner
    (singleton object of this class) which can be reached this way:

    1. Register instance of this class together with 'flash2' proxy object
       exported by this module with paste.registry object in your framework
       (it is supposed that this middleware is plugged-in0.
       For TurboGears2, you can use following in your root controller:

    from luci.lib.flash2 import flash2, Flash2
    class RootController(BaseController):
        def __call__(self, environ, start_response):
            environ['paste.registry'].register(flash2, Flash2())
        # you code

    2. In the module/controller where you want to use the instance of this class,
       just import 'flash2' proxy object exported by this module. Then, simply
       use flash2 as if it was directly the instance of this class.

    Example usage:
        flash2.info('This is info.')
        flash2.warning('This is warning.')
        flash2.flush()

    Note the same can be achieved by:
        flash2.info('This is info.').warning('This is warning').flush()

    As shown, you always have to use 'flush' method in order to store the state
    of flash messages to session's data which are read on the templates side
    afterwards and displayed on respective page. During (the first) iteration
    over the instance of this class, all messages are consequently popped
    making this instance messages-free. That's why this iteration is intended
    way of use on the templates side.

    """
    def __init__(self):
        self.__messages = []
        #self.__messages_dict = {'info':[], 'warning':[], 'error':[], 'ok': []}

    def __iter__(self):
        class DeletingIterator:
            def __init__(self, messages):
                self.__messages = messages
            def __iter__(self):
                return self
            def next(self):
                try:
                    # Note: self.__messages_dict should be handled if used.
                    item = self.__messages.pop(0)
                    return item
                except IndexError:
                    raise StopIteration
        return DeletingIterator(self.__messages)

    def __repr__(self):
        return "<Flash2 with messages: %s>" % ", ".join(map(lambda m: str(m), self.get_messages()))

    def __add_message(self, msg, cls, html=False, hideable=False):
        m = _Flash2Message(msg, cls, html, hideable)
        self.__messages.append(m)
        #if cls not in self.__messages_dict:
        #    self.__messages_dict[cls] = []
        #self.__messages_dict[cls].append(m)
        return self

    def flush(self):
        session['flash2'] = self
        session.save()

    def get_messages(self):
        return self.__messages[:]

    #def get_messages_dict(self)
    #    return self.__messages_dict.copy()

    #---

    def info(self, msg, html=False, hideable=True):
        return self.__add_message(msg, 'info', html, hideable)

    def warning(self, msg, html=False, hideable=True):
        return self.__add_message(msg, 'warning', html, hideable)

    def error(self, msg, html=False, hideable=False):
        return self.__add_message(msg, 'error', html, hideable)

    def ok(self, msg, html=False, hideable=True):
        return self.__add_message(msg, 'ok', html, hideable)


# Proxy object as mentioned in Flash2 class doc.
flash2 = StackedObjectProxy()
