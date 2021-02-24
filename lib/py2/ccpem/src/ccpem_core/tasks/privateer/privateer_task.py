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
from ccpem_core.tasks.refmac import refmac_task
from ccpem_core import settings

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
            'privateer': settings.which('privateer')
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

    # .././privateer -pdbin ../../../tests/test_data/6m15.pdb -mapin ../../../tests/test_data/6m15.map -resolution 2.38 -glytoucan ../../../src/privateer/database.json
    # Wrapper inspired by proshade

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
        
        parser.add_argument (   '-input_code',
                                '--input_code',
                                help            = 'PDB three letter code,
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
                                metavar='Oxygen',
                                default='O5' )
        
        parser.add_argument(    '-ring_C1',
                                '--ring_C1',
                                help=('Designate the atom code for first Carbon'),
                                type=str,
                                metavar='Carbon 1',
                                default='C1' )

        parser.add_argument(    '-ring_C2',
                                '--ring_C2',
                                help=('Designate the atom code for second Carbon, clockwise'),
                                type=str,
                                metavar='Carbon 2',
                                default='C2' )

        parser.add_argument(    '-ring_C3',
                                '--ring_C3',
                                help=('Designate the atom code for third Carbon, clockwise'),
                                type=str,
                                metavar='Carbon 3',
                                default='C3' )

        parser.add_argument(    '-ring_C4',
                                '--ring_C4',
                                help=('Designate the atom code for fourth Carbon, clockwise'),
                                type=str,
                                metavar='Carbon 4',
                                default='C4' )
        
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
                                metavar='CPU',
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

    def run_pipeline(self, job_id=None, db_inject=None):
        pl = []
        base = 'shaken_' + os.path.basename(self.args.input_pdb())
        self.pdbout_path = os.path.join(
            self.job_location,
            base)
        self.process_shake = refmac_task.PDBSetShake(
            name='Shake refined structure',
            job_location=self.job_location,
            pdb_path=self.args.input_pdb(),
            pdbout_path=self.pdbout_path)
        pl.append([self.process_shake.process])
        self.pipeline = process_manager.CCPEMPipeline(
            pipeline=pl,
            job_id=job_id,
            args_path=self.args.jsonfile,
            location=self.job_location,
            database_path=self.database_path,
            db_inject=db_inject,
            taskname=self.task_info.name,
            title=self.args.job_title.value)
        self.pipeline.start()

