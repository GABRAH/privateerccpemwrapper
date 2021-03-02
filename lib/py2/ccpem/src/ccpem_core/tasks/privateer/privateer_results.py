import sys
import re
import os
import time
import pyrvapi
import fileinput
import collections
import shutil
import numpy as np
import math
from lxml import etree
from ccpem_core import process_manager
from ccpem_core import ccpem_utils
from ccpem_core.ccpem_utils.ccp4_log_parser import smartie
from ccpem_core.data_model import metadata_utils
import pyrvapi_ext as API


class PipelineResultsViewer(object):
    # class ResultViewer(object):
    '''
    Get Privateer results from program.xml
    '''

    def __init__(self,
                 pipeline=None,
                 pipeline_path=None,
                 xmlfilename=None):
        if pipeline_path is not None:
            self.pipeline = process_manager.CCPEMPipeline(
                pipeline=None,
                import_json=pipeline_path)
        else:
            self.pipeline = pipeline
        self.privateer_process = None
        self.xmlfilename = []
        # setup doc
        ccp4 = os.environ['CCPEM']
        share_jsrview = os.path.join(ccp4, 'share', 'jsrview')
        self.directory = os.path.join(self.pipeline.location, 'report')
        self.index = os.path.join(self.directory, 'index.html')
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)
        ccpem_utils.check_directory_and_make(self.directory)

        xml_relpath = os.path.join(self.directory, 'output.xml')
        # setup pages
        pyrvapi.rvapi_init_document(self.pipeline.location, self.directory, self.pipeline.location,
                                    1, pyrvapi.RVAPI_LAYOUT_Tabs,
                                    share_jsrview, None, 'index.html', None, xml_relpath)
        pyrvapi.rvapi_add_header('Parsed output')
        pyrvapi.rvapi_flush()

        # get the process that ran
        for jobs in self.pipeline.pipeline:
            for job in jobs:
                if job.name == 'Privateer':
                    self.privateer_process = job

        # get xml file from Buccaneer/Nautilus
        if xmlfilename is not None:
            if isinstance(xmlfilename, str):
                self.xmlfilename.append(os.path.join(
                    self.pipeline.location, xmlfilename))
            else:
                self.xmlfilename = list.copy(xmlfilename)
        else:
            infile = 'program.xml'
            self.xmlfilename.append(os.path.join(
                        self.pipeline.location, infile))

        # set results table and graphs
        pipeline_tab = 'pipeline_tab'
        if self.privateer_process is not None:
            privateer_data = self.GetXML2Table('Privateer', pipeline_tab)
            self.buildref_summary_graph(
                'Privateer', build_data, refine_data, pipeline_tab)
        



    def GetXML2Table(self, process, pipeline_tab):
        '''
        Get data from XML output and fill table
        '''
        data = []
        tab_name = ''
        len(self.xmlfilename)
        for infile in self.xmlfilename:
            # print infile
            tree = etree.parse(infile)  # self.xmlfilename)
            i_entries = collections.OrderedDict()
            if process == 'Nautilus':
                tab_name = 'Nautilus Build Results'
                for child in tree.findall('Final'):
                    i_entries['FragBuilt'] = child.find('FragmentsBuilt')
                    i_entries['ResBuilt'] = child.find('ResiduesBuilt')
                    i_entries['ResSeq'] = child.find('ResiduesSequenced')
                    i_entries['ResLongFrag'] = child.find(
                        'ResiduesLongestFragment')
                data.append(i_entries)
            if process == 'Buccaneer':
                tab_name = 'Buccaneer Build Results'
                for child in tree.findall('Final'):
                    i_entries['CompByRes'] = child.find(
                        'CompletenessByResiduesBuilt')
                    i_entries['CompByChain'] = child.find(
                        'CompletenessByChainsBuilt')
                    i_entries['ChainsBuilt'] = child.find('ChainsBuilt')
                    i_entries['FragBuilt'] = child.find('FragmentsBuilt')
                    i_entries['ResBuilt'] = child.find('ResiduesBuilt')
                    i_entries['ResSeq'] = child.find('ResiduesSequenced')
                    i_entries['UniqRes'] = child.find('ResiduesUnique')
                    i_entries['ResLongFrag'] = child.find(
                        'ResiduesLongestFragment')
                data.append(i_entries)
        build_sec = 'built_sec'
        build_table = 'built_table'
        # set tabs and sections
        pyrvapi.rvapi_add_tab(pipeline_tab, tab_name, True)
        pyrvapi.rvapi_add_section(
            build_sec, 'Please reference', pipeline_tab, 0, 0, 1, 1, False)
        reference_text = self.get_reference(process)
        # add reference to cite found from logfile
        r = 0
        for i in range(0, len(reference_text)):
            pyrvapi.rvapi_add_text(str(i + 1) + ') ', build_sec, r, 0, 1, 1)
            for j in range(0, len(reference_text[i])):
                pyrvapi.rvapi_add_text(
                    reference_text[i][j], build_sec, r, 1, 1, 1)
                r += 1
        pyrvapi.rvapi_flush()
        # set table headers
        if process == 'Nautilus':
            pyrvapi.rvapi_add_table(
                build_table, 'Nautilus Build Summary', pipeline_tab, 1, 0, 1, 1, False)
            pyrvapi.rvapi_put_horz_theader(
                build_table, 'Run #', 'nth run of cnautilus', 0)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Fragments<br>built',
                                           'total number of fragments built', 1)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>built',
                                           'total number of residues built', 2)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>sequenced',
                                           'total number of residues sequenced', 3)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>in longest<br>fragment',
                                           'total number of residues in longest fragment', 4)
        if process == 'Buccaneer':
            pyrvapi.rvapi_add_table(
                build_table, 'Buccaneer Build Summary', pipeline_tab, 1, 0, 1, 1, False)
            pyrvapi.rvapi_put_horz_theader(
                build_table, 'Run #', 'nth run of cbuccaneer', 0)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Completeness<br>by<br>residues<br>built (%)',
                                           '(Number of unique residues allocated to chain)/(Residues built)', 1)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Completeness<br>by<br>chains<br>built (%)',
                                           '(Number of unique residues allocated to chain)/(Total sequence length provided)', 2)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Chains<br>built',
                                           'total number of chains built', 3)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Fragments<br>built',
                                           'total number of fragments built', 4)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>built',
                                           'total number of residues built', 5)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>sequenced',
                                           'total number of residues sequenced', 6)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Unique<br>residues<br>allocated',
                                           'total number of unique residues allocated to chain', 7)
            pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>in longest<br>fragment',
                                           'total number of residues in longest fragment', 8)
        pyrvapi.rvapi_flush()
        # fill table
        i = 0  # row
        for entries in data:
            j = 0  # column
            for name in entries:
                if j == 0:
                    pyrvapi.rvapi_put_table_string(
                        build_table, str(i + 1), i, j)  # fill in cycle number
                    j += 1  # %0.1f %
                    if name == 'CompByRes':
                        value = float(entries[name].text) * 100
                        pyrvapi.rvapi_put_table_string(
                            build_table, '%0.1f' % value, i, j)  # fill in % value
                    else:
                        pyrvapi.rvapi_put_table_string(
                            build_table, entries[name].text, i, j)  # fill in built values
                else:
                    if name == 'CompByChain':
                        value = float(entries[name].text) * 100
                        pyrvapi.rvapi_put_table_string(
                            build_table, '%0.1f' % value, i, j)  # fill in % value
                    else:
                        pyrvapi.rvapi_put_table_string(
                            build_table, entries[name].text, i, j)  # fill in built values
                j += 1
            i += 1
        pyrvapi.rvapi_flush()
        return data


