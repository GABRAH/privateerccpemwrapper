#
#     Copyright (C) 2017 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.
#

'''
CCP-EM main window.
'''


import sys
import os
import traceback

from PyQt4 import QtGui
from PyQt4 import QtCore

import ccpem_core
from ccpem_core import ccpem_utils
from ccpem_core import process_manager
from ccpem_core import settings
from ccpem_gui import icons
from ccpem_gui.image_viewer import gallery_viewer
from ccpem_gui.image_viewer import mrc_edit_window
from ccpem_gui.project_database import sqlite_project_database
from ccpem_gui.project_database import database_widget
from ccpem_gui.project_database import project_widget
from ccpem_gui.project_database import project_manager
from ccpem_gui.tasks import ccpem_tasks
from ccpem_gui.utils import gui_process
from ccpem_gui.utils import ccpem_widgets
from ccpem_gui.utils import window_utils

# Import modeller if available
try:
    import modeller
    modeller_available = True
except ImportError:
    modeller_available = False


class CCPEMProjectWindow(QtGui.QMainWindow):
    '''
    Window to show job view and project manager
    '''
    def __init__(self, parent=None):
        super(CCPEMProjectWindow, self).__init__(parent)
        # Reassign main window from parent for call backs
        self.main_window = parent
        self.set_docks()
        self.set_jobs_widget()
        self.set_projects_widget()

    def set_jobs_widget(self):
        '''
        Set jobs widget
        '''
        self.jobs_widget = None
        if self.main_window.database is not None:
            self.jobs_widget = MainWindowProjectView(
                main_window=self.main_window)
            self.jobs_dock.setWidget(self.jobs_widget)
            self.jobs_dock.show()
            self.jobs_dock.raise_()
        else:
            self.jobs_dock.hide()

    def set_projects_widget(self):
        '''
        Set projects widget
        '''
        if self.main_window.ccpem_projects is not None:
            self.projects_widget = MainWindowProjectWidget(
                ccpem_projects=self.main_window.ccpem_projects,
                main_window=self.main_window)
            self.projects_scroll = QtGui.QScrollArea()
            self.projects_scroll.setWidgetResizable(True) # Set to make the inner widget resize with scroll area
            self.projects_scroll.setWidget(self.projects_widget)
            self.projects_dock.setWidget(self.projects_scroll)

    def set_docks(self):
        '''
        Setup docks to hold projects and jobs widgets
        '''
        self.jobs_dock = QtGui.QDockWidget('Jobs',
                                           self,
                                           QtCore.Qt.Widget)
        self.projects_dock = QtGui.QDockWidget('Projects',
                                               self,
                                               QtCore.Qt.Widget)
        # Set docks
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.jobs_dock)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.projects_dock)
        self.tabifyDockWidget(self.jobs_dock, self.projects_dock)
        # Set dock options
        self.setDockOptions(
            QtGui.QMainWindow.ForceTabbedDocks |
            QtGui.QMainWindow.VerticalTabs |
            QtGui.QMainWindow.AnimatedDocks)


