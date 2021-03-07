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

        return data



            # for parent in tree.findall('PrivateerResult'):
            #     print(tree)
            #     for child in parent:
            #         pyranose_tree = 
            #     i_entries['FragBuilt'] = child.find('FragmentsBuilt')
            #     i_entries['ResBuilt'] = child.find('ResiduesBuilt')
            #     i_entries['ResSeq'] = child.find('ResiduesSequenced')
            #     i_entries['ResLongFrag'] = child.find(
            #         'ResiduesLongestFragment')
            # data.append(i_entries)
            # build_sec = 'built_sec'
            # build_table = 'built_table'
            # # set tabs and sections
            # pyrvapi.rvapi_add_tab(pipeline_tab, tab_name, True)
            # pyrvapi.rvapi_add_section(
            #     build_sec, 'Please reference', pipeline_tab, 0, 0, 1, 1, False)
            # reference_text = self.get_reference(process)
            # # add reference to cite found from logfile
            # r = 0
            # for i in range(0, len(reference_text)):
            #     pyrvapi.rvapi_add_text(str(i + 1) + ') ', build_sec, r, 0, 1, 1)
            #     for j in range(0, len(reference_text[i])):
            #         pyrvapi.rvapi_add_text(
            #             reference_text[i][j], build_sec, r, 1, 1, 1)
            #         r += 1
            # pyrvapi.rvapi_flush()
            # # set table headers
            # if process == 'Nautilus':
            #     pyrvapi.rvapi_add_table(
            #         build_table, 'Nautilus Build Summary', pipeline_tab, 1, 0, 1, 1, False)
            #     pyrvapi.rvapi_put_horz_theader(
            #         build_table, 'Run #', 'nth run of cnautilus', 0)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Fragments<br>built',
            #                                 'total number of fragments built', 1)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>built',
            #                                 'total number of residues built', 2)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>sequenced',
            #                                 'total number of residues sequenced', 3)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>in longest<br>fragment',
            #                                 'total number of residues in longest fragment', 4)
            # if process == 'Buccaneer':
            #     pyrvapi.rvapi_add_table(
            #         build_table, 'Buccaneer Build Summary', pipeline_tab, 1, 0, 1, 1, False)
            #     pyrvapi.rvapi_put_horz_theader(
            #         build_table, 'Run #', 'nth run of cbuccaneer', 0)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Completeness<br>by<br>residues<br>built (%)',
            #                                 '(Number of unique residues allocated to chain)/(Residues built)', 1)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Completeness<br>by<br>chains<br>built (%)',
            #                                 '(Number of unique residues allocated to chain)/(Total sequence length provided)', 2)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Chains<br>built',
            #                                 'total number of chains built', 3)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Fragments<br>built',
            #                                 'total number of fragments built', 4)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>built',
            #                                 'total number of residues built', 5)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>sequenced',
            #                                 'total number of residues sequenced', 6)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Unique<br>residues<br>allocated',
            #                                 'total number of unique residues allocated to chain', 7)
            #     pyrvapi.rvapi_put_horz_theader(build_table, 'Residues<br>in longest<br>fragment',
            #                                 'total number of residues in longest fragment', 8)
            # pyrvapi.rvapi_flush()
        

    def validation_summary_graphs(self,
                                process=None,
                                builddata=None,
                                pipeline_tab=None):
        '''
        Make conformational landscape for Pyranoses or Furanoses (in the same plot)
        Make <B-Factor> vs Real Space CC 
        '''
        # make graph widget
        graphWid1 = API.loggraph(pipeline_tab)
        brdata = API.graph_data(graphWid1, 'Build & Refinement Summary')
        dx = API.graph_dataset(brdata, 'Cycle', 'Cycle')
        dy3 = API.graph_dataset(brdata, 'Average FSC', 'y3', isint=False)
        # set different labels for Nautilus/Buccaneer
        if process == 'Nautilus':
            dy1 = API.graph_dataset(brdata, 'Residues build', 'y2')
            dy2 = API.graph_dataset(brdata, 'Residues sequenced', 'y2')
            y1col = 'ResBuilt'
            y2col = 'ResSeq'
            yaxlabel = 'Amount built'
        if process == 'Buccaneer':
            dy1 = API.graph_dataset(
                brdata, 'Completeness by residues', 'y1', isint=False)
            dy2 = API.graph_dataset(
                brdata, 'Completeness by chains', 'y2', isint=False)
            y1col = 'CompByRes'
            y2col = 'CompByChain'
            yaxlabel = 'Percentage (%)'
        xmax = len(builddata)
        # add data
        for i in range(0, xmax):
            dx.add_datum(i + 1)
            if process == 'Buccaneer':
                dy1.add_datum(float(builddata[i][y1col].text) * 100)
                dy2.add_datum(float(builddata[i][y2col].text) * 100)
            else:
                dy1.add_datum(int(builddata[i][y1col].text))
                dy2.add_datum(int(builddata[i][y2col].text))
            dy3.add_datum(
                float(refinedata[i].results_summary['FSC average'][1]) * 100)
        # make plot, same plot for Buccaneer(all %), separate for Nautilus
        plot1 = API.graph_plot(
            graphWid1, 'Completeness after each cycle', 'Cycle', yaxlabel)
        plot1.reset_xticks()
        for i in range(0, xmax, 1):
            plot1.add_xtick(i + 1, '%d' % (i + 1))
        dx_y1 = API.plot_line(plot1, brdata, dx, dy1)
        dx_y2 = API.plot_line(plot1, brdata, dx, dy2)
        if process == 'Buccaneer':
            dx_y3 = API.plot_line(plot1, brdata, dx, dy3)
        if process == 'Nautilus':
            plot2 = API.graph_plot(
                graphWid1, 'Average FSC after each cycle', 'Cycle', 'Percentage (%)')
            plot2.reset_xticks()
            for i in range(0, xmax, 1):
                plot2.add_xtick(i + 1, '%d' % (i + 1))
            dx_dy3 = API.plot_line(plot2, brdata, dx, dy3)
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
