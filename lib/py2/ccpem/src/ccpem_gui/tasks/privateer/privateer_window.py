#
#     Copyright (C) 2017 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.
#


import os

from PyQt4 import QtGui, QtCore, QtWebKit

from ccpem_core.tasks.privateer import privateer_task
from ccpem_gui.utils import window_utils
from ccpem_core.ccpem_utils import ccpem_file_types
from ccpem_gui.utils import command_line_launch
from ccpem_core.ccpem_utils import get_test_data_path
from ccpem_core.test_data.tasks import privateer as test_data

        # self.n_mpi_input = window_utils.NumberArgInput(
        #     parent=self,
        #     arg_name='n_mpi',
        #     required=False,
        #     args=self.args)
        # mpi_layout.addWidget(self.n_mpi_input)
        # self.set_n_mpi_visible()
    
    


        # Dropdown menu for choice
        # symm_input = window_utils.ChoiceArgInput(
        #     parent=self,
        #     arg_name='symmetry',
        #     args=self.args,
        #     tooltip_text='Define symmetry')
        # self.args_widget.args_layout.addWidget(symm_input)



class PrivateerWindow(window_utils.CCPEMTaskWindow):
    '''
    Privateer window.
    '''
    gui_test_args = get_test_data_path(test_data, 'unittest_args.json')

    def __init__(self,
                 task,
                 parent=None):
        super(PrivateerWindow, self).__init__(task=task,
                                             parent=parent)
        self.rv_timer = QtCore.QTimer()
        self.rv_timer.timeout.connect(self.set_rv_ui)
        self.rv_timer.start(1500)

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
        self.title_input.value_line.editingFinished.connect(
            self.handle_title_set)

        # Input map
        self.model_input = window_utils.FileArgInput(
            parent=self,
            arg_name='input_model',
            args=self.args,
            label='Input model',
            file_types=ccpem_file_types.pdb_ext,
            required=True)
        self.args_widget.args_layout.addWidget(self.model_input)

        # Input map
        self.map_input = window_utils.FileArgInput(
            parent=self,
            arg_name='input_map',
            args=self.args,
            label='Input map',
            file_types=ccpem_file_types.mrc_ext,
            required=True)
        self.args_widget.args_layout.addWidget(self.map_input)

        # Resolution
        self.resolution_input = window_utils.NumberArgInput(
            parent=self,
            decimals=1,
            step=0.1,
            arg_name='resolution',
            args=self.args,
            required=True)
        self.args_widget.args_layout.addWidget(self.resolution_input)

        # Radius-in
        self.maskradius_input = window_utils.NumberArgInput(
            parent=self,
            decimals=1,
            step=0.1,
            minimum=1,
            maximum=10,
            arg_name='mask_radius',
            args=self.args,
            required=False)
        self.args_widget.args_layout.addWidget(self.maskradius_input)

        # Custom Sugar control frame
        self.custom_sugar_frame = window_utils.CCPEMExtensionFrame(
            button_name='A sugar I want to validate is not yet part of the Chemical Component Dictionary',
            button_tooltip='Define a sugar not yet part of the CCD')
        self.args_widget.args_layout.addLayout(self.custom_sugar_frame)

        # Sugar in PDB file input?
        self.confirm_undefined_sugar = window_utils.CheckArgInput(
            parent=self,
            label='Custom sugar is present in input model file',
            label_width=225,
            arg_name='undefinedsugar',
            args=self.args,
            required=True)
        self.custom_sugar_frame.add_extension_widget(self.confirm_undefined_sugar)

        # Custom CCD code
        self.custom_sugar_code = window_utils.StrArgInput(
            parent=self,
            label='Analyse sugar with code',
            arg_name='input_code',
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_sugar_code)

        # Custom Sugar Anomer
        self.custom_anomer = window_utils.ChoiceArgInput(
            parent=self,
            arg_name='input_anomer',
            second_width=None,
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_anomer)

        # Custom Sugar Handedness
        self.custom_handedness = window_utils.ChoiceArgInput(
            parent=self,
            arg_name='input_handedness',
            second_width=None,
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_handedness)
        
        # Custom Sugar Ring Conformation
        self.custom_ring_conformation = window_utils.ChoiceArgInput(
            parent=self,
            arg_name='input_ring_conformation',
            second_width=None,
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_conformation)
        self.custom_ring_conformation.value_line.currentIndexChanged.connect(
            self.set_conformation_input_options)

        # Custom Sugar Ring Conformation(Pyranose)
        self.custom_ring_pyranose = window_utils.ChoiceArgInput(
            parent=self,
            label_width=225,
            arg_name='input_conformation_pyranose',
            second_width=None,
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_pyranose)
        
        # Custom Sugar Ring Conformation(Furanose)
        self.custom_ring_furanose = window_utils.ChoiceArgInput(
            parent=self,
            label_width=225,
            arg_name='input_conformation_furanose',
            second_width=None,
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_furanose)

        # Custom Sugar Ring Oxygen
        self.custom_ring_oxygen = window_utils.StrArgInput(
            parent=self,
            arg_name='ring_oxygen',
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_oxygen)

        # Custom Sugar Ring Carbon 1
        self.custom_ring_C1 = window_utils.StrArgInput(
            parent=self,
            arg_name='ring_C1',
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_C1)

        # Custom Sugar Ring Carbon 2
        self.custom_ring_C2 = window_utils.StrArgInput(
            parent=self,
            arg_name='ring_C2',
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_C2)

        # Custom Sugar Ring Carbon 3
        self.custom_ring_C3 = window_utils.StrArgInput(
            parent=self,
            arg_name='ring_C3',
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_C3)

        # Custom Sugar Ring Carbon 4
        self.custom_ring_C4 = window_utils.StrArgInput(
            parent=self,
            arg_name='ring_C4',
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_C4)

        # Custom Sugar Ring Carbon 5
        self.custom_ring_C5 = window_utils.StrArgInput(
            parent=self,
            arg_name='ring_C5',
            args=self.args)
        self.custom_sugar_frame.add_extension_widget(self.custom_ring_C5)

        self.set_conformation_input_options()
        
        # Custom GlyTouCan settings frame
        self.glytoucan_settings_frame = window_utils.CCPEMExtensionFrame(
            button_name='Validation of Glycans with GlyTouCan and GlyConnect databases.',
            button_tooltip='Validation of Glycans with GlyTouCan and GlyConnect databases.')
        self.args_widget.args_layout.addLayout(self.glytoucan_settings_frame)

        # Enable GlyTouCan
        self.enable_glytoucan = window_utils.CheckArgInput(
            parent=self,
            label='Enable Glycan validation with GlyTouCan and GlyConnect databases',
            label_width=425,
            arg_name='glytoucan',
            args=self.args)
        self.glytoucan_settings_frame.add_extension_widget(self.enable_glytoucan)

        self.glyconnect_disable = window_utils.CheckArgInput(
            parent=self,
            label='Don\'t look for closest match on GlyConnect database if input glycan is not found',
            label_width=500,
            arg_name='closestmatch',
            second_width=None,
            args=self.args)
        self.glytoucan_settings_frame.add_extension_widget(self.glyconnect_disable)

        self.all_permutations_enable = window_utils.CheckArgInput(
            parent=self,
            label='Generate all possible Glycan permutation combinations in looking for the closest match',
            tooltip_text='Should only be used for O-glycans as computationally very expensive',
            label_width=550,
            arg_name='allpermutations',
            second_width=None,
            args=self.args)
        self.glytoucan_settings_frame.add_extension_widget(self.all_permutations_enable)

        self.ncpus = window_utils.NumberArgInput(
            parent=self,
            arg_name='ncpus',
            required=False,
            args=self.args)
        mpi_layout.addWidget(self.ncpus)
        self.ncpus_visible()


        # Detect number of CPUs
        # def set_n_mpi_all_cores(self):
        #     self.n_mpi_input.set_arg_value(QtCore.QThread.idealThreadCount())

        # def set_n_mpi_half_cores(self):
        #     self.n_mpi_input.set_arg_value(QtCore.QThread.idealThreadCount() / 2)

        # set_mpi_all_cpus_button = QtGui.QPushButton('Use all CPUs')
        # set_mpi_all_cpus_button.clicked.connect(self.set_n_mpi_all_cores)
        # set_mpi_all_cpus_button.setToolTip("Set the number of MPI nodes to use all of the CPU cores on this computer")
        # mpi_layout.addWidget(set_mpi_all_cpus_button)

        # set_mpi_half_cpus_button = QtGui.QPushButton('Use half CPUs')
        # set_mpi_half_cpus_button.clicked.connect(self.set_n_mpi_half_cores)
        # set_mpi_half_cpus_button.setToolTip("Set the number of MPI nodes to use half of the CPU cores on this computer")
        # mpi_layout.addWidget(set_mpi_half_cpus_button)
        
        # Privateer parallelism settings
        self.parallelism_settings = window_utils.CCPEMExtensionFrame(
            button_name='Parallelism settings.',
            button_tooltip='Parallelism settings.')
        self.args_widget.args_layout.addLayout(self.parallelism_settings)

        # Privateer parallelism settings
        self.disable_multithreaded = window_utils.CheckArgInput(
            parent=self,
            label='Run Privateer in single-threaded mode.',
            label_width=300,
            arg_name='singlethreaded',
            args=self.args)
        self.parallelism_settings.add_extension_widget(self.enable_glytoucan)


        self.all_permutations_enable = window_utils.CheckArgInput(
            parent=self,
            label='Generate all possible Glycan permutation combinations in looking for the closest match',
            tooltip_text='Should only be used for O-glycans as computationally very expensive',
            label_width=550,
            arg_name='allpermutations',
            second_width=None,
            args=self.args)
        self.parallelism_settings.add_extension_widget(self.all_permutations_enable)


    
    def set_conformation_input_options(self):
        if self.args.input_ring_conformation.value == 'pyranose':
            self.custom_ring_pyranose.show()
            self.custom_ring_furanose.hide()
            self.custom_ring_oxygen.show()
            self.custom_ring_C1.show()
            self.custom_ring_C2.show()
            self.custom_ring_C3.show()
            self.custom_ring_C4.show()
            self.custom_ring_C5.show()
        elif self.args.input_ring_conformation.value == 'furanose':
            self.custom_ring_pyranose.hide()
            self.custom_ring_furanose.show()
            self.custom_ring_oxygen.show()
            self.custom_ring_C1.show()
            self.custom_ring_C2.show()
            self.custom_ring_C3.show()
            self.custom_ring_C4.show()
            self.custom_ring_C5.hide()



    def set_rv_ui(self):
        '''
        RVAPI results viewer.
        '''
        if hasattr(self.task, 'job_location'):
            if self.task.job_location is not None:
                report = os.path.join(self.task.job_location,
                                      'report/index.html')
                if os.path.exists(report):
                    self.rv_view = QtWebKit.QWebView()
                    self.rv_view.load(QtCore.QUrl(report))
                    self.results_dock = QtGui.QDockWidget('Results',
                                                          self,
                                                          QtCore.Qt.Widget)
                    self.results_dock.setToolTip('Results overview')
                    self.results_dock.setWidget(self.rv_view)
                    self.tabifyDockWidget(self.setup_dock, self.results_dock)
                    self.results_dock.show()
                    self.results_dock.raise_()
                    self.rv_timer.stop()

    def set_on_job_running_custom(self):
        # Structure factor from input map
        if hasattr(self.task, 'process_maptomtz'):
            self.launcher.add_file(
                arg_name=None,
                path=self.task.process_maptomtz.hklout_path,
                file_type='mtz',
                description='Structure factors from input map',
                selected=False)
        # Add PDB from last Privateer cycle
        for i in range(1, (self.args.ncycle.value)):
            path = os.path.dirname(self.task.process_privateer_pipeline.pdbout)
            fname = os.path.join(path, 'build' + str(i) + '.pdb')
            self.launcher.add_file(
                path=fname,
                file_type='pdb',
                description='Model built from Privateer cycle #' + str(i),
                selected=False)
            path = os.path.dirname(self.task.process_refine.pdbout_path)
            fname = os.path.join(path, 'refined' + str(i) + '.pdb')
            self.launcher.add_file(
                path=fname,
                file_type='pdb',
                description='Model built and refined from Privateer cycle #' +
                str(i),
                selected=False)
        # needed this line to refresh the file launcher view
        self.launcher.set_tree_view()

    def set_on_job_finish_custom(self):
        '''
        Actions to run on job completion.  For now show starting, refined
        pdb and experimental map.
        '''
        if hasattr(self.task, 'process_privateer_pipeline'):
            if hasattr(self.task, 'process_refine'):
                self.launcher.add_file(
                    path=self.task.process_privateer_pipeline.pdbout,
                    file_type='pdb',
                    description='Model built from final Privateer cycle',
                    selected=False)
                self.launcher.add_file(
                    path=self.task.process_refine.pdbout_path,
                    file_type='pdb',
                    description='Final Privateer built and refined model',
                    selected=True)
        self.launcher.set_tree_view()
        self.launcher_dock.raise_()


def main():
    '''
    Launch standalone task runner.
    '''
    command_line_launch.ccpem_task_launch(
        task_class=privateer_task.Privateer,
        window_class=PrivateerWindow)


if __name__ == '__main__':
    main()