class CCPEMMainWindow(QtGui.QMainWindow):
    '''
    Main window class to hold job history and task launch buttons.
    '''
    def __init__(self,
                 splash=None,
                 show_warning=True,
                 args=None,
                 parent=None):
        super(CCPEMMainWindow, self).__init__(parent)
        self.args = args
        self.database = None
        self.ccpem_projects = None
        self.version = ccpem_utils.CCPEMVersion()

        # Get tasks
        self.tasks = ccpem_tasks.CCPEMTasks(alpha=self.args.alpha())

        # Set main layout
        widget = QtGui.QWidget()
        self.main_layout = QtGui.QHBoxLayout(widget)
        self.setCentralWidget(widget)

        # Set size and title
        self.resize(
            QtGui.QDesktopWidget().availableGeometry(self).size() * 0.5)
        self.setWindowTitle('CCPEM | {0}'.format(self.version.name))

        # Set task buttons
        self.set_task_buttons()

        # Set project view
        self.set_project_window()

        # Check if CCP4 is present
        ccp4_warnings = self.tasks.check_ccp4_environment()

        if show_warning:
            if ccp4_warnings is not None:
                if splash is not None:
                    splash.close()
                self.show_ccp4_not_found()

            # Show task errors
            if self.tasks.errors:
                if splash is not None:
                    splash.close()
                self.show_task_errors()

    def show_ccp4_not_found(self):
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        q_settings = QtCore.QSettings()
        if q_settings.value('dont_show_ccp4_warning', type=bool):
            return
        msg.setText('CCP4 not found')
        info_text = (
            'As CCP4 was not found some tasks will be unavailable. '
            'If CCP4 is installed please ensure environment '
            'variables can be found prior to launching CCP-EM:'
            '\n\nsource <path to ccp4>/bin/ccp4.setup-sh'
            '\nor'
            '\nsource <path to ccp4>/bin/ccp4.setup-csh')
        msg.setInformativeText(info_text)
        msg.setWindowTitle('CCP4 warning')
        dont_show = QtGui.QCheckBox("Don't show this again")
        dont_show.blockSignals(True)
        msg.addButton(dont_show, QtGui.QMessageBox.ApplyRole)
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        retval = msg.exec_()
        if retval == QtGui.QMessageBox.Ok:
            if dont_show.isChecked():
                q_settings.setValue('dont_show_ccp4_warning', True)

    def show_task_errors(self):
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        q_settings = QtCore.QSettings()
        if q_settings.value('dont_show_task_warnings', type=bool):
            return
        msg.setText('Some CCP-EM tasks not available')
        msg.setWindowTitle('CCP-EM task warning')
        errors = 'Task errors:'
        for key, value in self.tasks.errors.iteritems():
            print str(value)
            errors += '\n{0} : {1}'.format(key, value)
        msg.setInformativeText(errors)
        dont_show = QtGui.QCheckBox("Don't show this again")
        dont_show.blockSignals(True)
        msg.addButton(dont_show, QtGui.QMessageBox.ApplyRole)
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        retval = msg.exec_()
        if retval == QtGui.QMessageBox.Ok:
            if dont_show.isChecked():
                q_settings.setValue('dont_show_task_warnings', True)

    def set_tasks_projects(self):
        '''
        This is called outside of init otherwise any warning messages are hidden
        behind splash screen.
        '''
        self.set_projects()
        tasks_projects_splitter = QtGui.QSplitter()
        tasks_projects_splitter.addWidget(self.task_scroll)
        tasks_projects_splitter.addWidget(self.project_box)
        self.main_layout.addWidget((tasks_projects_splitter))
        self.set_test_mode(False)

    def set_project_window(self):
        # Add group box for frame
        self.project_box = QtGui.QGroupBox()
        self.project_box_layout = QtGui.QHBoxLayout()
        self.project_box.setLayout(self.project_box_layout)
        # Set project window
        self.project_window = CCPEMProjectWindow(parent=self)
        self.project_box_layout.addWidget(self.project_window)

    def set_projects(self):
        if self.args.projects.value is '':
            settings_path = os.path.dirname(self.args.location.value)
            projects_path = os.path.join(settings_path, 'ccpem_projects.json')
            self.args.projects.value = projects_path
            self.args.output_args_as_json(self.args.location.value)
        self.ccpem_projects = project_manager.CCPEMProjectContainer(
            filename=self.args.projects.value)
        self.project_window.set_projects_widget()
        self.active_project_path = \
            self.ccpem_projects.get_active_project_path()
        if self.active_project_path is None:
            self.database_path = None
            self.database = None
            self.task_buttons.setEnabled(False)
        else:
            self.set_database()
            self.task_buttons.setEnabled(True)

    def set_active_project(self, active_project_path):
        # Set active project
        self.active_project_path = active_project_path
        self.set_database()
        self.project_window.set_jobs_widget()
        if self.active_project_path is not None:
            # Set working directory to project directory
            os.chdir(self.ccpem_projects.get_active_project().path)
            # Add project directory to dialog side bar
            dialog = QtGui.QFileDialog()
            dialog_urls = dialog.sidebarUrls()
            project_url = QtCore.QUrl.fromLocalFile(self.active_project_path)
            if project_url not in dialog_urls:
                dialog_urls.append(project_url)
                dialog.setSidebarUrls(dialog_urls)
            self.args.output_args_as_json(self.args.location.value)
            self.task_buttons.setEnabled(True)

    def set_database(self):
        if self.active_project_path is not None:
            self.database_path = os.path.join(
                self.ccpem_projects.get_active_project().path,
                sqlite_project_database.CCPEMDatabase.ccpem_db_filename)
            try:
                self.database = sqlite_project_database.CCPEMDatabase(
                    database_path=self.database_path)
            except Exception:
                print "Error opening project database file " + self.database_path
                traceback.print_exc()
        else:
            self.database_path = None
            self.database = None

    def set_test_mode(self, test_mode):
        self.test_mode = test_mode
        if self.test_mode:
            self.test_button.setChecked(True)
        else:
            self.test_button.setChecked(False)
            if self.ccpem_projects.get_active_project_path() is not None:
                os.chdir(self.ccpem_projects.get_active_project_path())

    def add_button(self, name, tooltip, callback):
        '''Convenience function for adding a button to the task layout.'''
        button = QtGui.QPushButton(name, self)
        self.task_buttons_layout.addWidget(button)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        return button

    def add_task_button(self, name, task_wrapper):
        '''Convenience function for adding a task button.

        The task's short_info is used as the tooltip. If task_wrapper is None,
        the button is created in a disabled state.'''
        if task_wrapper is not None:
            def open_task_window():
                self.open_new_task_window(task_wrapper)

            button = self.add_button(name,
                                     task_wrapper.task.task_info.short_description,
                                     open_task_window)
        else:
            button = QtGui.QPushButton(name, self)
            self.task_buttons_layout.addWidget(button)
            button.setToolTip('Error: task unavailable. See "About" below for more details.')
            button.setDisabled(True)
        return button

    def set_task_buttons(self):
        '''
        Set all task launch buttons.
        '''
        self.task_buttons = QtGui.QWidget()
        self.task_buttons_layout = QtGui.QVBoxLayout()
        self.task_buttons.setLayout(self.task_buttons_layout)

        # CCPEM logo
        ccpem_logo = QtGui.QPixmap(icons.icon_utils.get_ccpem_icon())
        ccpem_button = QtGui.QPushButton()
        ccpem_button.setToolTip(
            'CCP-EM\n'
            'Collaborative Computational Project for Electron cryo-Microscopy')
        ccpem_icon = QtGui.QIcon(ccpem_logo)
        ccpem_button.setIcon(ccpem_icon)
        ccpem_button.setIconSize(ccpem_logo.rect().size())
        ccpem_button.clicked.connect(self.handle_ccpem_logo)
        self.task_buttons_layout.addWidget(ccpem_button)

        # Separator
        self.task_buttons_layout.addWidget(ccpem_widgets.CCPEMMenuSeparator())

        # Tasks
        self.add_task_button('AceDRG', self.tasks.acedrg)
        self.add_task_button('Buccaneer', self.tasks.buccaneer)
        self.add_task_button('Choyce', self.tasks.choyce)
        self.add_task_button('Confidence Maps', self.tasks.confidence_maps)
        self.add_button('Coot', 'Open Coot in the project directory', lambda: gui_process.run_coot(None))
        self.add_task_button('cryoEF', self.tasks.cryoEF)
        self.add_task_button('DockEM', self.tasks.dock_em)
        self.add_task_button('Flex-EM', self.tasks.flex_em)
        if self.args.alpha():
            self.add_task_button('Haruspex', self.tasks.haruspex)
        self.add_task_button('LAFTER', self.tasks.lafter)
        self.add_task_button('LocScale', self.tasks.loc_scale)
        self.add_task_button('Map Process', self.tasks.map_process)
        if self.args.alpha():
            self.add_task_button('Model2Map', self.tasks.model2map)
        self.add_task_button('Molrep', self.tasks.molrep)
        self.add_task_button('Model tools', self.tasks.model_tools)
        self.add_task_button('MRC to MTZ', self.tasks.mrc_to_mtz)
        self.add_task_button('MRC-Allspace', self.tasks.mrcallspacea)
        self.add_task_button('MRC-Tif', self.tasks.mrc2tif)
        self.add_task_button('Nautilus', self.tasks.nautilus)
        self.add_task_button('Privateer', self.tasks.privateer)
        self.add_task_button('ProSHADE', self.tasks.proshade)
        self.add_task_button('ProSMART', self.tasks.prosmart)
        self.add_task_button('Refmac5', self.tasks.refmac)
        self.add_button('RELION', 'Open RELION in a chosen project directory', self.handle_run_relion)
        self.add_task_button('Ribfind', self.tasks.ribfind)
        self.add_task_button('Shake', self.tasks.shake)
        self.add_task_button('SymmetryExpand', self.tasks.sym_expand)
        self.add_task_button('TEMPy: DiffMap', self.tasks.tempy_diff_map)
        self.add_task_button('TEMPy: Local score', self.tasks.tempy_smoc)
        self.add_task_button('TEMPy: Scores', self.tasks.tempy_scores)
        self.add_task_button('Validation: model', self.tasks.model_validation)
        self.add_task_button('FDR model validation', self.tasks.fdr_validation)

        # Separator
        self.task_buttons_layout.addWidget(ccpem_widgets.CCPEMMenuSeparator())

        ### Utilities
        self.add_button('Images', 'Image gallery', self.handle_run_images)
        self.add_button('MRC Header', 'MRC header viewer', self.handle_run_mrc_edit)
        self.add_button('relion_display', 'Run relion_display to view maps and images',
                             gui_process.run_relion_display)

        # Separator with stretch above
        self.task_buttons_layout.addStretch()
        self.task_buttons_layout.addWidget(ccpem_widgets.CCPEMMenuSeparator())

        ### Information

        # About button
        self.add_button('About', 'Information about CCP-EM setup', self.handle_about_button)

        # Test mode button
        self.test_button = self.add_button('Test mode', 'Test mode launches tasks with test parameters',
                                           self.handle_test_button)
        self.test_button.setCheckable(True)
        self.test_button.setChecked(True)
        self.test_button.setStyleSheet(
            'QPushButton:checked { background-color: lightgreen; }')

        # Set up scrolling
        self.task_scroll = QtGui.QScrollArea()
        self.task_scroll.setWidgetResizable(True) # Set to make the inner widget resize with scroll area
        self.task_scroll.setWidget(self.task_buttons)
        self.task_scroll.ensureWidgetVisible(ccpem_button)

    def handle_ccpem_logo(self):
        '''
        Launch ccpem website via system default browser.
        '''
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('http://www.ccpem.ac.uk/'))

    def handle_about_button(self):
        '''
        Launch CCP-EM settings display
        '''
        # Bugs etc
        info_str = '\nFeatures, bugs and requests please contact'
        info_str += '\nccpem@stfc.ac.uk\n'
        # CCP-EM source
        ccpem_src = os.path.dirname(ccpem_core.__file__)
        ccpem_src.replace('/src/ccpem_core', '')
        info_str += '\nCCP-EM source location\n{0}\n'.format(ccpem_src)

        # Python interpreter
        info_str += '\nccpem-python bin location\n{0}\n'.format(os.path.dirname(
            sys.executable))

        # CCP-EM Git version
        info_str += '\nCCP-EM version\n{0}\n'.format(
            self.version.version)
        info_str += '\nCCP-EM Git revision\n{0}\n'.format(
            self.version.git_revision)
        info_str += '\nCCP-EM build time\n{0}\n'.format(
            self.version.build_time)

        # CCP4 info
        try:
            ccp4_env = (os.environ['CCP4'])
        except KeyError:
            ccp4_env = None
        if ccp4_env is None:
            info_str += '\nCCP4\nNot available\n'
        else:
            info_str += '\nCCP4 path\n{0}\n'.format(
                ccp4_env)

        # Modeller info
        if modeller_available:
            info_str += '\nModeller version\n{0}\n'.format(
                modeller.info.version)
        else:
            info_str += '\nModeller\nNot available\n'
        info_str += '\nUser settings\n'
        info_str +=  self.args.output_args_as_text()

        # Task errors
        if self.tasks.errors:
            info_str += ('\nMissing tasks\n\nTasks are missing when all or '
                         'some part of the task pipeline is missing or can '
                         'not be found on your system.\n\n'
                         'For CCP4 programs (e.g. Buccaneer, Molrep, MRC to '
                         'MTZ, Refmac, ProSMART, Shake) please ensure CCP4 is '
                         'installed and correctly set up (CCP4 flag errors '
                         'indicated CCP4 is not sourced).\n\n'
                         'For Choyce and Flex-EM please ensure Modeller is '
                         'installed.\n\n'
                         'See below for list of missing tasks:\n')
            for task, error in self.tasks.errors.iteritems():
                info_str += '\n{0}: {1}'.format(task, error)

        # Info message box
        info_box = QtGui.QMessageBox(self)
        info_box.setWindowTitle('About CCP-EM')
        info_box.setText(info_str)
        info_box.addButton(QtGui.QPushButton('Edit'), QtGui.QMessageBox.YesRole)
        info_box.addButton(QtGui.QPushButton('Ok'), QtGui.QMessageBox.NoRole)
        info_box.setIconPixmap(QtGui.QPixmap(icons.icon_utils.get_ccpem_icon()))
        ret = info_box.exec_()
        if ret == 0:
            # Launch default editor to edit json settings
            path = self.args.location()
            url = QtCore.QUrl.fromLocalFile(QtCore.QString(path))
            QtGui.QDesktopServices.openUrl(url)

    def handle_test_button(self):
        test_mode = self.test_button.isChecked()
        self.set_test_mode(test_mode=test_mode)

    def open_new_task_window(self, task_wrapper):
        args_json = task_wrapper.window.gui_test_args if self.test_mode else None
        task = task_wrapper.task(parent=self, args_json=args_json, database_path=self.database_path)
        window = task_wrapper.window(parent=self, task=task)
        window.show()

    def handle_run_relion(self):
        '''
        Run relion GUI in a directory chosen by the user.
        '''
        relion_command = settings.which('relion')
        if relion_command is None:
            text = 'Warning: RELION not found'
            ccpem_utils.print_error(message=text)
        else:
            found_project = False
            project_dir = os.getcwd()
            # Slightly tricky logic here. Take care not to get stuck in an infinite loop!
            while not found_project:
                project_dir = QtGui.QFileDialog.getExistingDirectory(self, 'Choose RELION project directory',
                                                                     directory=project_dir)
                if len(project_dir) == 0:
                    # User selected 'Cancel'. Exit without running RELION.
                    return

                project_file = os.path.join(str(project_dir), '.gui_projectdir')
                if os.path.isfile(project_file):
                    # Already a RELION project. Break out of the loop and run RELION.
                    found_project = True
                else:
                    # Not an existing RELION project. Check if the user really means this directory.
                    create_new = QtGui.QMessageBox.question(self, 'Create new project?',
                                                            'There is no existing RELION project in this directory. '
                                                            'Do you want to create a new one?',
                                                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
                    if create_new == QtGui.QMessageBox.Ok:
                        # Create a new project indicator file, then break out of loop and run RELION.
                        open(project_file, 'w').close()
                        found_project = True
                    # else loop again to try a different directory
            gui_process.run_detatched_process(command=relion_command, args=[], cwd=project_dir)

    def handle_run_images(self):
        window = gallery_viewer.CCPEMGalleryWindow(parent=self)
        window.show()

    def handle_run_mrc_edit(self):
        window = mrc_edit_window.CCPEMMrcEditWindow(parent=self)
        window.show()

    def echo_main_window(self):
        '''
        For testing
        '''
        print ('CCP-EM Main Window')


class MainWindowProjectView(database_widget.CCPEMProjectTableView):
    def __init__(self, main_window):
        super(MainWindowProjectView, self).__init__(parent=main_window)
        self.main_window = main_window
        self.tasks = main_window.tasks

    def clone_custom(self, args_json):
        task_class = self.tasks.get_task_class(program=self.program)
        window_class = self.tasks.get_window_class(program=self.program)
        task = task_class(
            parent=self,
            args_json=args_json,
            database_path=self.main_window.database_path)
        window = window_class(
            parent=self,
            task=task)
        window.show()

    def on_click_custom(self, index, path):
        program_index = index.sibling(index.row(),
                                      self.model.fieldIndex('program'))
        program = str(self.model.data(program_index).toString())
        task_class = self.tasks.get_task_class(program=program)
        window_class = self.tasks.get_window_class(program=program)
        task_file = os.path.join(path, process_manager.task_filename)
        if task_class is not None and os.path.exists(task_file):
            window_utils.relaunch_task_window(
                task_class=task_class,
                window_class=window_class,
                task_file=task_file,
                main_window=self.main_window)
        else:
            message = 'No task found'
            QtGui.QMessageBox.warning(
                self,
                'CCP-EM warning',
                message)

class MainWindowProjectWidget(project_widget.CCPEMProjectsWidget):
    def __init__(self, main_window, ccpem_projects):
        self.main_window = main_window
        super(MainWindowProjectWidget, self).__init__(
            ccpem_projects=ccpem_projects,
            parent=main_window)

    def set_active_project_display(self):
        active_project = self.projects.get_active_project()
        if active_project is None:
            self.active_project_text = 'No active project: please add a project'
        else:
            self.active_project_text = '''Active project:
    User : {0}
    Name : {1}
    Path : {2}'''.format(active_project.user,
                         active_project.name,
                         active_project.path)
            self.active_project_button.setToolTip('Click to explore')
        self.active_project_button.setText(self.active_project_text)
        self.active_project_button.setStyleSheet("Text-align:left")
        # Update parent GUI
        if self.main_window is not None:
            self.main_window.set_active_project(
                active_project_path=self.projects.get_active_project_path())


def main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(icons.icon_utils.get_ccpem_icon()))
    args = settings.get_ccpem_settings()
    # Set styles
    if args.style.value == 'default':
        if sys.platform == 'linux' or sys.platform == 'linux2':
            args.style.value = 'plastique'
    app.setStyle(args.style.value)
    app.setStyleSheet('''QToolTip {background-color: black;
                                   color: white;
                                   border: black solid 1px
                                   }''')

    # Launch main GUI
    window = CCPEMMainWindow(args=args)
    window.show()
    window.set_tasks_projects()
    #
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
