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
from ccpem_core import ccpem_utils
from ccpem_core.ccpem_utils.ccp4_log_parser import smartie
from ccpem_core.data_model import metadata_utils
import pyrvapi_ext as API


# Resolution label (equivalent to <4SSQ/LL>
ang_min_one = (ur'Resolution (\u00c5-\u00B9)').encode('utf-8')
angstrom_label = (ur'Resolution (\u00c5)').encode('utf-8')

class PrivateerResultsViewer(object):
    '''
    Privateer results viewer for RVAPI
        refine_process = which program in concatenated log file corresponds
            to privateer refinement process
    '''
    def __init__(self,
                 job_location='',
                 xmlfilename=None):
        self.job_location = job_location
        self.xmlfilename = []
        self.directory = os.path.join(self.job_location,
                                      'report')
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)
        ccpem_utils.check_directory_and_make(self.directory)
        self.index = os.path.join(self.directory, 'index.html')
        # XXX debug
        ccp4 = os.environ['CCPEM']
        share_jsrview = os.path.join(ccp4, 'share', 'jsrview')
        # Setup pages

        if xmlfilename is not None:
            if isinstance(xmlfilename, str):
                self.xmlfilename.append(os.path.join(
                    self.job_location, xmlfilename))
            else:
                self.xmlfilename = list.copy(xmlfilename)
        else:
            infile = 'program.xml'
            self.xmlfilename.append(os.path.join(
                        self.job_location, infile))

        pyrvapi.rvapi_init_document(
            self.job_location, self.directory,
            self.job_location, 1, 4, share_jsrview,
            None, 'index.html', None, None)
        pyrvapi.rvapi_flush()

        # Set results
        self.set_results()

    @staticmethod
    def fix_privateer_fsc_table(stdout):
        '''
        Fix missing column headings for fsc table
        '''
        error_line = ' 2sin(th)/l 2sin(th)/l NREF sigma  FSC FSCT PHdiff cos(PHdiff) sigmaSig ZZ TT co\n'
        fixed_line = ' 2sin(th)/l 2sin(th)/l NREF sigma  FSC FSCT PHdiff cos(PHdiff) sigmaSig ZZ TT cor(|F1|,|F2|) $$'
        ignore_line = ' r(|F1|,|F2|) $$\n'
        #
        for line in fileinput.input(stdout, inplace=True):
            if line == error_line:
                print fixed_line,
            elif line == ignore_line:
                pass
            else:
                print line,
        fileinput.close()

    def set_results(self):
        data = collections.OrderedDict()
        tab_name = ''
        len(self.xmlfilename)
        for infile in self.xmlfilename:
            # print infile
            tree = etree.parse(infile)  # self.xmlfilename)
            PrivateerResult = tree.find('PrivateerResult')
            ValidationData = PrivateerResult.find('ValidationData')
            pyranoses = ValidationData.findall("Pyranose")
            furanoses = ValidationData.findall("Furanse")
            tab_name = 'Detailed monosaccharide validation data'
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
            
            pyrvapi.rvapi_add_tab(pipeline_tab, tab_name, True)
            if "Pyranoses" in data:
                build_table = 'built_table'
                # set tabs and sections
                pyrvapi.rvapi_add_table(
                    build_table, 'Validation results for pyranose sugars:', pipeline_tab, 1, 0, 1, 1, False)
                pyrvapi.rvapi_put_horz_theader(
                    build_table, 'Chain', 'Protein backbone chain ID monosaccharide is a part of', 0)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Name',
                                            'Monosaccharide\'s PDB CCD code', 1)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Q',
                                            'Total puckering amplitude, measured in Angstroems', 2)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Phi',
                                            'Phi of monosaccharide', 3)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Theta',
                                            'Theta of monosaccharide', 4)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Anomer',
                                            'Anomer of monosaccharide', 5)
                pyrvapi.rvapi_put_horz_theader(build_table, 'D/L<sup>2</sup>',
                                            'Whenever N is displayed in the D/L column, it means that Privateer has been unable to determine the handedness based solely on the structure.', 6)
                pyrvapi.rvapi_put_horz_theader(build_table, 'RSCC',
                                            'Real Space Correlation Coefficient.', 7)
                pyrvapi.rvapi_put_horz_theader(build_table, '<BFactor>',
                                            'BFactor of monosaccharide.', 8)
                pyrvapi.rvapi_put_horz_theader(build_table, '<Diagnosic>',
                                            'Geometric quality of the monosaccharide.', 9)                                 
            if "Furanoses" in data:
                build_table = 'built_table'
                pyrvapi.rvapi_add_tab(pipeline_tab, tab_name, True)
                pyrvapi.rvapi_add_table(
                    build_table, 'Validation results for furanose sugars:', pipeline_tab, 1, 0, 1, 1, False)
                pyrvapi.rvapi_put_horz_theader(
                    build_table, 'Chain', 'Protein backbone chain ID monosaccharide is a part of', 0)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Name',
                                            'Monosaccharide\'s PDB CCD code', 1)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Q',
                                            'Total puckering amplitude, measured in Angstroems', 2)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Phi',
                                            'Phi of monosaccharide', 3)
                pyrvapi.rvapi_put_horz_theader(build_table, 'Anomer',
                                            'Anomer of monosaccharide', 4)
                pyrvapi.rvapi_put_horz_theader(build_table, 'D/L<sup>2</sup>',
                                            'Whenever N is displayed in the D/L column, it means that Privateer has been unable to determine the handedness based solely on the structure.', 5)
                pyrvapi.rvapi_put_horz_theader(build_table, 'RSCC',
                                            'Real Space Correlation Coefficient.', 6)
                pyrvapi.rvapi_put_horz_theader(build_table, '<BFactor>',
                                            'BFactor of monosaccharide.', 7)
                pyrvapi.rvapi_put_horz_theader(build_table, '<Diagnosic>',
                                            'Geometric quality of the monosaccharide.', 8)

        # # DaC mode
        # if os.path.exists(self.dac_stdout):
        #     self.dac_results = dacParser(
        #         stdout=self.dac_stdout)
        #     self.set_refine_results_summary()
        #     return
        # else:
        #     self.dac_results = None

        # # Get mrc2mtz results (power spectrum)
        # if os.path.exists(self.mrc2mtz_stdout):
        #     self.mrc2mtz_results = PrivateerPowerSpectrumParser(
        #         stdout=self.mrc2mtz_stdout)
        # else:
        #     self.mrc2mtz_results = None

        # # Get refinement results
        # if os.path.exists(self.refine_stdout):
        #     self.refine_results = PrivateerRefineResultsParser(
        #         stdout=self.refine_stdout)
        #     if self.refine_results.refine_results is not None:
        #         self.set_refine_results_summary()

        # Get validation results
        # validate_processes = [os.path.exists(self.validate_hm1_stdout),
        #                       os.path.exists(self.validate_hm2_stdout),
        #                       os.path.exists(self.fsc_stdout)]

        # if all(validate_processes):
        #     # Refinement against half map one
        #     self.refine_hm1_results = PrivateerRefineResultsParser(
        #         stdout=self.validate_hm1_stdout)
        #     self.refine_hm2_results = PrivateerRefineResultsParser(
        #         stdout=self.validate_hm2_stdout)
        #     self.fix_privateer_fsc_table(stdout=self.fsc_stdout)
        #     self.fsc_hm1hm2 = PrivateerFSCMapParser(
        #         stdout=self.fsc_stdout)
        #     self.set_validation_results()

    def set_log(self, path):
        '''
        Set log text file display.
        '''
        pyrvapi.rvapi_add_tab('log_tab', 'Log file', False)
        pyrvapi.rvapi_append_content(path, True, 'log_tab') # To do_pageTop replaces tab1
        pyrvapi.rvapi_flush()

    def set_refine_results_summary(self):
        '''
        Set summary of refinement results from metadata table.
        '''
