#
#     Copyright (C) 2017 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

import os


class CCPEMTaskWrapper(object):
    '''
    Wrapper to link a CCPEMTask instance and a CCPEMTaskWindow instance.
    '''
    # TODO: can this be removed? The TaskWindow is always tightly coupled to the Task type, so we could have the
    # TaskWindow class keep a reference to the Task class, and the TaskWindow instance could perhaps hold a reference
    # to the Task instance itself? This last part might be trickier if the window ever needs to change the task instance
    # that it's linked to.
    def __init__(self,
                 name,
                 task,
                 window,
                 test_data=None):
        self.name = name
        self.task = task
        self.window = window
        self.check_commands()

    def check_commands(self):
        '''
        Check all commands can be found (e.g. refmac wrapper can find refmac5
        binary
        '''
        missing_commands = []
        for key, value in self.task.commands.iteritems():
            if value is None:
                missing_commands.append(key)
        if len(missing_commands) > 0:
            raise AssertionError('Required commands not found for {0} task: {1}'
                                 .format(self.name, ' '.join(missing_commands)))


class CCPEMTasks(object):
    '''
    Class of Tasks.  Relates program name to task function.
    '''
    def __init__(self, alpha=False):
        '''
        Set up task dictionary
        '''
        self.errors = {}

        # Check ccp4 flags
        ccp4_flag_errors = self.check_ccp4_environment()
        if ccp4_flag_errors is not None:
            self.errors['CCP4 flags'] = ccp4_flag_errors

        # AceDRG
        self.acedrg = None
        try:
            from ccpem_core.tasks.acedrg import acedrg_task
            from ccpem_gui.tasks.acedrg import acedrg_window
            self.acedrg = CCPEMTaskWrapper(
                name=acedrg_task.AcedrgTask.task_info.name,
                task=acedrg_task.AcedrgTask,
                window=acedrg_window.AcedrgWindow)
        except Exception as e:
            self.errors['AceDRG'] = e

        # Buccaneer
        self.buccaneer = None
        try:
            from ccpem_core.tasks.buccaneer import buccaneer_task
            from ccpem_gui.tasks.buccaneer import buccaneer_window
            self.buccaneer = CCPEMTaskWrapper(
                name=buccaneer_task.Buccaneer.task_info.name,
                task=buccaneer_task.Buccaneer,
                window=buccaneer_window.BuccaneerWindow)
        except Exception as e:
            self.errors['Buccaneer'] = e

        # Choyce
        self.choyce = None
        try:
            import modeller  # @UnusedImport
            from ccpem_core.tasks.choyce import choyce_task
            from ccpem_gui.tasks.choyce import choyce_window
            self.choyce = CCPEMTaskWrapper(
                name=choyce_task.Choyce.task_info.name,
                task=choyce_task.Choyce,
                window=choyce_window.ChoyceWindow)
        except Exception as e:
            self.errors['Choyce'] = e

        # Confidence Maps
        self.confidence_maps = None
        try:
            from ccpem_core.tasks.confidence_maps import confidence_maps_task
            from ccpem_gui.tasks.confidence_maps import confidence_maps_window
            self.confidence_maps = CCPEMTaskWrapper(
                name=confidence_maps_task.ConfidenceMapsTask.task_info.name,
                task=confidence_maps_task.ConfidenceMapsTask,
                window=confidence_maps_window.ConfidenceMapsWindow)
        except Exception as e:
            self.errors['Confidence Maps'] = e

        # cryoEF
        self.cryoEF = None
        try:
            from ccpem_core.tasks.cryoEF import cryoEF_task
            from ccpem_gui.tasks.cryoEF import cryoEF_window
            self.cryoEF = CCPEMTaskWrapper(
                name=cryoEF_task.cryoEF.task_info.name,
                task=cryoEF_task.cryoEF,
                window=cryoEF_window.cryoEFWindow)
        except Exception as e:
            self.errors['cryoEF'] = e

        # Dock-EM
        self.dock_em = None
        try:
            from ccpem_core.tasks.dock_em import dock_em_task
            from ccpem_gui.tasks.dock_em import dock_em_window
            self.dock_em = CCPEMTaskWrapper(
                name=dock_em_task.DockEM.task_info.name,
                task=dock_em_task.DockEM,
                window=dock_em_window.DockEMMainWindow)
        except Exception as e:
            self.errors['Dock EM'] = e

        # Flex-EM
        self.flex_em = None
        try:
            import modeller  # @UnusedImport @Reimport
            from ccpem_core.tasks.flex_em import flexem_task
            from ccpem_gui.tasks.flex_em import flexem_window
            self.flex_em = CCPEMTaskWrapper(
                name=flexem_task.FlexEM.task_info.name,
                task=flexem_task.FlexEM,
                window=flexem_window.FlexEMWindow)
        except Exception as e:
            self.errors['Flex-EM'] = e

        # Haruspex
        if alpha:
            self.haruspex = None
            try:
                from ccpem_core.tasks.haruspex import haruspex_task
                from ccpem_gui.tasks.haruspex import haruspex_window
                self.haruspex = CCPEMTaskWrapper(
                    name=haruspex_task.Haruspex.task_info.name,
                    task=haruspex_task.Haruspex,
                    window=haruspex_window.HaruspexWindow)
            except Exception as e:
                self.errors['Haruspex'] = e

        # LAFTER
        self.lafter = None
        try:
            from ccpem_core.tasks.lafter import lafter_task
            from ccpem_gui.tasks.lafter import lafter_window
            self.lafter = CCPEMTaskWrapper(
                name=lafter_task.LafterTask.task_info.name,
                task=lafter_task.LafterTask,
                window=lafter_window.LafterWindow)
        except Exception as e:
            self.errors['LAFTER'] = e

        # LocScale
        self.loc_scale = None
        try:
            from ccpem_core.tasks.loc_scale_interface import loc_scale_task
            from ccpem_gui.tasks.loc_scale_interface import loc_scale_window
            self.loc_scale = CCPEMTaskWrapper(
                name=loc_scale_task.LocScale.task_info.name,
                task=loc_scale_task.LocScale,
                window=loc_scale_window.LocScaleWindow)
        except Exception as e:
            self.errors['LocScale'] = e

        #Model2Map
        if alpha:
            self.model2map = None
            try:
                from ccpem_core.tasks.model2map import model2map_task
                from ccpem_gui.tasks.model2map import model2map_window
                self.model2map = CCPEMTaskWrapper(
                    name=model2map_task.Model2Map.task_info.name,
                    task=model2map_task.Model2Map,
                    window=model2map_window.Model2MapWindow)
            except Exception as e:
                self.errors['Model2Map'] = e

        # MapProcess
        self.map_process = None
        try:
            from ccpem_core.tasks.map_process import mapprocess_task
            from ccpem_gui.tasks.map_process import mapprocess_window
            self.map_process = CCPEMTaskWrapper(
                name=mapprocess_task.MapProcess.task_info.name,
                task=mapprocess_task.MapProcess,
                window=mapprocess_window.MapProcessWindow)
        except Exception as e:
            self.errors['MapProcess'] = e

        # Molrep
        self.molrep = None
        try:
            from ccpem_core.tasks.molrep import molrep_task
            from ccpem_gui.tasks.molrep import molrep_window
            self.molrep = CCPEMTaskWrapper(
                name=molrep_task.MolRep.task_info.name,
                task=molrep_task.MolRep,
                window=molrep_window.MolrepWindow)
        except Exception as e:
            self.errors['Molrep'] = e

        # Model tools
        self.model_tools = None
        try:
            from ccpem_core.tasks.model_tools import model_tools_task
            from ccpem_gui.tasks.model_tools import model_tools_window
            self.model_tools = CCPEMTaskWrapper(
                name=model_tools_task.ModelTools.task_info.name,
                task=model_tools_task.ModelTools,
                window=model_tools_window.ModelToolsWindow)
        except Exception as e:
            self.errors['Model Tools'] = e

        # MRC to MTZ
        self.mrc_to_mtz = None
        try:
            from ccpem_core.tasks.mrc_to_mtz import mrc_to_mtz_task
            from ccpem_gui.tasks.mrc_to_mtz import mrc_to_mtz_window
            self.mrc_to_mtz = CCPEMTaskWrapper(
                name=mrc_to_mtz_task.MrcToMtz.task_info.name,
                task=mrc_to_mtz_task.MrcToMtz,
                window=mrc_to_mtz_window.MrcToMtzWindow)
        except Exception as e:
            self.errors['MRC to MTZ'] = e

        # MRC to tif
        self.mrc2tif = None
        try:
            from ccpem_core.tasks.mrc_mrc2tif import mrc_mrc2tif_task
            from ccpem_gui.tasks.mrc_mrc2tif import mrc_mrc2tif_window
            self.mrc2tif = CCPEMTaskWrapper(
                name=mrc_mrc2tif_task.Mrc2Tif.task_info.name,
                task=mrc_mrc2tif_task.Mrc2Tif,
                window=mrc_mrc2tif_window.Mrc2TifWindow)
        except Exception as e:
            self.errors['MRC2TIF'] = e

        # MRC Allspacea
        self.mrcallspacea = None
        try:
            from ccpem_core.tasks.mrc_allspacea import mrc_allspacea_task

