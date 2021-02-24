#
#     Copyright (C) 2017 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.
#

import os
from ccpem_gui.utils import window_utils
from ccpem_core.tasks.privateer import privateer_task
from ccpem_core.ccpem_utils import ccpem_file_types
from ccpem_gui.utils import command_line_launch

class PrivateerWindow(window_utils.CCPEMTaskWindow):
    '''
    Privateer window.
    '''
    def __init__(self,
                 task,
                 parent=None):
        super(PrivateerWindow, self).__init__(
            task=task,
            parent=parent)

    def set_args(self):
        '''
        Set input arguments
        '''
        # Job title
        self.title_input = window_utils.TitleArgInput(
            parent=self,
            arg_name='job_title',
            args=self.args)
        self.args_widget.args_layout.addWidget(self.title_input)

        # Input pdb
        input_pdb_input = window_utils.FileArgInput(
            parent=self,
            arg_name='input_pdb',
            required=True,
            file_types=ccpem_file_types.pdb_ext,
            args=self.args)
        self.args_widget.args_layout.addWidget(input_pdb_input)

        # Copies to find
        shake_input = window_utils.NumberArgInput(
            parent=self,
            arg_name='shift',
            args=self.args)
        self.args_widget.args_layout.addWidget(shake_input)

        # Extended options
        extended_options_frame = window_utils.CCPEMExtensionFrame(
            button_name='Extended options',
            button_tooltip='Show extended options')
        self.args_widget.args_layout.addLayout(extended_options_frame)

        # Keyword entry
        self.keyword_entry = window_utils.KeywordArgInput(
            parent=self,
            arg_name='keywords',
            args=self.args)
        self.args_widget.args_layout.addWidget(self.keyword_entry)

        # Set inputs for launcher
        self.launcher.add_file(
            arg_name='input_pdb',
            file_type='pdb',
            description=self.args.input_pdb.help,
            selected=True)

    def set_on_job_finish_custom(self):
        '''
        Actions to run on job completion.  Show output pdb.
        '''
        # Set launcher
        if self.task.pdbout_path is not None:
            if os.path.exists(path=self.task.pdbout_path):
                self.launcher.add_file(
                    arg_name=None,
                    path=self.task.pdbout_path,
                    file_type='pdb',
                    description='Output PDB file',
                    selected=True)
                self.launcher.set_tree_view()

def main():
    '''
    Launch standalone task runner.
    '''
    command_line_launch.ccpem_task_launch(
        task_class=privateer_task.Privateer,
        window_class=PrivateerWindow)

if __name__ == '__main__':
    main()