#         validate_tab = 'tab3'
#         validate_sec = 'sec_hm1'
#         validate_table = 'table_hm1'
#         # Setup refine_results (summary, graphs and output files)
#         pyrvapi.rvapi_add_header('Privateer Results')
#         pyrvapi.rvapi_add_tab(validate_tab, 'Validation', True)
#         pyrvapi.rvapi_add_section(validate_sec,
#                                   'Refinement summary',
#                                   validate_tab,
#                                   0, 0, 1, 1, True)
#
        # dac mode
        if os.path.exists(self.dac_stdout):
            refine_tab = 'refine_tab'
            refine_sec = 'sec_refine'
            refine_summary_table = 'refine_table'
            pyrvapi.rvapi_add_header('Divide and Conquer Results')
            pyrvapi.rvapi_add_tab(refine_tab, 'Refinement', True)
            pyrvapi.rvapi_add_section(refine_sec,
                                  'Refinement summary',
                                  refine_tab,
                                  0, 0, 1, 1, True)

            if len(self.dac_results.results_summary) < 1:
                pyrvapi.rvapi_set_text('<H2>Divide and Conquer Script failed; please look at the log file</H2>\n', refine_sec, 0, 0, 1, 1)
                print 'Results Summary:'
                print self.dac_results.results_summary
                return

            if len(self.dac_results.results_summary[0]) <= 1:
                print 'Results Summary:'
                print self.dac_results.results_summary
                pyrvapi.rvapi_set_text('<H2>Divide and Conquer Script failed; please look at the log file</H2>\n', refine_sec, 0, 0, 1, 1)
                return

            pyrvapi.rvapi_add_table(refine_summary_table, 'Divide and Conquer Refinement Results', refine_sec, 0, 0, 1, 1, 100)

            columnsIds = {}
            i = 0
            if 'ramaOut' in self.dac_results.results_summary[0].keys():
                pyrvapi.rvapi_put_horz_theader(refine_summary_table, 'Ramachandran <br>outliers', 'C2',  i)
                pyrvapi.rvapi_shape_horz_theader(refine_summary_table, i, '', '', 1, 2)
                columnsIds['ramaOut'] = i
                i += 1

            if 'ramaFav' in self.dac_results.results_summary[0].keys():
                pyrvapi.rvapi_put_horz_theader(refine_summary_table, 'Ramachandran <br>favoured', 'C3',  i)
                pyrvapi.rvapi_shape_horz_theader(refine_summary_table, i, '', '', 1, 2)
                columnsIds['ramaFav'] = i
                i += 1

            if 'rmsBonds' in self.dac_results.results_summary[0].keys():
                pyrvapi.rvapi_put_horz_theader(refine_summary_table, 'RMS bonds', 'C4', i)
                pyrvapi.rvapi_shape_horz_theader(refine_summary_table, i, '', '', 1, 2)
                columnsIds['rmsBonds'] = i
                i += 1

            if 'rmsAngles' in self.dac_results.results_summary[0].keys():
                pyrvapi.rvapi_put_horz_theader(refine_summary_table, 'RMS angles', 'C5',  i)
                pyrvapi.rvapi_shape_horz_theader(refine_summary_table, i, '', '', 1, 2)
                columnsIds['rmsAngles'] = i
                i += 1

            if 'rFact' in self.dac_results.results_summary[0].keys():
                pyrvapi.rvapi_put_horz_theader(refine_summary_table, 'R-factor', 'C6',  i)
                pyrvapi.rvapi_shape_horz_theader(refine_summary_table, i, '', '', 1, 2)
                columnsIds['rFact'] = i
                i += 1

            if 'fsc' in self.dac_results.results_summary[0].keys():
                pyrvapi.rvapi_put_horz_theader(refine_summary_table, 'Average FSC', 'C7',  i)
                pyrvapi.rvapi_shape_horz_theader(refine_summary_table, i, '', '', 1, 2)
                columnsIds['fsc'] = i

            pyrvapi.rvapi_put_vert_theader (refine_summary_table, '', '', 0)
            i = 1
            for record in self.dac_results.results_summary:
                if 'pdb' in record.keys():
                    pyrvapi.rvapi_put_vert_theader (refine_summary_table, record['pdb'], 'R%d' % i, i)
                    i += 1
                else:
                    pyrvapi.rvapi_set_text('<H2>Parser could not find file names for the PDB files (do they have .pdb extension?)<BR> Please look at the log file</H2>\n', refine_sec, 0, 0, 1, 1)
                    return


            for i in range(len(columnsIds)):
                pyrvapi.rvapi_put_table_string (refine_summary_table,
                                                'Before', 0, i * 2)
                pyrvapi.rvapi_put_table_string (refine_summary_table,
                                                'After', 0, (i * 2) + 1)

            i = 1
            for record in self.dac_results.results_summary:
                if 'ramaOut' in record.keys():
                    s1 = '%0.2f %%' % (record['ramaOut'][0])
                    s2 = '%0.2f %%' % (record['ramaOut'][1])
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s1, i,
                                                    columnsIds['ramaOut'] * 2)
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s2, i,
                                                    (columnsIds['ramaOut'] * 2) + 1)

