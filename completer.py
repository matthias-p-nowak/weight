"""
completer takes input and provides completer options based on the previous entered tokens
"""
import logging
import pprint
import readline
import termcolor


class ComplOption:
    """
    The options for the completer
    """
    def __init__(self, name: str, final=False):
        """
        :param name: value to be displayed
        :param final: true of this is the final switch/flag, if true: everything left are options and values
        """
        self.name: str = name
        self.final: bool = final
        self.options = {}

    def exec(self,parts: list[str]):
        """
        default action is to start a completer at this level - needs to be customized
        :param parts: right side of command line, here it should be empty
        :return: None
        """
        print("connecting to submenu '%s'" % self.name)
        logging.debug("create completer for '%s'" % self.name)
        # TODO: create a new completer at this stage and execute it
        rc = Completer(self.name)
        for opn in self.options:
            rc.add(self.options[opn])
        rc.run()

    def prep(self,others: list[str], text: str) -> list[str]:
        """
        preparing the option array based on situation and entered arguments
        needs to be customized for variable options/arguments
        :param others: the right hand side of command line
        :param text: the beginning of the next argument
        :return:
        """
        logging.debug("nothing to prepare for me '{:s}'".format(self.name))
        fill=[]
        for op in self.options:
            if op.startswith(text):
                fill.append(op)
        return fill

    def add(self, other: 'ComplOption'):
        """
        adds a new option to this level
        :param other: the child
        """
        logging.debug("adding another option '%s' to '%s'" % (other.name, self.name))
        self.options[other.name] = other


class Completer():
    """
    A wrapper around readlines complete, it can be stacked. It completes and also parses the line.
    """
    def __init__(self, prompt=''):
        """
        initializer
        :param prompt: the displayed prompt
        """
        self.prompt = prompt
        self.fill: list[ComplOption] = []
        self.rootOption = ComplOption('')
        self.running = True

    def startOptions(self, text: str):
        """
        the first tab requires retrieval of all options
        it fills self.fill with the possible options
        :param text: the beginning of the current token
        :return: None
        """
        logging.debug(' start with -->%s' % text)
        self.fill = []
        line = readline.get_line_buffer()
        fields = line.split()
        if text == fields[-1]:
            fields=fields[:-1]
        logging.debug("line was '%s' parts were '%s'" % (line,pprint.pformat(fields)))
        option = self.rootOption
        others=[]
        for pi in range(len(fields)):
            # going through the tokens
            token=fields[pi]
            logging.debug('looking for %s' % token)
            others = fields[pi+1:]
            if token in option.options:
                option = option.options[token]
                if option.final:
                    break
                if not option.options:
                    # there are no further options
                    break
            else:
                logging.error('no option found %s' % (pprint.pformat(fields)))
                return
        # allow the option to prepare child options
        self.fill= option.prep(others,text)
        logging.debug('filled fill with %s' % pprint.pformat(self.fill))

    def complete(self, text: str, stage: int):
        if stage == 0:
            self.startOptions(text)
        if stage >= len(self.fill):
            return None
        return self.fill[stage]

    def add(self, other: ComplOption):
        logging.debug("adding '%s' to /" % other.name)
        self.rootOption.add(other)

    def run(self):
        # using global variable
        global rootCompleter
        logging.debug('running completer '+self.prompt)
        self.running = True
        while self.running:
            rootCompleter = self
            a = input(termcolor.colored(self.prompt,'green')+termcolor.colored('>', 'red'))
            token = a.split()
            if len(token)==0:
                # empty line ends run
                logging.debug("exiting")
                break
            logging.debug('executing %s', pprint.pformat(token))
            option = self.rootOption
            i = 0
            for p in token:
                if p in option.options:
                    i += 1
                    option = option.options[p]
                    if option.final:
                        break
                else:
                    break
            token = token[i:]
            logging.debug(' exec %s with %s' % (option.name, pprint.pformat(token)))
            option.exec(token)


# noinspection PyTypeChecker
rootCompleter: 'Completer' = None

def init_completer():
    global rootCompleter
    logging.debug('initializing Completer')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(lambda txt, st: rootCompleter.complete(txt, st))
    logging.debug('adding a root completer')
    rootCompleter = Completer()
