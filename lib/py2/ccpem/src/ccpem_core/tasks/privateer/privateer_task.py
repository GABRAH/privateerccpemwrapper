#
#     Copyright (C) 2017 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.
#

import os
from ccpem_core.ccpem_utils import ccpem_argparser
from ccpem_core import process_manager
from ccpem_core.tasks import task_utils
from ccpem_core import settings
from ccpem_core.tasks.privateer import privateer_results

class Privateer(task_utils.CCPEMTask):
    '''
    CCPEM shake task.  Use PDBSET to shake structure to set RMSD.
    '''
    task_info = task_utils.CCPEMTaskInfo(
        name='Privateer',
        author='Agirre J',
        version='0.4',
        description=(
            'Privateers performs automated validation of carbohydrates '
            'in Glycoprotein models. \n'
            'Validation of geometry and composition. Measures carbohydrate fit to Electron Density map\n'
            'Supports re-refinement via Coot and Refmac5.'),
        short_description=(
            'Automated validation of glycosylation. Manual re-refinment support for Coot and Refmac5'),
        documentation_link='http://legacy.ccp4.ac.uk/html/privateer.html',
        references=None)

    commands = {'refmac': settings.which(program='refmac5'),
            'coot': settings.which(program='coot'),
            'privateer': settings.which('/home/harold/Dev/privateer_master/build/executable/./privateer')
            }

    def __init__ ( self,
                   database_path  = None,
                   args           = None,
                   args_json      = None,
                   pipeline       = None,
                   job_location   = None,
                   verbose        = False,
                   parent         = None):
        super ( Privateer, self).__init__ ( database_path    = database_path,
                                           args             = args,
                                           args_json        = args_json,
                                           pipeline         = pipeline,
                                           job_location     = job_location,
                                           verbose          = verbose,
                                           parent           = parent )

    def parser(self):
        parser = ccpem_argparser.ccpemArgParser()
        #
        parser.add_argument ( '-job_title',
                              '--job_title',
                              help            = 'Short description of job',
                              metavar         = 'Job title',
                              type            = str,
                              default         = None )
        #
        parser.add_argument ( '-input_model',
                              '--input_model',
                              help            = '',
                              type            = str,
                              metavar         = 'PDB structure',
                              nargs           = '*',
                              default         = None )

        parser.add_argument (   '-input_map',
                                '--input_map',
                                help            = 'Input map',
                                type            = str,
                                metavar         = 'Map',
                                default         = None )

        parser.add_argument (   '-resolution',
                                '--resolution',
                                help            = 'Resolution (Angstrom)',
                                metavar         = 'Resolution (Angstrom)',
                                type            = float,
                                default         = None )
        
        parser.add_argument (   '-glytoucan',
                                '--glytoucan',
                                help            = 'Validate glycan against GlyToucan and GlyConnect databases',
                                metavar         = 'Glycan composition validation',
                                type            = bool,
                                default         = True )
        
        parser.add_argument (   '-closestmatch',
                                '--closestmatch',
                                help            = 'Don\'t look for closest match on GlyConnect database if input glycan is not found',
                                metavar         = 'Closest match',
                                type            = bool,
                                default         = False )

        parser.add_argument (   '-allpermutations',
                                '--allpermutations',
                                help            = 'Generate all possible Glycan permutation combinations in looking for the closest match(should only be used for O-glycans as computationally very expensive)',
                                metavar         = 'All permutations',
                                type            = bool,
                                default         = False )

        parser.add_argument (   '-singlethreaded',
                                '--singlethreaded',
                                help            = 'Run Privateer in single threaded mode',
                                metavar         = 'Single Thread Mode',
                                type            = bool,
                                default         = False )

        parser.add_argument (   '-mask_radius',
                                '--mask_radius',
                                help            = 'Change the mask radius around the sugar atoms to _value_ Angstrom',
                                metavar         = 'Mask Radius (Angstrom)',
                                type            = float,
                                default         = 2.5 )

        parser.add_argument (   '-expression_system_mode',
                                '--expression_system_mode',
                                help            = 'Choose the expression system to validate against',
                                metavar         = 'Expression System',
                                choices         = [ 'undefined',
                                                    'bacterial',
                                                    'fungal',
                                                    'yeast',
                                                    'plant',
                                                    'insect',
                                                    'mammalian',
                                                    'human'],
                                type            = str,
                                default='undefined' )
        
        parser.add_argument (   '-undefinedsugar',
                                '--undefinedsugar',
                                help            = 'Custom sugar is present in input model file',
                                metavar         = 'Custom Sugar',
                                type            = bool,
                                default         = False )

        parser.add_argument (   '-input_code',
                                '--input_code',
                                help            = 'PDB three letter code',
                                type            = str,
                                metavar         = 'PDB Code',
                                default         = None )

        parser.add_argument (   '-input_anomer',
                                '--input_anomer',
                                help            = 'Choose the anomer of undefined sugar',
                                metavar         = 'Sugar Anomer',
                                choices         = [ 'alpha',
                                                    'beta'],
                                type            = str,
                                default='alpha' )
        
        parser.add_argument (   '-input_handedness',
                                '--input_handedness',
                                help            = 'Choose the handedness of undefined sugar',
                                metavar         = 'Sugar handedness',
                                choices         = [ '-D-',
                                                    '-L-'],
                                type            = str,
                                default='-D-' )

        parser.add_argument (   '-input_ring_conformation',
                                '--input_ring_conformation',
                                help            = 'Choose the Ring Type of undefined sugar',
                                metavar         = 'Sugar Ring Type',
                                choices         = [ 'pyranose',
                                                    'furanose'],
                                type            = str,
                                default='pyranose' )
        
        parser.add_argument (   '-input_conformation_pyranose',
                                '--input_conformation_pyranose',
                                help            = 'Choose the Expected Minimal energy ring conformation for input Pyranose',
                                metavar         = 'Expected Conformation for Pyranose',
                                choices         = [ '4c1',
                                                    '1c4',
                                                    '3Ob',
                                                    'b25',
                                                    '14b',
                                                    'b3O',
                                                    '25b',
                                                    'b14',
                                                    'Oev',
                                                    'ev5',
                                                    '4ev',
                                                    'ev3',
                                                    '2ev',
                                                    'ev1',
                                                    '3ev',
                                                    'ev2',
                                                    '1ev',
                                                    'evO',
                                                    '5ev',
                                                    'ev4',
                                                    'Oh5',
                                                    '4h5',
                                                    '4h3',
                                                    '2h3',
                                                    '2h1',
                                                    'Oh1',
                                                    '3h2',
                                                    '1h2',
                                                    '1hO',
                                                    '5hO',
                                                    '5h4',
                                                    '3h4',
                                                    'Os2',
                                                    '1s5',
                                                    '1s3',
                                                    '2sO',
                                                    '5s1',
                                                    '3s1'],
                                type            = str,
                                default='4c1' )

        parser.add_argument (   '-input_conformation_furanose',
                                '--input_conformation_furanose',
                                help            = 'Choose the Expected Minimal energy ring conformation for input Furanose',
                                metavar         = 'Expected Conformation for Furanose',
                                choices         = [ '3t2',
                                                    '3ev',
                                                    '3t4',
                                                    'ev4',
                                                    'Ot4',
                                                    'Oev',
                                                    'Ot1',
                                                    'ev1',
                                                    '2t1',
                                                    '2ev',
                                                    '2t3',
                                                    'ev3',
                                                    '4t3',
                                                    '4ev',
                                                    '4tO',
                                                    'evO',
                                                    '1tO',
                                                    '1ev',
                                                    '1t2',
                                                    'ev2'],
                                type            = str,
                                default='3t2' )

        parser.add_argument(    '-ring_oxygen',
                                '--ring_oxygen',
                                help=('Designate the atom code for anomeric Oxygen'),
                                type=str,
                                metavar='Ring Oxygen',
                                default='O5' )
        
        parser.add_argument(    '-ring_C1',
                                '--ring_C1',
                                help=('Designate the atom code for first Carbon'),
                                type=str,
                                metavar='Ring Carbon 1',
                                default='C1' )

        parser.add_argument(    '-ring_C2',
                                '--ring_C2',
                                help=('Designate the atom code for second Carbon, clockwise'),
                                type=str,
                                metavar='Ring Carbon 2',
                                default='C2' )

        parser.add_argument(    '-ring_C3',
                                '--ring_C3',
                                help=('Designate the atom code for third Carbon, clockwise'),
                                type=str,
                                metavar='Ring Carbon 3',
                                default='C3' )

        parser.add_argument(    '-ring_C4',
                                '--ring_C4',
                                help=('Designate the atom code for fourth Carbon, clockwise'),
                                type=str,
                                metavar='Ring Carbon 4',
                                default='C4' )

        parser.add_argument(    '-ring_C5',
                                '--ring_C5',
                                help=('Designate the atom code for fourth Carbon, clockwise'),
                                type=str,
                                metavar='Ring Carbon 5',
                                default='C5' )
        
        parser.add_argument (   '-diagram_style',
                                '--diagram_style',
                                help            = 'Choose the SNFG Diagram style',
                                metavar         = 'SNFG style',
                                choices         = [ 'GlycanBuilder',
                                                    'Old Privateer'],
                                type            = str,
                                default='GlycanBuilder' )

        parser.add_argument (   '-diagram_orientation',
                                '--diagram_orientation',
                                help            = 'Choose the SNFG Diagram orientation',
                                metavar         = 'SNFG orientation',
                                choices         = [ 'horizontal',
                                                    'vertical'],
                                type            = str,
                                default='horizontal' )

        parser.add_argument (   '-color_scheme',
                                '--color_scheme',
                                help            = 'Choose the SNFG Color Scheme',
                                metavar         = 'SNFG Color Scheme',
                                choices         = [ 'GlycanBuilder',
                                                    'Old Style'],
                                type            = str,
                                default='GlycanBuilder' )

        parser.add_argument (   '-color_scheme_outlines',
                                '--color_scheme_outlines',
                                help            = 'Choose the SNFG Color Scheme Outline',
                                metavar         = 'SNFG Color Scheme Outline',
                                choices         = [ 'black',
                                                    'white'],
                                type            = str,
                                default='black' )

        parser.add_argument(    '-ncpus',
                                '--ncpus',
                                help='Number of CPU threads for Privateer',
                                metavar='No. of Cores',
                                type=int,
                                default=None)
        
        parser.add_argument(    '-sleeptimer',
                                '--sleeptimer',
                                help='Set sleep timer value between parallel loops',
                                metavar='Sleep Timer',
                                type=int,
                                default=1)
        
        parser.add_argument(
            '-keywords',
            '--keywords',
            help='Keywords for advanced options. Select file or define text',
            type=str,
            metavar='Keywords',
            default='')
        
        return parser

    def run_pipeline ( self, job_id = None, db_inject = None ):
        '''
        Generate job classes and process.  Run=false for reloading.
        '''
        # Get data from multiple inputs
        
        # Get processes
        pr = PrivateerCLI ( name                        = self.task_info.name,
                           command                      = self.commands['privateer'],
                           prdatabase_path              = os.path.join(os.environ['CCPEM'], 'lib/data/privateer_database.json'),
                           job_location                 = self.job_location,
                           input_model                  = self.args.input_model( ),
                           input_map                    = self.args.input_map ( ),
                           resolution                   = self.args.resolution ( ),
                           glytoucan                    = self.args.glytoucan ( ),
                           closestmatch                 = self.args.closestmatch ( ),
                           allpermutations              = self.args.allpermutations ( ),
                           singlethreaded               = self.args.singlethreaded ( ),
                           mask_radius                  = self.args.mask_radius ( ),
                           expression_system_mode       = self.args.expression_system_mode ( ),
                           undefinedsugar               = self.args.undefinedsugar ( ),
                           input_code                   = self.args.input_code ( ),
                           input_anomer                 = self.args.input_anomer ( ),
                           input_handedness             = self.args.input_handedness( ),
                           input_ring_conformation      = self.args.input_ring_conformation ( ),
                           input_conformation_pyranose  = self.args.input_conformation_pyranose ( ),
                           input_conformation_furanose  = self.args.input_conformation_furanose ( ),
                           ring_oxygen                  = self.args.ring_oxygen ( ),
                           ring_C1                      = self.args.ring_C1 ( ),
                           ring_C2                      = self.args.ring_C2 ( ),
                           ring_C3                      = self.args.ring_C3 ( ),
                           ring_C4                      = self.args.ring_C4 ( ),
                           diagram_style                = self.args.diagram_style ( ),
                           diagram_orientation          = self.args.diagram_orientation ( ),
                           color_scheme                 = self.args.color_scheme ( ),
                           color_scheme_outlines        = self.args.color_scheme_outlines ( ),
                           ncpus                        = self.args.ncpus ( ),
                           sleeptimer                   = self.args.sleeptimer ( ) )
        pl = [[pr.process]]

        # custom_finish = PrivateerResultsOnFinish(
        #     job_location=self.job_location)

        # Run pipeline
        # os.chdir(self.job_location)
        self.pipeline = process_manager.CCPEMPipeline (
                        pipeline           = pl,
                        job_id             = job_id,
                        args_path          = self.args.jsonfile,
                        location           = self.job_location,
                        database_path      = self.database_path,
                        db_inject          = db_inject,
                        taskname           = self.task_info.name,
                        title              = self.args.job_title.value,
                        verbose            = self.verbose,
                        on_finish_custom   = None)
        self.pipeline.start()