#                'ramaFav'
                if 'ramaFav' in record.keys():
                    s1 = '%0.2f %%' % (record['ramaFav'][0])
                    s2 = '%0.2f %%' % (record['ramaFav'][1])
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s1, i,
                                                    columnsIds['ramaFav'] * 2)
                    pyrvapi.rvapi_put_table_string (
                        refine_summary_table, s2, i,
                        (columnsIds['ramaFav'] * 2) + 1)

#               'rmsBonds'
                if 'rmsBonds' in record.keys():
                    s1 = '%0.3f' % (record['rmsBonds'][0])
                    s2 = '%0.3f' % (record['rmsBonds'][1])
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s1, i,
                                            columnsIds['rmsBonds'] * 2)
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s2, i,
                                            (columnsIds['rmsBonds'] * 2) + 1)

                #'rmsAngles'
                if 'rmsAngles' in record.keys():
                    s1 = '%0.3f' % (record['rmsAngles'][0])
                    s2 = '%0.3f' % (record['rmsAngles'][1])
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s1, i,
                                                    columnsIds['rmsAngles'] * 2)
                    pyrvapi.rvapi_put_table_string (
                        refine_summary_table, s2, i,
                        (columnsIds['rmsAngles'] * 2) + 1)

                #'rFact'
                if 'rFact' in record.keys():
                    s1 = '%0.2f %%' % (record['rFact'][0] * 100)
                    s2 = '%0.2f %%' % (record['rFact'][1] * 100)
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s1, i,
                                                    columnsIds['rFact'] * 2)
                    pyrvapi.rvapi_put_table_string (
                        refine_summary_table, s2, i,
                        (columnsIds['rFact'] * 2) + 1)

                #'fsc'
                if 'fsc' in record.keys():
                    s1 = '%0.2f' % (record['fsc'][0])
                    s2 = '%0.2f' % (record['fsc'][1])
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s1, i,
                                                    columnsIds['fsc'] * 2)
                    pyrvapi.rvapi_put_table_string (refine_summary_table, s2, i,
                                                    (columnsIds['fsc'] * 2) + 1)

                i += 1

            pyrvapi.rvapi_flush()
            return

        # Set table
        refine_tab = 'refine_tab'
        refine_sec = 'sec_refine'
        refine_summary_table = 'refine_table'
        pyrvapi.rvapi_add_header('Privateer Results')
        pyrvapi.rvapi_add_tab(refine_tab, 'Refinement', True)
        pyrvapi.rvapi_add_section(refine_sec,
                                  'Refinement summary',
                                  refine_tab,
                                  0, 0, 1, 1, True)
        # pyrvapi.rvapi_add_text('Refinement summary', refine_sec, 0, 0, 1, 1)
        pyrvapi.rvapi_add_table(
            refine_summary_table, 'Refinement statistics', refine_sec, 0, 0, 1, 1, False)
        self.refine_results.results_summary.set_pyrvapi_table(
             table_id=refine_summary_table)

        if len(self.refine_results.weightText) > 1:
            weightParts = self.refine_results.weightText.split('E')
            weightReal = 0.0
            if len(weightParts) == 2:
                weightReal = float(weightParts[0]) * (10**int(weightParts[1]))
            if weightReal > 0:
                pyrvapi.rvapi_add_text('\nWeight Term: ' + self.refine_results.weightText + ' (%0.6f)' % weightReal, refine_sec, 1, 0, 1, 1)
            else:
                pyrvapi.rvapi_add_text('\nWeight Term: ' + self.refine_results.weightText, refine_sec, 1, 0, 1, 1)

        # Set refinement graphs - per ncyc and final
        refinement_graphs_id = 'ncyc_graphs'

        # Set graphs - refinement statistics vs cycle

        # Remove unwanted cols and set index
        keep_col = ['Ncyc', 'Rfact', 'rmsBOND', 'rmsANGL', 'rmsCHIRAL']
        for col in self.refine_results.ncyc_table.columns:
            if col not in keep_col:
                self.refine_results.ncyc_table.drop(col, axis=1, inplace=True)
        self.refine_results.ncyc_table.set_index('Ncyc', inplace=True)

        # Set col
        ncyc_data_id = 'ncyc_data'
        pyrvapi.rvapi_append_loggraph(refinement_graphs_id, refine_tab)
        pyrvapi.rvapi_add_graph_data(ncyc_data_id,
                                     refinement_graphs_id,
                                     'Statistics per refinement cycle')
        self.refine_results.ncyc_table.set_pyrvapi_graph(
            graph_id=refinement_graphs_id,
            data_id=ncyc_data_id,
            originalXAxis=True,
            step=1)

        # Set graphs - final graphs

        # Remove unwanted cols and set index
        keep_col = [angstrom_label, 'FSCwork', 'SigmaA_Fc1', 'CorrFofcWork']
        for col in self.refine_results.fsc_fom_table.columns:
            if col not in keep_col:
                self.refine_results.fsc_fom_table.drop(
                    col,
                    axis=1,
                    inplace=True)
        self.refine_results.fsc_fom_table.set_index(angstrom_label,
                                                    inplace=True)
        final_graph_id = 'final_graphs'
        final_data_id = 'final_data'
        pyrvapi.rvapi_append_loggraph(final_graph_id, refine_tab)
        pyrvapi.rvapi_add_graph_data(final_data_id,
                                     refinement_graphs_id,
                                     'Final refinement statistics')
        self.refine_results.fsc_fom_table.set_pyrvapi_graph(
            graph_id=refinement_graphs_id,
            data_id=final_data_id,
            originalXAxis=True,
            step=max(int(len(self.refine_results.fsc_fom_table) / 7.0 ), 1),
            ymin=0.0)

        ### Power spectrum
        #    1) Mn(|F|)
        #    2) Mn(|F|^2)
        #    3) Var = sqrt(<Fmean**2> - <Fmean>2)
        #        -> math.sqrt ( Mn(|F|^2) - math.pow(Mn(|F|), 2) )
        if self.mrc2mtz_results is not None:
            if self.mrc2mtz_results.mean_amp_table is not None:
                keep_col = [angstrom_label, 'Mn(|F|)', 'Mn(|F|^2)']
                for col in self.mrc2mtz_results.mean_amp_table.columns:
                    if col not in keep_col:
                        self.mrc2mtz_results.mean_amp_table.drop(
                            col,
                            axis=1,
                            inplace=True)
                self.mrc2mtz_results.mean_amp_table.set_index(angstrom_label,
                                                              inplace=True)
                # Calculate variance
                self.mrc2mtz_results.mean_amp_table['Mn(|F|)^2'] = \
                    self.mrc2mtz_results.mean_amp_table['Mn(|F|)'].apply(
                        lambda x: str(math.pow(float(x), 2)))
                self.mrc2mtz_results.mean_amp_table['Variance'] = \
                    self.mrc2mtz_results.mean_amp_table['Mn(|F|^2)'].astype(float)
                self.mrc2mtz_results.mean_amp_table['Variance'] = \
                    self.mrc2mtz_results.mean_amp_table['Variance'].subtract(
                        self.mrc2mtz_results.mean_amp_table['Mn(|F|)^2'].astype(float))
                self.mrc2mtz_results.mean_amp_table['Variance'] = \
                    self.mrc2mtz_results.mean_amp_table['Variance'].apply(
                        np.sqrt).astype(str)
                self.mrc2mtz_results.mean_amp_table.drop(
                    'Mn(|F|)^2',
                    axis=1,
                    inplace=True)

                self.mrc2mtz_results.mean_amp_table['Log(Mn(|F|))'] = \
                    self.mrc2mtz_results.mean_amp_table['Mn(|F|)'].apply(
                        lambda x: str(math.log(float(x))))
                self.mrc2mtz_results.mean_amp_table['Log(Mn(|F|^2))'] = \
                    self.mrc2mtz_results.mean_amp_table['Mn(|F|^2)'].apply(
                        lambda x: str(math.log(float(x))))
                self.mrc2mtz_results.mean_amp_table['Log(Variance)'] = \
                    self.mrc2mtz_results.mean_amp_table['Variance'].apply(
                        lambda x: str(math.log(float(x))))

                self.mrc2mtz_results.mean_amp_table.drop(
                    'Mn(|F|)',
                    axis=1,
                    inplace=True)
                self.mrc2mtz_results.mean_amp_table.drop(
                    'Mn(|F|^2)',
                    axis=1,
                    inplace=True)
                self.mrc2mtz_results.mean_amp_table.drop(
                    'Variance',
                    axis=1,
                    inplace=True)
                #
                map_data_id = 'map_data'
                pyrvapi.rvapi_append_loggraph(refinement_graphs_id, refine_tab)
                pyrvapi.rvapi_add_graph_data(map_data_id,
                                             refinement_graphs_id,
                                             'Input SF statistics')
                self.mrc2mtz_results.mean_amp_table.set_pyrvapi_graph(
                    graph_id=refinement_graphs_id,
                    data_id=map_data_id,
                    originalXAxis=True,
                    step=max(int(len(self.mrc2mtz_results.mean_amp_table) / 7.0), 1))


    def set_validation_results(self):
        '''
        Refine against half map 1.
        '''
        validate_tab = 'tab3'
        validate_sec = 'sec_hm1'
        validate_table = 'table_hm1'
        # Setup refine_results (summary, graphs and output files)
        pyrvapi.rvapi_add_header('Privateer Results')
        pyrvapi.rvapi_add_tab(validate_tab, 'Validation', True)
        pyrvapi.rvapi_add_section(validate_sec,
                                  'Refinement summary',
                                  validate_tab,
                                  0, 0, 1, 1, True)
        pyrvapi.rvapi_add_text(
            'Refinement summary (shaken structure vs work half map)',
            validate_sec, 0, 0, 1, 1)

        ### Set validate table
        pyrvapi.rvapi_add_table(
            validate_table, 'Refinement statistics', validate_sec, 1, 0, 1,
            1, False)
        self.refine_hm1_results.results_summary.set_pyrvapi_table(
            table_id=validate_table)

        ### Set model vs maps (work and free) plots

        # Remove unwanted cols and set index
        keep_col = [angstrom_label, 'FSCwork', 'CorrFofcWork']
        #
        for col in self.refine_hm1_results.fsc_fom_table.columns:
            if col not in keep_col:
                self.refine_hm1_results.fsc_fom_table.drop(col,
                                                           axis=1,
                                                           inplace=True)
        self.refine_hm1_results.fsc_fom_table.set_index(angstrom_label,
                                                        inplace=True)
        #
        for col in self.refine_hm2_results.fsc_fom_table.columns:
            if col not in keep_col:
                self.refine_hm2_results.fsc_fom_table.drop(col,
                                                           axis=1,
                                                           inplace=True)
        self.refine_hm2_results.fsc_fom_table.set_index(angstrom_label,
                                                        inplace=True)

        # Manually renamed col names from work to free
        self.refine_hm2_results.fsc_fom_table.rename(
            columns={'FSCwork': 'FSCfree',
                     'CorrFofcWork':'CorrFofcFree'},
            inplace=True)
        #
        map_v_model_data_id = 'map_v_model_data_id' #map_v_model_data'
        map_v_model_graphs_id = 'map_v_model_graphs_id'
        plot_id_list =  self.refine_hm1_results.fsc_fom_table.columns
        pyrvapi.rvapi_append_loggraph(map_v_model_graphs_id, validate_tab)
        pyrvapi.rvapi_add_graph_data(map_v_model_data_id,
                                     map_v_model_graphs_id,
                                     'Model vs map (work and free)')
        # Set plots from datatable
        self.refine_hm1_results.fsc_fom_table.set_pyrvapi_graph(
            graph_id=map_v_model_graphs_id,
            data_id=map_v_model_data_id,
            plot_id_list=plot_id_list,
            originalXAxis=True,
            step=int(len(self.refine_hm1_results.fsc_fom_table) / 7.0))

        self.refine_hm2_results.fsc_fom_table.set_pyrvapi_graph(
            graph_id=map_v_model_graphs_id,
            data_id=map_v_model_data_id,
            plot_id_list=plot_id_list,
            originalXAxis=True,
            step=int(len(self.refine_hm2_results.fsc_fom_table) / 7.0))

