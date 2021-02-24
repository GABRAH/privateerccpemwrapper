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
        author='xxxx',
        version='xxxx',
        description=(
            '<p>Use PDBSET to shake structure to set RMSD.  '
            'N.B. requires CCP4.</p>'
            '<p>Full documentation:</p>'
            '<p>http://www.ccp4.ac.uk/html/pdbset.html</p>'),
        short_description=(
            'Shake structure.  Requires CCP4'),
        documentation_link='http://www.ccp4.ac.uk/html/pdbset.html',
        references=None)

    def __init__(self,
                 task_info=task_info,
                 database_path=None,
                 args=None,
                 args_json=None,
                 pipeline=None,
                 job_location=None,
                 parent=None):
        command = settings.which(program='pdbset')
        super(Privateer, self).__init__(command=command,
                                     task_info=task_info,
                                     database_path=database_path,
                                     args=args,
                                     args_json=args_json,
                                     pipeline=pipeline,
                                     job_location=job_location,
                                     parent=parent)
        self.pdbout_path = None

    def parser(self):
        parser = ccpem_argparser.ccpemArgParser()
        #
        parser.add_argument(
            '-job_title',
            '--job_title',
            help='Short description of job',
            metavar='Job title',
            type=str,
            default=None)
        #
        parser.add_argument(
            '-input_pdb',
            '--input_pdb',
            help='''Input coordinate file (pdb format)''',
            metavar='Input PDB',
            type=str,
            default=None)
        #
        parser.add_argument(
            '-shift',
            '--shift',
            help='''Maximum shift (Angstrom)''',
            metavar='Max shift',
            type=float,
            default=0.5)
        #
        parser.add_argument(
            '-keywords',
            '--keywords',
            help='Keywords for advanced options.  Select file or define text',
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