class PrivateerCLI(object):
    '''
    Run Privateer via Command Line Interface
    '''
    def __init__ ( self,
                   name,
                   command,
                   prdatabase_path,
                   job_location,
                   input_model,
                   input_map,
                   resolution,
                   glytoucan,
                   closestmatch,
                   allpermutations,
                   singlethreaded,
                   mask_radius,
                   expression_system_mode,
                   undefinedsugar,
                   input_code,
                   input_anomer,
                   input_handedness,
                   input_ring_conformation,
                   input_conformation_pyranose,
                   input_conformation_furanose,
                   ring_oxygen,
                   ring_C1,
                   ring_C2,
                   ring_C3,
                   ring_C4,
                   diagram_style,
                   diagram_orientation,
                   color_scheme,
                   color_scheme_outlines,
                   ncpus,
                   sleeptimer ):
        self.command                        = command
        self.prdatabase_path                = prdatabase_path
        self.job_location                   = job_location
        self.input_model                    = input_model
        self.input_map                      = input_map
        self.resolution                     = resolution
        self.glytoucan                      = glytoucan
        self.closestmatch                   = closestmatch
        self.allpermutations                = allpermutations
        self.singlethreaded                 = singlethreaded
        self.mask_radius                    = mask_radius
        self.expression_system_mode         = expression_system_mode
        self.undefinedsugar                 = undefinedsugar
        self.input_code                     = input_code
        self.input_anomer                   = input_anomer
        self.input_handedness               = input_handedness
        self.input_ring_conformation        = input_ring_conformation
        self.input_conformation_pyranose    = input_conformation_pyranose
        self.input_conformation_furanose    = input_conformation_furanose
        self.ring_oxygen                    = ring_oxygen
        self.ring_C1                        = ring_C1
        self.ring_C2                        = ring_C2
        self.ring_C3                        = ring_C3
        self.ring_C4                        = ring_C4
        self.diagram_style                  = diagram_style
        self.diagram_orientation            = diagram_orientation
        self.color_scheme                   = color_scheme
        self.color_scheme_outlines          = color_scheme_outlines
        self.ncpus                          = ncpus
        self.sleeptimer                     = sleeptimer
       
        self.args                             = []
        self.set_args                         ()

        self.process = process_manager.CCPEMProcess (
                           name               = name,
                           command            = self.command,
                           args               = self.args,
                           location           = self.job_location,
                           stdin              = None )

    def set_args ( self ):
        self.args.append('-pdbin')
        self.args.append(self.input_model)

        self.args.append('-mapin')
        self.args.append(self.input_map)

        self.args.append('-resolution')
        self.args.append(self.resolution)

        self.args.append('-radiusin')
        self.args.append(self.mask_radius)

        if self.undefinedsugar:
            if self.input_ring_conformation == "pyranose":
                self.args.append                  ('-valstring')
                if self.input_code is not None:
                    self.args.append              (self.input_code)
                else:
                    text = 'No three letter code was provided for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_oxygen is not None:
                    self.args.append              (self.ring_oxygen)
                else:
                    text = 'Oxygen atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_C1 is not None:
                    self.args.append              (self.ring_C1)
                else:
                    text = 'C1 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_C2 is not None:
                    self.args.append              (self.ring_C2)
                else:
                    text = 'C2 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_C3 is not None:
                    self.args.append              (self.ring_C3)
                else:
                    text = 'C3 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_C4 is not None:
                    self.args.append              (self.ring_C4)
                else:
                    text = 'C4 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical     ( None, 'Error', text )
                    return False
                if self.ring_C5 is not None:
                    self.args.append              (self.ring_C5)
                else:
                    text = 'C5 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.input_anomer is not None:
                    if self.input_anomer == "alpha":
                        self.args.append              ('A')
                    elif self.input_anomer == "beta":
                        self.args.append              ('B')
                    else:
                        text = 'Can\'t distinguish input sugar\'s Anomer!'
                        QtGui.QMessageBox.critical        ( None, 'Error', text )
                        return False
                else:
                    text = 'Unknown sugar\'s Anomer was not designated!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.input_handedness is not None:
                    if self.input_handedness == "-D-":
                        self.args.append              ('D')
                    elif self.input_handedness == "-L-":
                        self.args.append              ('L')
                    else:
                        text = 'Can\'t distinguish input sugar\'s handedness!'
                        QtGui.QMessageBox.critical        ( None, 'Error', text )
                        return False
                else:
                    text = 'Unknown sugar\'s handedness was not designated!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.input_conformation_pyranose is not None:
                    self.args.append              (self.input_conformation_pyranose)
                else:
                    text = 'Unknown sugar\'s expected minimal energy conformation was not designated!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
            elif self.input_ring_conformation == "furanose":
                self.args.append                  ('-valstring')
                if self.input_code is not None:
                    self.args.append              (self.input_code)
                else:
                    text = 'No three letter code was provided for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_oxygen is not None:
                    self.args.append              (self.ring_oxygen)
                else:
                    text = 'Oxygen atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_C1 is not None:
                    self.args.append              (self.ring_C1)
                else:
                    text = 'C1 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_C2 is not None:
                    self.args.append              (self.ring_C2)
                else:
                    text = 'C2 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_C3 is not None:
                    self.args.append              (self.ring_C3)
                else:
                    text = 'C3 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.ring_C4 is not None:
                    self.args.append              (self.ring_C4)
                else:
                    text = 'C4 atom was not designated for undefined sugar!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.input_handedness is not None:
                    if self.input_handedness == "-D-":
                        self.args.append              ('D')
                    elif self.input_handedness == "-L-":
                        self.args.append              ('L')
                    else:
                        text = 'Can\'t distinguish input sugar\'s handedness!'
                        QtGui.QMessageBox.critical        ( None, 'Error', text )
                        return False
                else:
                    text = 'Unknown sugar\'s handedness was not designated!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False
                if self.input_conformation_furanose is not None:
                    self.args.append              (self.input_conformation_furanose)
                else:
                    text = 'Unknown sugar\'s expected minimal energy conformation was not designated!'
                    QtGui.QMessageBox.critical        ( None, 'Error', text )
                    return False 
            else:
                text = 'Unable to determine whether input sugar is a furanose or pyranose!'
                QtGui.QMessageBox.critical        ( None, 'Error', text )
                return False 
            if self.input_code is not None:
                self.args.append                  ('-codein')
                self.args.append                  (self.input_code)
            else:
                text = 'No three letter code was provided for undefined sugar!'
                QtGui.QMessageBox.critical        ( None, 'Error', text )
                return False

        if self.diagram_style:
            if self.diagram_style == "Old Privateer":
                self.args.append                  ('-oldstyle')

        if self.diagram_orientation:
            if self.diagram_orientation == "vertical":
                self.args.append                  ('-vertical')
        
        if self.color_scheme:
            if self.color_scheme == "Old Style":
                self.args.append                  ('-oldstyle')

        if self.color_scheme_outlines:
            if self.color_scheme == "white":
                self.args.append                  ('-invert')

        if self.expression_system_mode:
            self.args.append                  ('-expression')
            self.args.append                  (self.expression_system_mode)

        if self.glytoucan:
            self.args.append                  ( '-glytoucan' )
            if self.prdatabase_path is not None:
                self.args.append              ( '-databasein' )
                self.args.append              ( self.prdatabase_path )
            else:
                # Error message
                text = 'No path to privateer_database.json was provided!'
                QtGui.QMessageBox.critical        ( None, 'Error', text )
                return False
            if self.closestmatch:
                self.args.append                  ( '-closest_match_disable' )
            if self.allpermutations and not self.closestmatch:
                self.args.append                  ( '-all_permutations' )
        
        if self.singlethreaded:
            self.args.append                  ('-singlethreaded')
        
        if self.ncpus is not None and not self.singlethreaded:
            self.args.append                  ('-cores')
            self.args.append                  (self.ncpus)

        if self.sleeptimer and not self.singlethreaded:
            self.args.append                  ('-sleep_timer')
            self.args.append                  (self.sleeptimer)

# class PrivateerResultsOnFinish(process_manager.CCPEMPipelineCustomFinish):
#     '''
#     Generate RVAPI results on finish.
#     '''

#     def __init__(self,
#                  job_location):
#         super(PrivateerResultsOnFinish, self).__init__()
#         self.job_location = job_location

#     def on_finish(self, parent_pipeline=None, job_location=None):
#         # generate RVAPI report
#         results = privateer_results.PrivateerResultsViewer(
#             job_location=self.job_location)
        