#         # Set axis min
#         for plot_id in plot_id_list:
#             pyrvapi.rvapi_set_plot_ymin(plot_id, map_v_model_graphs_id, 0.0)
        # Remove unwanted cols and set index
        keep_col = [angstrom_label, 'FSCwork', 'CorrFofcWork']
        for col in self.refine_hm1_results.fsc_fom_table.columns:
            if col not in keep_col:
                self.refine_hm1_results.fsc_fom_table.drop(col,
                                                           axis=1,
                                                           inplace=True)

        # Half map 1 vs 2
        self.fsc_hm1hm2.fsc_table.set_index(angstrom_label,
                                            inplace=True)
        keep_col = [angstrom_label, 'FSC', 'cos(PHdiff)', 'cor(|F1|,|F2|)']
        for col in self.fsc_hm1hm2.fsc_table.columns:
            if col not in keep_col:
                self.fsc_hm1hm2.fsc_table.drop(col,
                                               axis=1,
                                               inplace=True)
        #
        map_v_map_data_id = 'fsc_data' #map_v_model_data'
        #
        pyrvapi.rvapi_append_loggraph(map_v_model_graphs_id, validate_tab)
        pyrvapi.rvapi_add_graph_data(map_v_map_data_id,
                                     map_v_model_graphs_id,
                                     'Half map 1 vs 2')
        # Set plots from datatable
        plot_id_fsc_list =  self.fsc_hm1hm2.fsc_table.columns
        self.fsc_hm1hm2.fsc_table.set_pyrvapi_graph(
            graph_id=map_v_model_graphs_id,
            data_id=map_v_map_data_id,
            plot_id_list=plot_id_fsc_list,
            originalXAxis=True,
            step=int(len(self.fsc_hm1hm2.fsc_table) / 7.0))


