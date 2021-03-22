import sys
import re
import os
import io
import time
import pyrvapi
import fileinput
import collections
import shutil
import numpy as np
import math
from lxml import etree, html
from ccpem_core import process_manager
from ccpem_core import ccpem_utils
from ccpem_core.ccpem_utils.ccp4_log_parser import smartie
from ccpem_core.data_model import metadata_utils
import pyrvapi_ext as API


class PrivateerResultsViewer(object):
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
            privateer_data = self.GetXML2Table('Privateer', results_tab, self.xmlfilename)
            self.validation_summary_graph(privateer_data, results_tab)
            self.display_glycan_chains(results_tab, self.xmlfilename)

            
    def get_reference(self, process):
        '''
        Get references to put in a section in results tab
        '''
        
        reference_list = ["\'Privateer: software for the conformational validation of carbohydrate structures.\' \nAgirre J, Iglesias-Fernandez J, Rovira C, Davies GJ, Wilson KS, Cowtan KD. (2014). \nNat Struct Mol Biol. 2015 Nov 4;22(11):833-4. doi: 10.1038/nsmb.3115."]
        return reference_list
    
    def GetXML2Table(self, process, results_tab, xmlfilename):
        '''
        Get data from XML output and fill table
        '''

        data = collections.OrderedDict()
        tab_name = 'Sugar view'
        tree = etree.parse(xmlfilename)  # self.xmlfilename)
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
        pyrvapi.rvapi_add_section(
            validation_sec, 'Detailed Monosaccharide validation results', results_tab, 0, 0, 1, 1, False)
        pyrvapi.rvapi_flush()
        if "Pyranoses" in data:
            # set tabs and sections
            pyrvapi.rvapi_add_table(
                validation_table, 'Detailed validation data for Pyranoses', validation_sec, 1, 0, 1, 1, False)
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
                        j += 1  
                        pyrvapi.rvapi_put_table_string(
                            validation_table, entries[name].text, i, j)  # fill in built values
                    else:
                        pyrvapi.rvapi_put_table_string(
                            validation_table, entries[name].text, i, j)  # fill in built values
                    j += 1
                i += 1
            pyrvapi.rvapi_flush()  
        if "Furanoses" in data:
            pyrvapi.rvapi_add_tab(validation_tab, tab_name, True)
            pyrvapi.rvapi_add_table(
                validation_table, 'Detailed validation data for Furanoses', validation_sec, 1, 0, 1, 1, False)
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
        if "Pyranoses" in validationdata:
            pyranoses = validationdata["Pyranoses"]

            low_energy_pyranoses   = []
            high_energy_pyranoses  = []
            other_issues_pyranoses = []

            for pyranose in pyranoses:
                if "conformation" in pyranose["Diagnostic"].text.lower() :
                    high_energy_pyranoses.append ( pyranose )
                elif "Ok" in pyranose["Diagnostic"].text:
                    low_energy_pyranoses.append ( pyranose )
                else : other_issues_pyranoses.append ( pyranose )

            graphWid1 = API.loggraph(results_tab)
            brdata = API.graph_data(graphWid1, 'Summary of detected pyranoses')
            dx_ok_Alpha = API.graph_dataset(brdata, 'Phi', 'Phi', isint=False)
            dy_ok_Alpha = API.graph_dataset(brdata, 'OK', 'y1', isint=False)
            dx_conformation_Alpha = API.graph_dataset(brdata, 'Phi', 'Phi', isint=False)
            dy_conformation_Alpha = API.graph_dataset(brdata, 'Conformation might be mistaken', 'y2', isint=False)
            dx_other_Alpha = API.graph_dataset(brdata, 'Phi', 'Phi', isint=False)
            dy_other_Alpha = API.graph_dataset(brdata, 'Other Issues', 'y3', isint=False)

            ycol_Alpha = 'Theta'
            xcol_Alpha = 'Phi'
            yaxlabel_Alpha = 'Theta'
            xmax_ok_Alpha = len(low_energy_pyranoses)
            xmax_conformation_Alpha = len(high_energy_pyranoses)
            xmax_other_Alpha = len(other_issues_pyranoses)
            for i in range(0, xmax_ok_Alpha):
                dx_ok_Alpha.add_datum(float(low_energy_pyranoses[i][xcol_Alpha].text))
                dy_ok_Alpha.add_datum(float(low_energy_pyranoses[i][ycol_Alpha].text))
            for i in range(0, xmax_conformation_Alpha):
                dx_conformation_Alpha.add_datum(float(high_energy_pyranoses[i][xcol_Alpha].text))
                dy_conformation_Alpha.add_datum(float(high_energy_pyranoses[i][ycol_Alpha].text))
            for i in range(0, xmax_other_Alpha):
                dx_other_Alpha.add_datum(float(other_issues_pyranoses[i][xcol_Alpha].text))
                dy_other_Alpha.add_datum(float(other_issues_pyranoses[i][ycol_Alpha].text))
            plotAlpha = API.graph_plot(graphWid1, "Conformational landscape for pyranoses", xcol_Alpha, yaxlabel_Alpha)
            plotAlpha.reset_xticks()
            plotAlpha.reset_yticks()
            for i in range(360, -1, -30):
                plotAlpha.add_xtick(i, '%d' % (i))
            for i in range(180, -1, -45):
                plotAlpha.add_ytick(i, '%d' % (i))
            dx_y_OK_Alpha = API.plot_line(plotAlpha, brdata, dx_ok_Alpha, dy_ok_Alpha)
            dx_y_OK_Alpha.set_options(color='olivedrab', marker='.', style=API.LINE_Off, width=1.0)
            dx_y_CONFORMATION_Alpha = API.plot_line(plotAlpha, brdata, dx_conformation_Alpha, dy_conformation_Alpha)
            dx_y_CONFORMATION_Alpha.set_options(color='red', marker='x', style=API.LINE_Off, width=2.0)
            dx_y_OTHER_Alpha = API.plot_line(plotAlpha, brdata, dx_other_Alpha, dy_other_Alpha)
            dx_y_OTHER_Alpha.set_options(color='orange', marker='o', style=API.LINE_Off, width=2.5)
            plotAlpha.set_legend('s', 'outsideGrid')


            dx_ok_Bravo = API.graph_dataset(brdata, 'BFactor', 'BFactor', isint=False)
            dy_ok_Bravo = API.graph_dataset(brdata, 'OK', 'y1', isint=False)
            dx_conformation_Bravo = API.graph_dataset(brdata, 'BFactor', 'BFactor', isint=False)
            dy_conformation_Bravo = API.graph_dataset(brdata, 'Conformation might be mistaken', 'y2', isint=False)
            dx_other_Bravo = API.graph_dataset(brdata, 'BFactor', 'BFactor', isint=False)
            dy_other_Bravo = API.graph_dataset(brdata, 'Other Issues', 'y3', isint=False)

            ycol_Bravo = 'RSCC'
            xcol_Bravo = 'BFactor'
            yaxlabel_Bravo = 'Real Space CC'
            xaxlabel_Bravo = 'Isotropic B-Factor'
            xmax_ok_Bravo = len(low_energy_pyranoses)
            xmax_conformation_Bravo = len(high_energy_pyranoses)
            xmax_other_Bravo = len(other_issues_pyranoses)
            for i in range(0, xmax_ok_Bravo):
                dx_ok_Bravo.add_datum(float(low_energy_pyranoses[i][xcol_Bravo].text))
                dy_ok_Bravo.add_datum(float(low_energy_pyranoses[i][ycol_Bravo].text))
            for i in range(0, xmax_conformation_Bravo):
                dx_conformation_Bravo.add_datum(float(high_energy_pyranoses[i][xcol_Bravo].text))
                dy_conformation_Bravo.add_datum(float(high_energy_pyranoses[i][ycol_Bravo].text))
            for i in range(0, xmax_other_Bravo):
                dx_other_Bravo.add_datum(float(other_issues_pyranoses[i][xcol_Bravo].text))
                dy_other_Bravo.add_datum(float(other_issues_pyranoses[i][ycol_Bravo].text))
            plotBravo = API.graph_plot(graphWid1, "BFactor vs RSCC", xaxlabel_Bravo, yaxlabel_Bravo)
            plotBravo.reset_xticks()
            plotBravo.reset_yticks()
            yticks = [0.0, 0.5, 0.7, 1.0]
            for i in range(0, 101, 20):
                plotBravo.add_xtick(i, '%d' % (i))
            for i in yticks:
                plotBravo.add_ytick(i, '%.1f' % (i))
            dx_y_OK_Bravo = API.plot_line(plotBravo, brdata, dx_ok_Bravo, dy_ok_Bravo)
            dx_y_OK_Bravo.set_options(color='olivedrab', marker='.', style=API.LINE_Off, width=1.0)
            dx_y_CONFORMATION_Bravo = API.plot_line(plotBravo, brdata, dx_conformation_Bravo, dy_conformation_Bravo)
            dx_y_CONFORMATION_Bravo.set_options(color='red', marker='x', style=API.LINE_Off, width=2.0)
            dx_y_OTHER_Bravo = API.plot_line(plotBravo, brdata, dx_other_Bravo, dy_other_Bravo)
            dx_y_OTHER_Bravo.set_options(color='orange', marker='o', style=API.LINE_Off, width=2.5)
            plotBravo.set_legend('s', 'outsideGrid')
            API.flush()

    def display_glycan_chains(self, results_tab, xmlfilename):
        tree = etree.parse(xmlfilename)  # self.xmlfilename)
        PrivateerResult = tree.find('PrivateerResult')
        ValidationData = PrivateerResult.find('ValidationData')
        glycans = ValidationData.findall("Glycan")
        list_of_glycans = []
        if len(glycans):
            list_of_glycans = []
            for glycan in glycans:
                i_glycan_dict = collections.OrderedDict()
                i_glycan_dict['Chain'] = glycan.find('GlycanChain')
                i_glycan_dict['WURCS'] = glycan.find('GlycanWURCS')
                i_glycan_dict['GTCID'] = glycan.find('GlycanGTCID')
                i_glycan_dict['GlyConnectID'] = glycan.find('GlycanGlyConnectID')
                i_glycan_dict['SVG'] = glycan.find('GlycanSVG')
                permutationList = glycan.find('GlycanPermutations')
                if permutationList is not None:
                    permutations = permutationList.findall('GlycanPermutation')
                    list_of_permutations = []
                    for permutation in permutations:
                        i_permutation_dict = collections.OrderedDict()
                        i_permutation_dict['PermutationWURCS'] = permutation.find('PermutationWURCS')
                        i_permutation_dict['PermutationScore'] = permutation.find('PermutationScore')
                        i_permutation_dict['anomerPermutations'] = permutation.find('anomerPermutations')
                        i_permutation_dict['residuePermutations'] = permutation.find('residuePermutations')
                        i_permutation_dict['residuePermutations'] = permutation.find('residuePermutations')
                        i_permutation_dict['residueDeletions'] = permutation.find('residueDeletions')
                        i_permutation_dict['PermutationGTCID'] = permutation.find('PermutationGTCID')
                        i_permutation_dict['PermutationGlyConnectID'] = permutation.find('PermutationGlyConnectID')
                        i_permutation_dict['PermutationSVG'] = permutation.find('PermutationSVG')
                        list_of_permutations.append(i_permutation_dict)
                    i_glycan_dict['Permutations'] = list_of_permutations
                else:
                    i_glycan_dict['Permutations'] = None
                list_of_glycans.append(i_glycan_dict)
        
        tab_name = 'Glycan view'
        glycan_tab = 'glycan_tab'
        chain_sec = 'chain_sec'

        self.glycanViewHTMLoutput = self.generate_HTML_glycan_view(list_of_glycans)

        pyrvapi.rvapi_add_tab(glycan_tab, tab_name, False)
        pyrvapi.rvapi_add_section(
            chain_sec, 'Detected Glycan chains in the input model', glycan_tab, 0, 0, 1, 1, False)
        pyrvapi.rvapi_add_text(self.glycanViewHTMLoutput,
                                    chain_sec, 1, 0, 1, 1)
        pyrvapi.rvapi_flush()
    
    def generate_HTML_glycan_view(self, list_of_glycans):
        html = etree.Element('html')
        head = etree.Element('head')
        
        style = etree.Element('style')
        style.text = "\nhtml {\n\tline-height: 1.6em;\n\tfont-family: \"Lucida Sans Unicode\", \"Lucida Grande\", Sans-Serif;\n\tmargin: 10px;\n\ttext-align: left;\n\tborder-collapse: collapse;\n\tclear: both; \n}\n\n.accordion {\n\tdisplay:block;\n\ttext-decoration:none;\n\tmargin:3px;\n\tmax-width:1000px;\n\theight:1.6em;\n\tpadding:1px;\n\tpadding-left:10px;\n\tpadding-right:10px;\n\tborder:2px solid #DDD;\n\ttext-align:left;\n\tfont-size:110%;\n\t-webkit-border-radius:10px;\n\tborder-radius:1px;\n\tbackground:-webkit-gradient(linear, 0% 0%, 0% 110%, from(#FFFFFF), to(#EEE));\n\tcursor: pointer;\n\ttransition:0.4s \n}\n\n.active, .accordion:hover {\n\tbackground-color: #ccc;\n}\n\n.accordion:after {\n\tcontent: \'\\002B\';\n\tcolor: #777;\n\tfont-weight: bold;\n\tfloat: right;\n\tmargin-left: 5px;\n}\n\n.active:after {\n\tcontent: \"\\2212\";\n}\n\n.panel {\n\tpadding: 0 18px;\n\tbackground-color: white;\n\tmax-height: 0;\n\toverflow: hidden;\n\ttransition: max-height 0.2s ease-out;\n}\n"
        
        script = etree.Element('script')

        script.text = "\nvar acc = document.getElementsByClassName(\"accordion\");\nvar i;\n\nfor (i = 0; i < acc.length; i++) {\n\t  acc[i].addEventListener(\"click\", function() {\n\t\tthis.classList.toggle(\"active\");\n\t\tvar panel = this.nextElementSibling;\n\t\tif (panel.style.maxHeight) {\n\t\t\tpanel.style.maxHeight = null;\n\t\t} else {\n\t\t\tpanel.style.maxHeight = panel.scrollHeight + \"px\";\n\t\t}\n\t});\n}" 
        
        head.append(style)
        html.append(head)
        
        body = etree.Element('body')
        etree.tostring(script, method='html')
        html.append(body)

        divGlobal = etree.Element('div', attrib={'class': 'global'})
        explanationParagraph = etree.Element('p')
        explanationParagraph.text = "Below are graphical plots of the detected glycan trees. Placing your mouse pointer over any of the sugars will display a tooltip containing its residue name and number from the PDB file."
        divGlobal.append(explanationParagraph)
        
        for glycan in list_of_glycans:
            chainParagraph = etree.Element('p', attrib={'style': 'font-size:110%; padding:2px; margin-top:20px; margin-bottom:0px; font-weight:bold; margin-left:15px; clear:both'})
            modelledGlycanChainID = glycan['Chain'].text
            chainParagraph.text = "Chain " + modelledGlycanChainID
            divGlobal.append(chainParagraph)
            modelledGlycanSVGName = glycan['SVG'].text
            modelledGlycanSVGPath = os.path.join(self.job_location, modelledGlycanSVGName)
            if os.path.isfile(modelledGlycanSVGPath):
                svg_file = open(modelledGlycanSVGPath, 'r')
                svg_string = svg_file.read()
                svg_file.close()

                svg_string_partitioned = svg_string.partition("width=\"")
                svg_width = ''
                for symbol in svg_string_partitioned[2]:
                    if symbol != "\"":
                        svg_width = svg_width + symbol
                    else:
                        break
                
                ElementTreeSVGsource = etree.parse(modelledGlycanSVGPath)
                ElementSVGsource = ElementTreeSVGsource.getroot()
                
                divBetweenPandSVG = etree.Element('div', attrib={'style': 'border-width:1px; padding-top:10px; padding-bottom:10px; border-color:black; border-style:solid; border-radius:15px;'})
                divGlobal.append(divBetweenPandSVG)
                
                divSVG = etree.Element('div', attrib={'style': 'padding:10px;'})
                divSVG.append(ElementSVGsource)

                WURCSParagraph = etree.Element('p', attrib={'style': 'font-size:110%; font-weight:bold'})
                WURCSParagraph.text = glycan['WURCS'].text
                divSVG.append(WURCSParagraph)

                if glycan['GTCID'].text != "Unable to find GlyTouCan ID":
                    GTCIDParagraph = etree.Element('p', attrib={'style': 'font-size:110%; font-weight:bold'})
                    GTCIDParagraph.text = 'GlyTouCan ID: ' + glycan['GTCID'].text
                    divSVG.append(GTCIDParagraph)
                else:
                    GTCIDParagraph = etree.Element('p', attrib={'style': 'font-size:110%; font-weight:bold; color:#ff3300'})
                    GTCIDParagraph.text = 'GlyTouCan ID: Not Found'
                    divSVG.append(GTCIDParagraph)

                if glycan['GlyConnectID'].text != "Unable to find GlyConnect ID":
                    GlyConnectIDParagraph = etree.Element('p', attrib={'style': 'font-size:110%; font-weight:bold'})
                    GlyConnectIDParagraph.text = 'GlyConnect ID: ' + glycan['GlyConnectID'].text
                    divSVG.append(GlyConnectIDParagraph)
                else:
                    GlyConnectIDParagraph = etree.Element('p', attrib={'style': 'font-size:110%; font-weight:bold; color:#ff3300'})
                    GlyConnectIDParagraph.text = 'GlyConnect ID: Not Found'
                    divSVG.append(GlyConnectIDParagraph)
                    if glycan['Permutations'] is not None:
                        button = etree.Element('button', attrib={'class': 'accordion'})
                        button.text = 'Closest permutations detected on GlyConnect database'
                        divSVG.append(button)
                        sectionDiv = etree.Element('div', attrib={'class': 'panel'})
                        sectionDivStyle = etree.Element('div', attrib={'style': 'border-width: 1px; padding-top: 10px; padding-bottom:10px; border-color:black; border-style:solid; border-radius:15px;'})
                        permutationList = glycan['Permutations']

                        for permutation in permutationList:
                            permutationDivBorder = etree.Element('div', attrib={'style': 'border-width: 1px; padding-top: 10px; padding-bottom:10px; border-color:grey; border-style:dashed; border-radius:20px;'})
                            permutationGlycanSVGName = permutation['PermutationSVG'].text
                            permutationGlycanSVGPath = os.path.join(self.job_location, permutationGlycanSVGName)
                            if os.path.isfile(permutationGlycanSVGPath):
                                svg_file_permutation = open(permutationGlycanSVGPath, 'r')
                                svg_string = svg_file_permutation.read()
                                svg_file_permutation.close()

                                svg_string_partitioned_permutation = svg_string.partition("width=\"")
                                svg_width_permutation = ''
                                for symbol in svg_string_partitioned[2]:
                                    if symbol != "\"":
                                        svg_width_permutation = svg_width_permutation + symbol
                                    else:
                                        break
                                
                                permutationElementTreeSVGsource = etree.parse(permutationGlycanSVGPath)
                                permutationElementSVGsource = permutationElementTreeSVGsource.getroot()
                                permutationDivBorder.append(permutationElementSVGsource)

                                
                                WURCSParagraphPermutation = etree.Element('p', attrib={'style': 'font-size:110%; font-weight:bold'})
                                WURCSParagraphPermutation.text = permutation['PermutationWURCS'].text
                                permutationDivBorder.append(WURCSParagraphPermutation)

                                permutation['PermutationScore'].text
                                PermutationScore = etree.Element('p', attrib={'style': 'font-size:110%;'})
                                PermutationScore.text = 'Permutation Score(out of 100): '
                                if float(permutation['PermutationScore'].text) <= 1.00:
                                    spanText = etree.Element('span', attrib={'style': 'color:#00ff00; font-weight: bold'})
                                    spanText.text = permutation['PermutationScore'].text
                                    PermutationScore.append(spanText)
                                elif float(permutation['PermutationScore'].text) > 1.00 and float(permutation['PermutationScore'].text) <= 10.00:
                                    spanText = etree.Element('span', attrib={'style': 'color:#ffa500; font-weight: bold'})
                                    spanText.text = permutation['PermutationScore'].text
                                    PermutationScore.append(spanText)                                    
                                elif float(permutation['PermutationScore'].text) > 10.00:
                                    spanText = etree.Element('span', attrib={'style': 'color:#ff3300; font-weight: bold'})
                                    spanText.text = permutation['PermutationScore'].text
                                    PermutationScore.append(spanText)                                     

                                permutationDivBorder.append(PermutationScore)


                                anomerPermutations = etree.Element('p', attrib={'style': 'font-size:110%;'})
                                anomerPermutations.text = 'Anomer Permutations: '
                                spanTextAnomer = etree.Element('span', attrib={'style': 'font-weight: bold'})
                                spanTextAnomer.text = permutation['anomerPermutations'].text
                                anomerPermutations.append(spanTextAnomer)
                                permutationDivBorder.append(anomerPermutations)


                                residuePermutations = etree.Element('p', attrib={'style': 'font-size:110%;'})
                                residuePermutations.text = 'Residue Permutations: '
                                spanTextResidue = etree.Element('span', attrib={'style': 'font-weight: bold'})
                                spanTextResidue.text = permutation['residuePermutations'].text
                                residuePermutations.append(spanTextResidue)                            
                                permutationDivBorder.append(residuePermutations)


                                residueDeletions = etree.Element('p', attrib={'style': 'font-size:110%;'})
                                residueDeletions.text = 'Residue Deletions: '
                                spanTextDeletions = etree.Element('span', attrib={'style': 'font-weight: bold'})
                                spanTextDeletions.text = permutation['residueDeletions'].text
                                residueDeletions.append(spanTextDeletions)                                   
                                permutationDivBorder.append(residueDeletions)


                                PermutationGTCIDParagraph = etree.Element('p', attrib={'style': 'font-size:110%;'})
                                PermutationGTCIDParagraph.text = 'GlyTouCan ID: ' 
                                spanTextPermutationGTCID = etree.Element('span', attrib={'style': 'font-weight: bold'})
                                spanTextPermutationGTCID.text = permutation['PermutationGTCID'].text
                                PermutationGTCIDParagraph.append(spanTextPermutationGTCID)  
                                permutationDivBorder.append(PermutationGTCIDParagraph)


                                PermutationGlyConnectIDParagraph = etree.Element('p', attrib={'style': 'font-size:110%;'})
                                PermutationGlyConnectIDParagraph.text = 'Glyconnect ID: '
                                spanTextPermutationGlyConnectID = etree.Element('span', attrib={'style': 'font-weight: bold'})
                                spanTextPermutationGlyConnectID.text = permutation['PermutationGlyConnectID'].text
                                PermutationGlyConnectIDParagraph.append(spanTextPermutationGlyConnectID)  
                                permutationDivBorder.append(PermutationGlyConnectIDParagraph)

                                
                                divSeperator = etree.Element('div', attrib={'style': 'padding:10px; '})
                                permutationDivBorder.append(divSeperator)
                                sectionDivStyle.append(permutationDivBorder)
                        
                        sectionDiv.append(sectionDivStyle)
                        divSVG.append(sectionDiv)
                
                
                divBetweenPandSVG.append(divSVG)
                divCLEAR = etree.Element('div', attrib={'style': 'clear:both'})
                divBetweenPandSVG.append(divCLEAR)
                divGlobal.append(divBetweenPandSVG)
                
                # modelledGlycanWURCS = glycan['WURCS'].text
                # modelledGlycanGTCID = glycan['GTCID'].text
                # modelledGlycanGlyConnectID = glycan['GlyConnectID'].text
            
        
        body.append(divGlobal)
        body.append(script)

        self.glycanViewHTML = os.path.join(self.directory, 'glycanview.html')
        
        etree.ElementTree(html).write(self.glycanViewHTML, pretty_print=True, encoding='unicode', method='html')
        parser = etree.HTMLParser()
        glycanViewHACK = etree.parse(self.glycanViewHTML, parser)

        finalHTMLoutput = etree.tostring(glycanViewHACK,
                        pretty_print=True, method="html")

        return finalHTMLoutput


def main(target_dir=None):
    from PyQt4 import QtGui, QtCore, QtWebKit
    if target_dir is None:
        pl_dir = '/home/harold/ccpem_project/Privateer_30' # with permutations
        # pl_dir = '/home/harold/ccpem_project/Privateer_22' # permutation-less
    else:
        pl_dir = target_dir
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
        rv = PrivateerResultsViewer(job_location=job_location)
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
