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
        print self.test_output

    def tearDown(self):
        '''
        Remove temporary data.
        '''
        if os.path.exists(path=self.test_output):
            shutil.rmtree(self.test_output)

    def test_privateer_window_integration(self):
        '''
        Test Privateer pipeline via GUI.
        '''
        ccpem_utils.print_header(message='Unit test - Privateer')
        # Unit test args contain relative paths, must change to this directory
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        args_path = os.path.join(self.test_data, 'unittest_args.json')
        run_task = privateer_task.Privateer(
            job_location=self.test_output,
            args_json=args_path)
        print run_task.args.output_args_as_text()
        # Run w/ gui
        window = privateer_window.PrivateerWindow(task=run_task)
        # Mouse click run
        QTest.mouseClick(
            window.tool_bar.widgetForAction(window.tb_run_button),
            QtCore.Qt.LeftButton)
        # Wait for run to complete
        job_completed = False
        timeout = 0
        # Global refine stdout (i.e. last job in pipeline)
        delay = 5.0
        while not job_completed and timeout < 500:
            print 'Privateer running for {0} secs (timeout = 500)'.format(timeout)
            time.sleep(delay)
            timeout += delay
            status =\
                process_manager.get_process_status(run_task.pipeline.json)
            if status == 'finished':
                job_completed = True
        # Check timeout
        assert timeout < 500
        # Check job completed
        assert job_completed
        # Check html output file created
        html = os.path.join(window.task.job_location,
                            'report/index.html')
        assert os.path.exists(path=html)

if __name__ == '__main__':
    unittest.main()