def smartie_table_to_meta_data_table(table):
    '''
    Convenience utility to convert CCP4 log graph to numpy array.
    '''
    ncolumns = table.ncolumns()
    if ncolumns > 0:
        nrows = len(table.table_column(0))
    else:
        nrows = 0
    md_table = metadata_utils.MetaDataTable()
    for i in range(0, nrows):
        for j in range(0, ncolumns):
            col = table.table_column(j)
            md_table.add_column(label=col.title(),
                                ccpem_labels=None,
                                data=col.data())
    return md_table


class PrivateerPowerSpectrumParser(object):
    '''
    PrivateerMapToMtz program should have following table:
        Mean(|F|) and other statistics
    '''
    def __init__(self, stdout):
        self.log = smartie.parselog(stdout)
        self.mean_amp_table = None
        prog = self.log.program(0)
        for table in prog.tables():
            if table.title() == 'Mean(|F|) and other statistics':
                try:
                    self.mean_amp_table = \
                        smartie_table_to_meta_data_table(table=table)
                    self.mean_amp_table.convert_to_resolution_angstrom()
                    self.mean_amp_table.replace_infinity()
                except ValueError:
                    self.mean_amp_table = None
                    ccpem_utils.print_warning('Unable to parse Mean(|F|) table')

class PrivateerFSCMapParser(object):
    '''
    FSC program should have following table:
        FSC and other statistics
    '''
    def __init__(self, stdout):
        self.log = smartie.parselog(stdout)
        # Find FSC program in stdout
        fsc_prog = self.log.program(0)
        self.fsc_table = None
        for table in fsc_prog.tables():
            if table.title() == 'FSC and other statistics':
                self.fsc_table = \
                    smartie_table_to_meta_data_table(table=table)
                self.fsc_table.convert_to_resolution_angstrom()
                self.fsc_table.replace_infinity()
        if self.fsc_table is None:
            ccpem_utils.print_warning('Unable to parse FSC table')

    def print_summary(self):
        if self.fsc_table is not None:
            print self.fsc_table.to_string()

