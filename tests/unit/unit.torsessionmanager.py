import sys
import unittest
sys.path.insert(0, './src/client/baitConnector.py')

from baitConnector import torSessionManager


class testTorSessionManager:

    ## These unittests should test: 
    ## 1. torSessionManager._setTorrcConfiguration()
    ## 2. torSessionManager._initiateTorProcess()
    
    def test_init_Default(self):
        self.TSM = torSessionManager()

    def test_init_EmptyDict(self):
        config = {}
        self.TMS = torSessionManager(config)

    def test_init_AbsentConfigKeys(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_IncorrectValueConfigKey(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_IncorrectValueConfigKeys(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_NonexistentConfigKeys(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_IncorrectFormatConfigValue(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_IncorrectFormatConfigValues(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_IncorrectValueConfigValues(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_IncorrectValuesConfigValues(self):
        config = None
        self.TMS = torSessionManager(config)


    


    ## We want to test