def main(target_dir=None):
    from PyQt4 import QtGui, QtCore, QtWebKit
    if target_dir is None:
        pl_dir = '/home/harold/ccpem_project/Privateer_22'
    else:
        pl_dir = target_dir
    pipeline_path = pl_dir + '/task.ccpem'
    rvapi_dir = pl_dir + '/report'
    if os.path.exists(rvapi_dir):
        shutil.rmtree(rvapi_dir)

    # set up viewer
    app = QtGui.QApplication(sys.argv)
    web_window = QtWebKit.QWebView()
    web_window.show()

    ccpem_utils.check_directory_and_make(rvapi_dir)
    os.chdir(pl_dir)
    if os.path.exists(pipeline_path):
        rv = PipelineResultsViewer(pipeline_path=pipeline_path)
        web_window.load(QtCore.QUrl(rv.index))
        app.exec_()


if __name__ == '__main__':
    '''
    usage:
        ccpem-python nautilus_results.py <path_to_nautiluspipeline_stdout>
    or:
        ccpem-python -m ccpem_core.gui.tasks.nautilus.nautilus_results
            ./test_data/nautiluspipeline_stdout.txt
    '''
    if len(sys.argv) == 2:
        pl_dir = sys.argv[1]
        main(target_dir=pl_dir)
    else:
        main()
