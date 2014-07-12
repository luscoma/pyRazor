__author__ = 'hoseinyeganloo@gmail.com'


class ViewLoader:

    # catching views to reduce io cost.
    __views__ = dict()

    @staticmethod
    def __init__():
        pass

    @staticmethod
    def Load(name,refresh = False):
        if name in ViewLoader.__views__.keys() or refresh:
            return ViewLoader.__views__[name]
        else:
            #try:
                f = open(name)
                ViewLoader.__views__[name] = f.read()
                f.close()
                return ViewLoader.__views__[name]
            #except:
            #   return 'Referenced view not found!';