class PrivateerRefineResultsParser(object):
    '''
    Program number specifies which program in cases of concatenated stout
    files.
    '''
    def __init__(self, stdout):
        self.stdout = stdout
        self.log = smartie.parselog(self.stdout)
        #
        self.refine_results = None
        self.ncyc_table = None
        self.fsc_fom_table = None
        self.weightText = ''

        stdoutIN = open(self.stdout, 'r')

        for line in stdoutIN:
            match = re.search('Weight matrix\s*(.*)', line)
            if match:
                self.weightText = match.group(1)

        # Get refinement prog
        refine_prog = self.log.program(0)
        # Get results summary
        if refine_prog.keytext(-1).name() == 'Result':
            self.refine_results = refine_prog.keytext(-1)
        if self.refine_results is not None:
            self.set_results_summary()

            # Parse table list in reverse order to find final FSC and ncyc table
            for cntr in reversed(xrange(len(refine_prog.tables()))):
                table = refine_prog.tables()[cntr]
                if table.title().find('FSC and  Fom') != -1:
                    if self.fsc_fom_table is None:
                        self.fsc_fom_table = smartie_table_to_meta_data_table(
                            table=table)
                        self.fsc_fom_table.convert_to_resolution_angstrom()

                if table.title().find('Rfactor analysis, stats vs cycle') != -1:
                    if self.ncyc_table is None:
                        self.ncyc_table = smartie_table_to_meta_data_table(
                            table=table)
                # Stop if both table found
                if self.ncyc_table is not None \
                        and self.fsc_fom_table is not None:
                    break

    def set_results_summary(self):
        data = collections.OrderedDict()
        data['Start'] = self.get_initial_full_refine_stats()
        data['Finish'] = self.get_final_refine_stats()
        self.results_summary = metadata_utils.MetaDataTable(data)
        self.results_summary = metadata_utils.MetaDataTable(
            self.results_summary.transpose())

    def get_initial_full_refine_stats(self):
        res = self.refine_results.message().split()
        i_res = collections.OrderedDict()
        i_res['FSC average'] = '-'
        i_res['R factor'] = res[4]
        i_res['Rms bond'] = res[8]
        i_res['Rms angle'] = res[12]
        i_res['Rms chiral'] = res[16]
        # Get overall fsc
        i_res['FSC average'] = self.find_fsc_average_at_rfactor(
            r_string=i_res['R factor'])
        return i_res

    def get_final_refine_stats(self):
        res = self.refine_results.message().split()
        f_res = collections.OrderedDict()
        f_res['FSC average'] = '-'
        f_res['R factor'] = res[5]
        f_res['Rms bond'] = res[9]
        f_res['Rms angle'] = res[13]
        f_res['Rms chiral'] = res[17]
        f_res['FSC average'] = self.find_fsc_average_at_rfactor(
            r_string=f_res['R factor'],
            reverse=True)
        return f_res

    def find_fsc_average_at_rfactor(self,
                                    r_string,
                                    reverse=False):
        # Find starting fsc
        search_file = open(self.stdout, 'r').read()
        r_line = 'Overall R factor                     =     {0}'.format(
            r_string)
        if reverse:
            find = search_file.rfind(r_line)
        else:
            find = search_file.find(r_line)
        fsc_line = search_file[find+40:find+100]
        fsc_line = fsc_line.split()
        fsc_average = fsc_line[fsc_line.index('=')+1]
        return fsc_average

    def print_summary(self):
        print self.refine_results.message()
        print self.fsc_fom_table.to_string()
        print self.ncyc_table.to_string()