#             if mrc_allspacea_task.MrcAllspacea.commands:
#                 message = mrc_allspacea_task.MrcAllspacea.task_info.name + ' command not found: '
#                 for command in mrc_allspacea_task.MrcAllspacea.commands:
#                     message += command
#                 raise AssertionError(message)

            from ccpem_gui.tasks.mrc_allspacea import mrc_allspacea_window
            self.mrcallspacea = CCPEMTaskWrapper(
                name=mrc_allspacea_task.MrcAllspacea.task_info.name,
                task=mrc_allspacea_task.MrcAllspacea,
                window=mrc_allspacea_window.MrcAllspaceaWindow)
        except Exception as e:
            self.errors['MRCAllspacea '] = e

        # Nautilus
        self.nautilus = None
        try:
            from ccpem_core.tasks.nautilus import nautilus_task
            from ccpem_gui.tasks.nautilus import nautilus_window
            self.nautilus = CCPEMTaskWrapper(
                name=nautilus_task.Nautilus.task_info.name,
                task=nautilus_task.Nautilus,
                window=nautilus_window.NautilusWindow)
        except Exception as e:
            self.errors['Nautilus'] = e

        # Privateer
        self.privateer = None
        try:
            from ccpem_core.tasks.privateer import privateer_task
            from ccpem_gui.tasks.privateer import privateer_window
            self.privateer = CCPEMTaskWrapper(
                name=privateer_task.Privateer.task_info.name,
                task=privateer_task.Privateer,
                window=privateer_window.PrivateerWindow)
        except Exception as e:
            self.errors['Privateer'] = e

        # ProSMART
        self.prosmart = None
        try:
            from ccpem_core.tasks.prosmart import prosmart_task
            from ccpem_gui.tasks.prosmart import prosmart_window
            self.prosmart = CCPEMTaskWrapper(
                name=prosmart_task.ProSMART.task_info.name,
                task=prosmart_task.ProSMART,
                window=prosmart_window.ProSMARTWindow)
        except Exception as e:
            self.errors['Prosmart'] = e

        # Refmac
        self.refmac = None
        try:
            from ccpem_core.tasks.refmac import refmac_task
            from ccpem_gui.tasks.refmac import refmac_window
            self.refmac = CCPEMTaskWrapper(
                name=refmac_task.Refmac.task_info.name,
                task=refmac_task.Refmac,
                window=refmac_window.Refmac5Window)
        except Exception as e:
            self.errors['Refmac'] = e

        # SymExpand
        self.sym_expand = None
        try:
            from ccpem_core.tasks.sym_expand import sym_expand_task
            from ccpem_gui.tasks.sym_expand import sym_expand_window
            self.sym_expand = CCPEMTaskWrapper(
                name=sym_expand_task.SymExpand.task_info.name,
                task=sym_expand_task.SymExpand,
                window=sym_expand_window.SymExpandWindow)
        except Exception as e:
            self.errors['SymExpand'] = e

        # Ribfind
        self.ribfind = None
        try:
            from ccpem_core.tasks.ribfind import ribfind_task
            from ccpem_gui.tasks.ribfind import ribfind_window
            self.ribfind = CCPEMTaskWrapper(
                name=ribfind_task.Ribfind.task_info.name,
                task=ribfind_task.Ribfind,
                window=ribfind_window.RibfindWindow)
        except Exception as e:
            self.errors['Ribfind'] = e

        # Shake
        self.shake = None
        try:
            from ccpem_core.tasks.shake import shake_task
            from ccpem_gui.tasks.shake import shake_window
            self.shake = CCPEMTaskWrapper(
                name=shake_task.Shake.task_info.name,
                task=shake_task.Shake,
                window=shake_window.ShakeWindow)
        except Exception as e:
            self.errors['Shake'] = e

        # Tempy Diff Map
        self.tempy_diff_map = None
        try:
            from ccpem_core.tasks.tempy.difference_map import difference_map_task
            from ccpem_gui.tasks.tempy.difference_map import difference_map_window
            self.tempy_diff_map = CCPEMTaskWrapper(
                name=difference_map_task.DifferenceMap.task_info.name,
                task=difference_map_task.DifferenceMap,
                window=difference_map_window.DifferenceMapWindow)
        except Exception as e:
            self.errors['TEMPy Diff Map'] = e

        # Tempy SMOC
        self.tempy_smoc = None
        try:
            from ccpem_core.tasks.tempy.smoc import smoc_task
            from ccpem_gui.tasks.tempy.smoc import smoc_window
            self.tempy_smoc = CCPEMTaskWrapper(
                name=smoc_task.SMOC.task_info.name,
                task=smoc_task.SMOC,
                window=smoc_window.SMOCMapWindow)
        except Exception as e:
            self.errors['TEMPy SMOC'] = e

        # Tempy Scores
        self.tempy_scores = None
        try:
            from ccpem_core.tasks.tempy.scores import scores_task
            from ccpem_gui.tasks.tempy.scores import scores_window
            self.tempy_scores = CCPEMTaskWrapper(
                name=scores_task.GlobScore.task_info.name,
                task=scores_task.GlobScore,
                window=scores_window.GlobScoreWindow)
        except Exception as e:
            self.errors['TEMPy GlobScore'] = e
        # Tempy SCCC
        self.tempy_sccc = None
        try:
            from ccpem_core.tasks.tempy.sccc import sccc_task
            from ccpem_gui.tasks.tempy.sccc import sccc_window
            self.tempy_sccc = CCPEMTaskWrapper(
                name=sccc_task.SCCC.task_info.name,
                task=sccc_task.SCCC,
                window=sccc_window.SCCCMapWindow)
        except Exception as e:
            self.errors['TEMPy SCCC'] = e

        # Model validation
        self.model_validation = None
        try:
            from ccpem_core.tasks.atomic_model_validation import validate_task
            from ccpem_gui.tasks.atomic_model_validation import validate_window
            self.model_validation = CCPEMTaskWrapper(
                name=validate_task.ValidateTask.task_info.name,
                task=validate_task.ValidateTask,
                window=validate_window.ValidateWindow)
        except Exception as e:
            self.errors['Model_validation'] = e

        # ProShade
        self.proshade = None
        try:
            from ccpem_core.tasks.proshade import proshade_task
            from ccpem_gui.tasks.proshade import proshade_window
            self.proshade = CCPEMTaskWrapper(
                name=proshade_task.ProShade.task_info.name,
                task=proshade_task.ProShade,
                window=proshade_window.ProShadeWindow )
        except Exception as e:
            self.errors['ProShade'] = e

        # ProShade CHANGE TO FDR
        self.fdr_validation = None
        try:
            from ccpem_core.tasks.fdr_validation import fdr_validation_task
            from ccpem_gui.tasks.fdr_validation import fdr_validation_window
            self.fdr_validation = CCPEMTaskWrapper(
                name=fdr_validation_task.FDRValidationTask.task_info.name,
                task=fdr_validation_task.FDRValidationTask,
                window=fdr_validation_window.FDRValidationWindow )
        except Exception as e:
            self.errors['FDR-validation'] = e

    def get_task_class(self, program):
        '''
        Return task class from program name.
        '''
        for task in self.__dict__.values():
            if isinstance(task, CCPEMTaskWrapper):
                if task.name == program:
                    return task.task
        return None

    def get_window_class(self, program):
        '''
        Return window class from program name.
        '''
        for task in self.__dict__.values():
            if isinstance(task, CCPEMTaskWrapper):
                if task.name == program:
                    return task.window
        return None

    def check_ccp4_environment(self):
        '''
        Check appropriate environment variables are set
        '''
        # Not exhaustive list of ccp4 flags; just those needed for ccp4
        # programs called by ccp-em
        ccp4_flags = ['CCP4', 'CCP4_MASTER', 'CBIN', 'CLIB', 'CLIBD_MON']
        missing_flags = []
        for flag in ccp4_flags:
            try:
                os.environ[flag]
            except KeyError:
                missing_flags.append(flag)
        if len(missing_flags) > 0:
            return 'CCP4 flags not set : {0}'.format(' '.join(missing_flags))
        else:
            return None
