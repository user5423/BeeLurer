import sys
import unittest
sys.path.insert(0, './src/client/')

from torSessionManager import torSessionManager


class testTorSessionManager(unittest.TestSuite):

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


    ## These unittests should test
    ## 1. torSessionManager._initiateTorProccess()

    def test_init_ProcessAlreadyListeningOnPort(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_TorNotInstalled(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_TorProcessFailedToStartup(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_torSessionManagerObjectKilled(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_torSessionManagerProcessKilled(self):
        config = None
        self.TMS = torSessionManager(config)


    ## These unittests should test:
    ## 1. torSessionManager._initiateTorController(self):

    def test_init_TorControlPortAlreadyListened(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_TorControlPortNotListened(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_TorControlFailedToAuthenticate(self):
        config = None
        self.TMS = torSessionManager(config)


    ## These unittests should test all functions called by torSessionManager.__init__():
    ## 1. torSessionManager._setTorrcConfiguration()
    ## 2. torSessionManager._initiateTorProcess()
    ## 3. torSessionManager._initiateTorController(self):

    def test_init_defaultSuccess(self):
        config = None
        self.TMS = torSessionManager(config)

    def test_init_customSuccess(self):
        config = None
        self.TMS = torSessionManager(config)