class dacParser(object):
    '''
    Parser for Divide and Conquer mode

    '''
    def __init__(self, stdout):
        self.stdout = stdout
        self.log = os.path.dirname(stdout) + '/DaC/DaC.log'        # smartie.parselog(self.stdout)
        self.set_results_summary()


    def set_results_summary(self):
        self.results_summary = []

        isSummary = False
        stdoutFile = open(self.stdout, 'r')

        currentResult = {}

        for line in stdoutFile:
            match = re.search('Please find following refined PDB files',line)
            if match:
                isSummary = True
                currentResult = {}

            if isSummary:
                # name of a PDB file
                match = re.search('\.pdb', line.lower())
                if match:
                    if 'pdb' in currentResult.keys():
                        self.results_summary.append(currentResult)
                        currentResult = {}
                        currentResult['pdb'] = line.strip()
                        continue
                    else:
                        currentResult['pdb'] = line.strip()

                    # Rama outliers
                    match = re.search('Ramachandran outliers \(before\/after\)\:(.*)\/(.*)\%', line)
                    if match:
                        currentResult['ramaOut'] = (float(match.group(1).strip()), float(match.group(2).strip()))
                        continue

                    # Rama favoured
                    match = re.search('Ramachandran favoured \(before\/after\)\:(.*)\/(.*)\%', line)
                    if match:
                        currentResult['ramaFav'] = (float(match.group(1).strip()), float(match.group(2).strip()))
                        continue

                    # RMS bonds
                    match = re.search('RMS bonds.*\(before\/after\)\:(.*)\/(.*)', line)
                    if match:
                        currentResult['rmsBonds'] = (float(match.group(1).strip()), float(match.group(2).strip()))
                        continue

                    # RMS angles
                    match = re.search('RMS angles.*\(before\/after\)\:(.*)\/(.*)', line)
                    if match:
                        currentResult['rmsAngles'] = (float(match.group(1).strip()), float(match.group(2).strip()))
                        continue

                    # R-factor
                    match = re.search('Overall R-factor.*\(before\/after\)\:(.*)\/(.*)', line)
                    if match:
                        currentResult['rFact'] = (float(match.group(1).strip()), float(match.group(2).strip()))
                        continue

                    # FSC
                    match = re.search('Average FSC.*\(before\/after\)\:(.*)\/(.*)', line)
                    if match:
                        currentResult['fsc'] = (float(match.group(1).strip()), float(match.group(2).strip()))
                        continue


            match = re.search('^collected', line)
            if match:
                self.results_summary.append(currentResult)
                break

        stdoutFile.close()

    def print_summary(self):
        print self.stdout

def main():
    # job_location = sys.argv[1]
    job_location = '/home/harold/ccpem_project/Privateer_30'

    PrivateerResultsViewer(
        job_location=job_location)

if __name__ == '__main__':
    main()
