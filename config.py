import atexit
import json
import logging
import os
import pprint

import completer

# according to the standard filesystem recommendation
CFGFILE = os.path.expanduser('~/.config/weight/weight.json')

# the global configuration dictionary
Config: dict[str,str] = {}

def getConfig(key: str, default=None):
    """
    returns value from configuration
    :param key: key
    :param default: if not found, this will be returned and put into config
    :return: the configuration value
    """
    if key in Config:
        return Config[key]
    else:
        if default is None:
            return None
        Config[key]=default
        return default

def writeConfig():
    """
    Writes configuration back at the end
    """
    global Config
    try:
        bp = os.path.dirname(CFGFILE)
        if not os.path.exists(bp):
            os.mkdir(bp)
        with open(CFGFILE, 'w') as outp:
            json.dump(Config, outp, ensure_ascii=True, sort_keys=True, indent=2)
            logging.debug('wrote config file %s' % CFGFILE)
    except Exception as e:
        logging.error('could not write %s due to %s' % (CFGFILE, e))


def listConfig(args: list[str]):
    """
    prints out all configuration values
    :param args:  not used
    """
    global Config
    logging.debug('listening all configs')
    maxKeyLength = 0
    # determining the longest length of the keys
    for key in Config:
        if maxKeyLength < len(key):
            maxKeyLength = len(key)
    f = "  {:>" + str(maxKeyLength) + "s} = {:s}"
    for key in Config:
        print(f.format(key, Config[key]))


class DelConfig(completer.ComplOption):
    """
    A completer options for deleting values
    """
    def prep(self, others: list[str], text: str) -> list[str]:
        global Config
        logging.debug("called with {} starting with {}".format(pprint.pformat(others),text))
        fill=[]
        for key in Config:
            if key in others:
                logging.debug(" already have {} in arguments".format(key))
                continue
            if key.startswith(text):
                fill.append(key)
        return fill

    def exec(self, args: list[str]):
        global Config
        logging.debug("called")
        for key in args:
            logging.debug("deleting {}".format(key))
            Config.pop(key, None)

class GetConfig(DelConfig):
    """
    completer option for getting values
    """
    def exec(self, args: list[str]):
        global Config
        maxKeyLength = 0
        # determining the longest length of the keys
        for key in Config:
            if maxKeyLength < len(key):
                maxKeyLength = len(key)
        f = "  {:>" + str(maxKeyLength) + "s} = {:s}"
        for key in args:
            print(f.format(key, Config[key]))

class SetConfig(completer.ComplOption):
    """
    Setting options, alternatively name value
    """
    def prep(self, others: list[str], text: str) -> list[str]:
        global Config
        logging.debug("called with {} starting with {}".format(pprint.pformat(others),text))
        fill=[]
        if len(others)% 2 == 0:
            for key in Config:
                if key in others:
                    continue
                if key.startswith(text):
                    fill.append(key)
        else:
            for key in Config:
                val=Config[key]
                if val in fill:
                    continue
                if val.startswith(text):
                    fill.append(val)
        return fill

    def exec(self, args: list[str]):
        """
        setting config value
        :param args: list of pairs, name value
        :return:
        """
        global Config
        for i in range(0,len(args),2):
            key=args[i]
            val=args[i+1]
            Config[key]=val

def init_config():
    # reading the config
    global Config
    logging.debug('reading config from %s' % CFGFILE)
    try:
        with open(CFGFILE) as inp:
            Config = json.load(inp)
    except:
        logging.warning("couldn't read %s" % CFGFILE)
    atexit.register(writeConfig)
    # adding interactive editing of config values
    cfg = completer.ComplOption('config')
    # ---
    cmdLst = completer.ComplOption('list', final=True)
    cmdLst.exec = listConfig
    cfg.add(cmdLst)
    # ---
    cmdSet = SetConfig('set', final=True)
    cfg.add(cmdSet)
    # ---
    cmdDel = DelConfig('delete', final=True)
    cfg.add(cmdDel)
    # ---
    cmdGet = GetConfig('get', final=True)
    cfg.add(cmdGet)
    # ---
    completer.rootCompleter.add(cfg)
    Config['hello'] = 'world'
    Config['yellow'] = 'submarine'
