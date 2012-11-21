# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from functools import partial
import logging
import signal

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
from PyQt4.QtGui import (QApplication, QSystemTrayIcon, QMessageBox)
from PyQt4.QtCore import QTimer
from PyQt4 import QtCore

from leap import __version__ as VERSION
from leap.baseapp.mainwindow import LeapWindow

def sigint_handler(*args):
    #import pdb4qt as pdb; pdb.set_trace()
    app = args[0]
    app.cleanupAndQuit()

def main():
    """
    launches the main event loop
    long live to the (hidden) leap window!
    """
    import sys
    from leap.util import leap_argparse
    parser, opts = leap_argparse.init_leapc_args()
    debug = getattr(opts, 'debug', False)

    # XXX get severity from command line args
    if debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    logger = logging.getLogger(name='leap')
    logger.setLevel(level)
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s '
        '- %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    #logger.debug(opts)
    logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    logger.info('LEAP client version %s', VERSION)
    logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    logfile = getattr(opts, 'log_file', False)
    if logfile:
        logger.debug('setting logfile to %s ', logfile)
        fileh = logging.FileHandler(logfile)
        fileh.setLevel(logging.DEBUG)
        fileh.setFormatter(formatter)
        logger.addHandler(fileh)

    logger.info('Starting app')
    app = QApplication(sys.argv)

    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None) 

    # needed for initializing qsettings
    # it will write .config/leap/leap.conf
    # top level app settings
    # in a platform independent way
    app.setOrganizationName("leap")
    app.setApplicationName("leap")
    app.setOrganizationDomain("leap.se")

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray",
                             "I couldn't detect"
                             "any system tray on this system.")
        sys.exit(1)
    if not debug:
        QApplication.setQuitOnLastWindowClosed(False)

    window = LeapWindow(opts)

    sigint_window = partial(sigint_handler, window)
    signal.signal(signal.SIGINT, sigint_window)
    #signal.signal(signal.SIGINT, lambda: QtCore.QMetaObject.invokeMethod(window, 'cleanupAndQuit'))
    #window.shutdownSignal.connect(window.cleanupAndQuit)
    #signal.signal(signal.SIGINT, window.shutdownSignal.emit))

    if debug:
        # we only show the main window
        # if debug mode active.
        # if not, it will be set visible
        # from the systray menu.
        window.show()

    # run main loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
