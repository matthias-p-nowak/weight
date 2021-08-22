#!/usr/bin/python3.9
import atexit
import logging
import completer
import config

if __name__ == '__main__':
  atexit.register(print,'good bye')
  logging.basicConfig(filename='debug.log', level=logging.DEBUG, filemode='w',
      format='%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d %(funcName)s: %(message)s', )
  logging.debug('started')
  completer.init_completer()
  config.init_config()
  completer.rootCompleter.run()

