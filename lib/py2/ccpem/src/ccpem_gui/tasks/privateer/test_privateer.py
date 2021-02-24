#
#     Copyright (C) 2017 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.
#

import unittest
import os
import sys
import shutil
import time
import tempfile
from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from ccpem_core.tasks.privateer import privateer_task
from ccpem_gui.tasks.privateer import privateer_window
from ccpem_core.test_data.tasks import privateer as privateer_test
from ccpem_core import ccpem_utils
from ccpem_core import process_manager

app = QtGui.QApplication(sys.argv)

class Test(unittest.TestCase):
    '''
    Unit test for Shake / PDBSet (invokes GUI).
    '''
    def setUp(self):
        '''
        Setup test data and output directories.
        '''
        self.test_data = os.path.dirname(privateer_test.__file__)
        self.test_output = tempfile.mkdtemp()

    def tearDown(self):
        '''
        Remove temporary data.
        '''
        if os.path.exists(path=self.test_output):
            shutil.rmtree(self.test_output)

    def test_shake_window_integration(self):
        '''
        Test pdbset shake refinement pipeline via GUI.
        '''
        pass
#         ccpem_utils.print_header(message='Unit test - Privateer')
#         # Load args
#         os.chdir(os.path.dirname(os.path.realpath(__file__)))
#         args_path = os.path.join(self.test_data, 'unittest_args.json')
#         run_task = privateer_task.Privateer(job_location=self.test_output,
#                                     args_json=args_path)
#         # Setup GUI
#         self.window = privateer_window.PrivateerWindow(task=run_task)
#         # Mouse click run
#         QTest.mouseClick(
#             self.window.tool_bar.widgetForAction(self.window.tb_run_button),
#             QtCore.Qt.LeftButton)
#         # Wait for run to complete
#         self.job_completed = False
#         timeout = 0
#         stdout = run_task.pipeline.pipeline[-1][0].stdout
#         while not self.job_completed and timeout < 500:
#             print 'Shake running for {0} secs (timeout = 500)'.format(timeout)
#             time.sleep(5.0)
#             timeout += 5
#             status =\
#                 process_manager.get_process_status(run_task.pipeline.json)
#             if status == 'finished':
#                 if os.path.isfile(stdout):
#                     tail = ccpem_utils.tail(stdout, maxlen=10)
#                     if tail.find('CCP-EM process finished') != -1:
#                         self.job_completed = True
#         # Check timeout
#         assert timeout < 500
#         # Check job completed
#         assert self.job_completed
#         print run_task.pdbout_path
#         # Check output created


if __name__ == '__main__':
    unittest.main()
