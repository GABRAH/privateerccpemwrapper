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
                 job_location=None,
                 xmlfilename=None):

        self.job_location = job_location
        self.xmlfilename = xmlfilename
        # setup doc
        ccp4 = os.environ['CCPEM']
        share_jsrview = os.path.join(ccp4, 'share', 'jsrview')
        self.directory = os.path.join(self.job_location, 'report')
        self.index = os.path.join(self.directory, 'index.html')
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)
        ccpem_utils.check_directory_and_make(self.directory)

        # setup pages
        pyrvapi.rvapi_init_document(self.job_location, self.directory, self.job_location,
                                    1, 4,
                                    share_jsrview, None, 'index.html', None, None)

        pyrvapi.rvapi_flush()


        # get xml file from Buccaneer/Nautilus
        infile = 'program.xml'
        self.xmlfilename = os.path.join(self.job_location, infile)

        # set results table and graphs
        results_tab = 'results_tab'
        if self.job_location is not None:
            privateer_data = self.GetXML2Table('Privateer', results_tab)

            
    def get_reference(self, process):
        '''
        Get references to put in a section in results tab
        '''
        
        reference_list = ["\'Privateer: software for the conformational validation of carbohydrate structures.\' \nAgirre J, Iglesias-Fernandez J, Rovira C, Davies GJ, Wilson KS, Cowtan KD. (2014). \nNat Struct Mol Biol. 2015 Nov 4;22(11):833-4. doi: 10.1038/nsmb.3115."]
        return reference_list
    
    def GetXML2Table(self, process, results_tab):
        '''
        Get data from XML output and fill table
        '''

        data = collections.OrderedDict()
        tab_name = 'Results'
        tree = etree.parse(self.xmlfilename)  # self.xmlfilename)
        PrivateerResult = tree.find('PrivateerResult')
        ValidationData = PrivateerResult.find('ValidationData')
        pyranoses = ValidationData.findall("Pyranose")
        furanoses = ValidationData.findall("Furanse")
        if len(pyranoses):
            list_of_pyranoses = []
            for pyranose in pyranoses:
                i_pyranose_dict = collections.OrderedDict()
                i_pyranose_dict['Chain'] = pyranose.find('SugarChain')
                i_pyranose_dict['Name'] = pyranose.find('SugarName')
                i_pyranose_dict['Q'] = pyranose.find('SugarQ')
                i_pyranose_dict['Phi'] = pyranose.find('SugarPhi')
                i_pyranose_dict['Theta'] = pyranose.find('SugarTheta')
                i_pyranose_dict['Anomer'] = pyranose.find('SugarAnomer')
                i_pyranose_dict['Hand'] = pyranose.find('SugarHand')
                i_pyranose_dict['Conformation'] = pyranose.find('SugarConformation')
                i_pyranose_dict['RSCC'] = pyranose.find('SugarRSCC')
                i_pyranose_dict['BFactor'] = pyranose.find('SugarBFactor')
                i_pyranose_dict['Diagnostic'] = pyranose.find('SugarDiagnostic')
                list_of_pyranoses.append(i_pyranose_dict)
            data['Pyranoses'] = list_of_pyranoses
        if len(furanoses):
            list_of_furanoses = []
            for furanose in furanoses:
                i_furanose_dict = collections.OrderedDict()
                i_furanose_dict['Chain'] = furanose.find('SugarChain')
                i_furanose_dict['Name'] = furanose.find('SugarName')
                i_furanose_dict['Q'] = furanose.find('SugarQ')
                i_furanose_dict['Phi'] = furanose.find('SugarPhi')
                i_furanose_dict['Anomer'] = furanose.find('SugarAnomer')
                i_furanose_dict['Hand'] = furanose.find('SugarHand')
                i_furanose_dict['Conformation'] = furanose.find('SugarConformation')
                i_furanose_dict['RSCC'] = furanose.find('SugarRSCC')
                i_furanose_dict['BFactor'] = furanose.find('SugarBFactor')
                i_furanose_dict['Diagnostic'] = furanose.find('SugarDiagnostic')
                list_of_furanoses.append(i_furanose_dict)
            data['Furanoses'] = list_of_furanoses

        validation_sec = 'validation_sec'
        validation_table = 'validation_table'
        pyrvapi.rvapi_add_tab(results_tab, tab_name, True)
        # pyrvapi.rvapi_add_section(
        #     validation_sec, 'Please reference', results_tab, 0, 0, 1, 1, False)
        # reference_text = self.get_reference(process)
        # # add reference to cite found from logfile
        # r = 0
        # for i in range(0, len(reference_text)):
        #     pyrvapi.rvapi_add_text(str(i + 1) + ') ', validation_sec, r, 0, 1, 1)
        #     for j in range(0, len(reference_text[i])):
        #         pyrvapi.rvapi_add_text(
        #             reference_text[i][j], validation_sec, r, 1, 1, 1)
        #         r += 1
        pyrvapi.rvapi_flush()
        if "Pyranoses" in data:
            # set tabs and sections
            pyrvapi.rvapi_add_table(
                validation_table, 'Detailed validation data for Pyranoses', results_tab, 1, 0, 1, 1, False)
            pyrvapi.rvapi_put_horz_theader(
                validation_table, '#', 'nth sugar detected in the model', 0)
            pyrvapi.rvapi_put_horz_theader(
                validation_table, 'Chain', 'Protein backbone chain ID monosaccharide is a part of', 1)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Name',
                                        'Monosaccharide\'s PDB CCD code', 2)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Q',
                                        'Total puckering amplitude, measured in Angstroems', 3)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Phi',
                                        'Phi of monosaccharide', 4)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Theta',
                                        'Theta of monosaccharide', 5)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Anomer',
                                        'Anomer of monosaccharide', 6)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'D/L<sup>2</sup>',
                                        'Whenever N is displayed in the D/L column, it means that Privateer has been unable to determine the handedness based solely on the structure.', 7)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Conformation',
                                        'Conformation of the sugar.', 8)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'RSCC',
                                        'Real Space Correlation Coefficient.', 9)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'BFactor',
                                        'BFactor of monosaccharide.', 10)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Diagnosic',
                                        'Geometric quality of the monosaccharide.', 11)

            i = 0  # row
            for entries in data['Pyranoses']:
                j = 0  # column
                for name in entries:
                    if j == 0:
                        pyrvapi.rvapi_put_table_string(
                            validation_table, str(i + 1), i, j)  # fill in cycle number
                        j += 1  # %0.1f %
                        # if name == 'CompByRes':
                        #     value = float(entries[name].text) * 100
                        #     pyrvapi.rvapi_put_table_string(
                        #         validation_table, '%0.1f' % value, i, j)  # fill in % value
                        # else:
                        pyrvapi.rvapi_put_table_string(
                            validation_table, entries[name].text, i, j)  # fill in built values
                    else:
                    # if name == 'CompByChain':
                    #     value = float(entries[name].text) * 100
                    #     pyrvapi.rvapi_put_table_string(
                    #         validation_table, '%0.1f' % value, i, j)  # fill in % value
                    # else:
                        pyrvapi.rvapi_put_table_string(
                            validation_table, entries[name].text, i, j)  # fill in built values
                    j += 1
                i += 1
            pyrvapi.rvapi_flush()  
        if "Furanoses" in data:
            pyrvapi.rvapi_add_tab(validation_tab, tab_name, True)
            pyrvapi.rvapi_add_table(
                validation_table, 'Detailed validation data for Furanoses', results_tab, 1, 0, 1, 1, False)
            pyrvapi.rvapi_put_horz_theader(
                validation_table, '#', 'nth sugar detected in the model', 0)
            pyrvapi.rvapi_put_horz_theader(
                validation_table, 'Chain', 'Protein backbone chain ID monosaccharide is a part of', 1)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Name',
                                        'Monosaccharide\'s PDB CCD code', 2)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Q',
                                        'Total puckering amplitude, measured in Angstroems', 3)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Phi',
                                        'Phi of monosaccharide', 4)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Theta',
                                        'Theta of monosaccharide', 5)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Anomer',
                                        'Anomer of monosaccharide', 6)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'D/L<sup>2</sup>',
                                        'Whenever N is displayed in the D/L column, it means that Privateer has been unable to determine the handedness based solely on the structure.', 7)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Conformation',
                                        'Conformation of the sugar.', 8)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'RSCC',
                                        'Real Space Correlation Coefficient.', 9)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'BFactor',
                                        'BFactor of monosaccharide.', 10)
            pyrvapi.rvapi_put_horz_theader(validation_table, 'Diagnosic',
                                        'Geometric quality of the monosaccharide.', 11)
            
            i = 0  # row
            for entries in data['Pyranoses']:
                j = 0  # column
                for name in entries:
                    if j == 0:
                        pyrvapi.rvapi_put_table_string(
                            validation_table, str(i + 1), i, j)  # fill in cycle number
                        j += 1  # %0.1f %
                        pyrvapi.rvapi_put_table_string(
                            validation_table, entries[name].text, i, j)  # fill in built values
                    else:
                        pyrvapi.rvapi_put_table_string(
                            validation_table, entries[name].text, i, j)  # fill in built values
                    j += 1
                i += 1
            pyrvapi.rvapi_flush() 

        return data

    def validation_summary_graph(self,
                                validationdata=None,
                                results_tab=None):
        '''
        Make conformational landscape for Pyranoses or Furanoses (in the same plot)
        Make <B-Factor> vs Real Space CC 
        '''
        # make graph widget
        graphWid1 = API.loggraph(results_tab)
        brdata = API.graph_data(graphWid1, 'Summary of detected Pyranose Sugars')
        dx = API.graph
        
        API.flush()


def main(target_dir=None):
    from PyQt4 import QtGui, QtCore, QtWebKit
    if target_dir is None:
        pl_dir = '/home/harold/ccpem_project/Privateer_30' # with permutations
        # pl_dir = '/home/harold/ccpem_project/Privateer_22' # permutation-less
    else:
        pl_dir = target_dir
    # job_location = pl_dir + '/task.ccpem'
    job_location = pl_dir
    rvapi_dir = pl_dir + '/report'
    if os.path.exists(rvapi_dir):
        shutil.rmtree(rvapi_dir)

    # set up viewer
    app = QtGui.QApplication(sys.argv)
    web_window = QtWebKit.QWebView()
    web_window.show()

    ccpem_utils.check_directory_and_make(rvapi_dir)
    os.chdir(pl_dir)
    if os.path.exists(job_location):
        rv = PipelineResultsViewer(job_location=job_location)
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
