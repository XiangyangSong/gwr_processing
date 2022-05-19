# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GWR
                                 A QGIS plugin
 A QGIS plugin for Geographically Weighted Regression(GWR).
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-02-15
        copyright            : (C) 2022 by Song
        email                : xiangyang.song@mail.polimi.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Song'
__date__ = '2022-02-15'
__copyright__ = '(C) 2022 by Song'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingMultiStepFeedback,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsProcessingParameterFile,
                       QgsWkbTypes,
                       QgsProcessingUtils)
                

import pandas as pd
import numpy as np
import os
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW


class GWRAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    # load to qgis directly as sink layer
    SINK_LAYER = 'SINK_LAYER'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # load vector layer
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name = 'source_layer',
                description = 'Input layer',
                types = [QgsProcessing.TypeVector],
                defaultValue=None,
                optional = False
            )
        )

        # load location file
        # self.addParameter(
        #             QgsProcessingParameterFile(
        #                 name = 'location_csv',
        #                 description = 'Open CSV file containing geographical coordinates',
        #                 defaultValue=None,
        #                 optional = False
        #             )
        #  )
        
        
        # load field location X from source layer
        # self.addParameter(
        #     QgsProcessingParameterField(
        #         name = 'location_variable_x',
        #         description = 'Choose the location variable X', 
        #         type=QgsProcessingParameterField.Numeric, 
        #         parentLayerParameterName='source_layer', 
        #         allowMultiple=False, 
        #         defaultValue='',
        #         optional = False
        #     )
        # )

        # load field location X from CSV
        # self.addParameter(
        #     QgsProcessingParameterString(
        #         name = 'location_variable_x',
        #         description = 'Input field name of coordinate X in CSV file', 
        #         defaultValue='X',
        #         optional = False
        #     )
        # )

        # load field location Y from source layer
        # self.addParameter(
        #     QgsProcessingParameterField(
        #         name = 'location_variable_y',
        #         description = 'Choose the location variable Y', 
        #         type=QgsProcessingParameterField.Numeric, 
        #         parentLayerParameterName='source_layer', 
        #         optional = False,
        #         allowMultiple=False, 
        #         defaultValue=''
        #     )
        # )

        # load field location Y from CSV 
        # self.addParameter(
        #     QgsProcessingParameterString(
        #         name = 'location_variable_y',
        #         description = 'Input field name of coordinate Y in CSV file',
        #         optional = False,
        #         defaultValue='Y'
        #     )
        # )


        # load dependent field from source layer
        self.addParameter(
            QgsProcessingParameterField(
                name = 'dependent_field',
                description = 'Select one dependent field', 
                type=QgsProcessingParameterField.Any, 
                parentLayerParameterName='source_layer', 
                allowMultiple=False, 
                defaultValue='',
                optional = False
            )
        )

        # load explanatory fields from source layer
        self.addParameter(
            QgsProcessingParameterField(
                name = 'explanatory_field',
                description = 'Select one or multiple explanatory fields', 
                type=QgsProcessingParameterField.Any, 
                parentLayerParameterName='source_layer', 
                allowMultiple=True, 
                #defaultValue= ['PctFB','PctBlack','PctRural'],
                optional = False
            )
        )
                
        # select spatial kernel type
        self.addParameter(
            QgsProcessingParameterEnum(
                name = 'kernel_type',
                description = 'Select spatial kernel type',
                options = ['Adaptive','Fixed'],
                allowMultiple = False, 
                #defaultValue = 'Adaptive',
                optional = False
                
            )
        )
        
        # select spatial kernel function
        self.addParameter(
            QgsProcessingParameterEnum(
                name = 'kernel_function',
                description = 'Select spatial kernel function',
                options = ['Gaussian', 'Bisquare', 'Exponential'],
                allowMultiple = False, 
                #defaultValue = 'bisquare',
                optional = False
                
            )
        )
        
        # select bandwidth searching method
        self.addParameter(
            QgsProcessingParameterEnum(
                name = 'bandwidth_searching',
                description = 'Select bandwidth searching method',
                options = ['Golden Section', 'Interval'],
                allowMultiple = False, 
                #defaultValue = 'Golden Section',
                optional = False
                
            )
        )

        # select bandwidth searching criterion
        self.addParameter(
            QgsProcessingParameterEnum(
                name = 'bandwidth_searching_criterion',
                description = 'Select criterion for bandwidth searching',
                options = ['AICc', 'AIC','BIC','CV'],
                allowMultiple = False, 
                #defaultValue = 'Golden Section',
                optional = False
                
            )
        )
        
        # select bandwidth-min when bandwidth searching method selecting as interval
        self.addParameter(
            QgsProcessingParameterNumber(
                name = 'bw_min',
                description = 'Bandwidth Min (Input only if equal interval method is selected)',
                type = QgsProcessingParameterNumber.Double, 
                defaultValue = None, 
                optional = True, 
                minValue = 1
            )
        )

        # select bandwidth-max when bandwidth searching method selecting as interval
        self.addParameter(
            QgsProcessingParameterNumber(
                name = 'bw_max',
                description = 'Bandwidth Max (Input only if equal interval method is selected)',
                type = QgsProcessingParameterNumber.Double, 
                defaultValue = None, 
                optional = True, 
                minValue = 1
            )
        )
        
        # select interval-value when bandwidth searching method selecting as interval
        self.addParameter(
            QgsProcessingParameterNumber(
                name = 'bw_interval',
                description = 'Interval Value (Input only if equal interval method is selected)',
                type = QgsProcessingParameterNumber.Integer, 
                defaultValue = None, 
                optional = True, 
                minValue = 1
            )
        )

        
        # self.addParameter(
        #     QgsProcessingParameterEnum(
        #         name = 'model_type',
        #         description = 'Model Type',
        #         #options = ['Gaussian', 'Binomial', 'Poisson'],
        #         options = ['Gaussian'],
        #         allowMultiple = False, 
        #         #defaultValue = 'Gaussian',
        #         optional = False
                
        #     )
        # )
        
        # #QgsProcessingParameterEnum
        # self.addParameter(
        #     QgsProcessingParameterEnum(
        #         name = 'optimization_criterion',
        #         description = 'Optimization Criterion',
        #         options = ['AICc', 'AIC','R2', 'localR2'],
        #         allowMultiple = False, 
        #         #defaultValue = 'AICc',
        #         optional = False
        #     )
        # )
        
        # output the gwr result summary
        self.addParameter(
            QgsProcessingParameterFileDestination(
                name = 'output_summary', 
                description = 'Summary File', 
                fileFilter='TXT Files (*.txt)', 
                defaultValue = None,
                optional = True
            )
        )
        
        # output the feature layer as sink to qgis directly
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.SINK_LAYER, 
                description = 'Output',
                type = QgsProcessing.TypeVectorAnyGeometry,
                defaultValue = None,
                optional = True
            )
        )

        # # output the feature layer as shapefile
        # self.addParameter(
        #     QgsProcessingParameterFileDestination(
        #         name = 'output_layer', 
        #         description = 'Output layer to shapefile',
        #         fileFilter='SHP Files (*.shp)', 
        #         defaultValue = None,
        #         optional = True
        #     )
        # )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

       # ************************************************************************************#
        # *********************************do some prep work**********************************#
        # ************************************************************************************#   
        #      
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, feedback)
        # temporary: parameter to save the output layer: SINK_LAYER
        results = {}
        # temporary: parameter to save result explanatory fields
        sink_result_name_explanatory_field = []

        # get the input layer as source
        input_featuresource = self.parameterAsSource(parameters, 'source_layer', context)
        if input_featuresource is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, 'source_layer'))
        
        # set the output gwr result summary     
        txt = self.parameterAsFileOutput(parameters, 'output_summary', context)
        
        # get features of input layer 
        features = input_featuresource.getFeatures()

        # get the features fieldname of input layer
        fieldnames = [field.name() for field in input_featuresource.fields()]
        
        # set the list as the processing variables
        layer_attributes_attr = []  # temporary: parameter to save attributes of input layer features
        layer_attributes_attr_geometry = [] # temporary: parameter to save geometry of input layer features
        location_x = [] # temporary: parameter to save the x coordinate
        location_y = [] # temporary: parameter to save the y coordinate
        g_coords = [] # temporary: parameter to save the [x y] coordinates
        g_y = []    # temporary: parameter to save the dependent field
        g_X= []     # temporary: parameter to save the explanatory fields
        
        
        # get the attributes and geometry info from input layer
        for ft in features:
            layer_attributes_attr.append(ft.attributes())
            layer_attributes_attr_geometry.append(ft.geometry())

        
        # ************************************************************************************#
        # *********************************start processing data******************************#
        # ************************************************************************************# 
        #
        # Convert the layer_attributes_attr array to GeoDataFrame format        
        layer_attributes = pd.DataFrame(layer_attributes_attr)
        # rename the layer_attributes table fields
        for i in range(len(fieldnames)):
            layer_attributes.rename(columns={i: fieldnames[i]}, inplace=True)


        # read x y from csv
        # input_layer_location_csv = pd.read_csv(parameters['location_csv'])

        # location_x = layer_attributes[parameters['location_variable_x']]
        # location_y = layer_attributes[parameters['location_variable_y']]
        # location_x = input_layer_location_csv[parameters['location_variable_x']]
        # location_y = input_layer_location_csv[parameters['location_variable_y']]
        
        # Get the geometry type of the currently selected input layer
        # geometry type: 0 point, 2 polygon
        wkbtype = input_featuresource.wkbType()
        geomtype = QgsWkbTypes.geometryType(wkbtype)
        self.geomtype = geomtype

        # judge the type of inputlayer
        # If it is point type, read it directly
        if  geomtype == QgsWkbTypes.PointGeometry:            
            # feedback.pushInfo('The current input layer is point that is: '+str(geomtype))
            # feedback.pushInfo('When it is a point type, it is: '+str(QgsWkbTypes.PointGeometry))
            if {'X', 'Y'}.issubset(layer_attributes.columns):
                feedback.pushInfo('X Y exist, directly read')
                feedback.pushInfo('processing...wait a second...')                
                location_x = layer_attributes['X']
                location_y = layer_attributes['Y']            
            else:
                feedback.pushInfo('X Y not exist, need to calculate')
                feedback.pushInfo('processing...wait a second...')
                features = input_featuresource.getFeatures()
                for ft in features:
                    # feedback.pushInfo('ft.geometry().asPoint()[0] x: '+str(ft.geometry().asPoint()[0]))
                    # feedback.pushInfo('ft.geometry().asPoint()[1] y: '+str(ft.geometry().asPoint()[1]))
                    location_x.append(ft.geometry().asPoint()[0])
                    location_y.append(ft.geometry().asPoint()[1])            
        # If it is a Polygon, calculate the centroid
        elif geomtype == QgsWkbTypes.PolygonGeometry:         
            feedback.pushInfo('The current input layer is Polygon that is: '+str(geomtype))
            feedback.pushInfo('When it is a polygon type, it is: '+str(QgsWkbTypes.PolygonGeometry))
            # calculate centroid
            features = input_featuresource.getFeatures()
            for ft in features:
                # feedback.pushInfo('***ft.geometry(): '+str(ft.geometry().centroid().asPoint()))
                location_x.append(ft.geometry().centroid().asPoint()[0])
                location_y.append(ft.geometry().centroid().asPoint()[1])                
        else:
            feedback.pushInfo('The input layer type is invalid. It should be Point or Polygon')
        
        g_coords = list(zip(location_x, location_y))
        # feedback.pushInfo('X:  ' + str(location_x))
        # feedback.pushInfo('Y:  ' + str(location_y))
        # feedback.pushInfo('g_coords:  ' + str(g_coords))
        
        # g_coords = list(zip(location_x, location_y))
        g_y = layer_attributes[parameters['dependent_field']].values.reshape((-1,1))        
        g_X = layer_attributes[parameters['explanatory_field']].values
        
        g_X = (g_X - g_X.mean(axis=0)) / g_X.std(axis=0)
        g_y = g_y.reshape((-1,1))
        g_y = (g_y - g_y.mean(axis=0)) / g_y.std(axis=0)

        # ************************************************************************************#
        # *********************************Calibrate GWR model********************************#
        # ************************************************************************************# 
        #
        # initialize some parameters of the gwr model
        var_kernel_type = [False,True]
        var_kernel_function = ['gaussian', 'bisquare', 'exponential']
        var_bandwidth_searching = ['golden_section', 'interval']
        var_bandwidth_searching_criterion = ['AICc', 'AIC','BIC','CV']
        #var_model_type = ['Gaussian()', 'Binomial()', 'Poisson()']
        #var_optimization_criterion = ['aic', 'aicc','R2', 'localR2']
        
        # get the input parameters from users
        kernel_type = var_kernel_type[parameters['kernel_type']]
        kernel_function = var_kernel_function[parameters['kernel_function']]
        bandwidth_searching = var_bandwidth_searching[parameters['bandwidth_searching']]
        bandwidth_searching_criterion = var_bandwidth_searching_criterion[parameters['bandwidth_searching_criterion']]
        #model_type = var_model_type[parameters['model_type']]
        #optimization_criterion = var_optimization_criterion[parameters['optimization_criterion']]

        # Determine whether fixed is enabled, if true, the kernel type is fixed, else adaptive
        # if kernel_type == True and bandwidth_searching == 'interval':
        if bandwidth_searching == 'interval':
            # bandwidth_searching = 'interval'
            # kernel_function = 'bisquare'  # defalut is bisquare in source code

            if all([parameters['bw_min'],parameters['bw_max'],parameters['bw_interval']]):
                bw_min = float(parameters['bw_min'])
                bw_max = float(parameters['bw_max'])
                bw_interval = float(parameters['bw_interval'])
                if bw_min > bw_max:
                    feedback.pushInfo('Wrong parameters input, bw_max must more than bw_min.')
                    return
            else:
                feedback.pushInfo('Wrong parameters input, bw_min, bw_max and bw_interval all parameters cannot be empty.')
                return 

            gwr_selector = Sel_BW(g_coords, g_y, g_X, kernel=kernel_function,fixed=kernel_type)#family=Gaussian()
            gwr_bw = gwr_selector.search(search_method=bandwidth_searching, bw_min=bw_min, bw_max=bw_max, interval=bw_interval,criterion=bandwidth_searching_criterion)# criterion useless
        else:
            gwr_selector = Sel_BW(g_coords, g_y, g_X, kernel=kernel_function, fixed=kernel_type)#family=Gaussian(),fixed=kernel_type default is false
            # Select bandwidth for kernel
            gwr_bw = gwr_selector.search(search_method=bandwidth_searching, criterion=bandwidth_searching_criterion)             
        
        # Get the gwr result
        gwr_results = GWR(g_coords, g_y, g_X, gwr_bw, kernel=kernel_function, fixed=kernel_type).fit() 

        # test the variables getting from above
        feedback.pushInfo('fixed: ' + str(kernel_type))
        feedback.pushInfo('kernel_function: ' + str(kernel_function))
        feedback.pushInfo('bandwidth_searching: ' + str(bandwidth_searching))
        feedback.pushInfo('bandwidth_searching_criterion: ' + str(bandwidth_searching_criterion))
        feedback.pushInfo('bandwidth is: ' + str(gwr_bw))
        feedback.pushInfo('dependent field is: ' + str(parameters['dependent_field']))
        #feedback.pushInfo('model_type: ' + str(model_type))
        #feedback.pushInfo('optimization_criterion: ' + str(optimization_criterion))


        # ************************************************************************************#
        # *************************************output to shapefile*********************************#
        # ************************************************************************************#
        #
        # Prepare GWR results for mapping
        
        layer_attributes['gwr_#intercept'] = gwr_results.params[:,0]
        for i in range(len(parameters['explanatory_field'])):
            result_name_explanatory_field = 'gwr_#'+ str(i+1)+'_' + parameters['explanatory_field'][i]
            sink_result_name_explanatory_field.append(result_name_explanatory_field)
            feedback.pushInfo('explanatory field is: ' + str(parameters['explanatory_field'][i]))
            layer_attributes[result_name_explanatory_field] = gwr_results.params[:,i+1]
        
        layer_attributes['geometry'] = layer_attributes_attr_geometry    

        layer_attributes['localR2'] = gwr_results.localR2
        layer_attributes['std_res'] = gwr_results.std_res
                
        # save as a shp file
        # gwr_results_summary_str = gwr_results.summary(as_str=True)

        summary = '=' * 50 + '\n'
        summary += "%-54s %20s\n" % ('Model type', gwr_results.family.__class__.__name__)
        summary += "%-60s %14d\n" % ('Number of observations:', gwr_results.n)
        summary += "%-60s %14d\n\n" % ('Number of covariates:', gwr_results.k)

        # Global Regression Results
        # summary = "%s\n" % ('Global Regression Results')
        # summary += '-' * 75 + '\n'

        # Geographically Weighted Regression (GWR) Results
        XNames = ["X" + str(i) for i in range(gwr_results.k)]
        summary += "%s\n" % ('Geographically Weighted Regression (GWR) Results')
        summary += '-' * 75 + '\n'
        if kernel_type == True:
            summary += "%-50s %20s\n" % ('Spatial kernel:', 'Fixed ' + kernel_function)
        else: 
            summary += "%-54s %20s\n" % ('Spatial kernel:', 'Adaptive ' + kernel_function)

        summary += "%-62s %12.3f\n" % ('Bandwidth used:', gwr_bw)

        # Diagnostic information
        summary += "\n%s\n" % ('Diagnostic information')
        summary += '-' * 75 + '\n'
        summary += "%-62s %12.3f\n" % ('Residual sum of squares:', gwr_results.resid_ss)
        summary += "%-62s %12.3f\n" % ( 'Effective number of parameters (trace(S)):', gwr_results.tr_S)
        summary += "%-62s %12.3f\n" % ('Degree of freedom (n - trace(S)):', gwr_results.df_model)
        summary += "%-62s %12.3f\n" % ('Sigma estimate:', np.sqrt(gwr_results.sigma2))
        summary += "%-62s %12.3f\n" % ('Log-likelihood:', gwr_results.llf)
        summary += "%-62s %12.3f\n" % ('AIC:', gwr_results.aic)
        summary += "%-62s %12.3f\n" % ('AICc:', gwr_results.aicc)
        summary += "%-62s %12.3f\n" % ('BIC:', gwr_results.bic)
        summary += "%-62s %12.3f\n" % ('R2:', gwr_results.R2)
        summary += "%-62s %12.3f\n" % ('Adjusted R2:', gwr_results.adj_R2)
        summary += "%-62s %12.3f\n" % ('Adj. alpha (95%):', gwr_results.adj_alpha[1])
        summary += "%-62s %12.3f\n" % ('Adj. critical t value (95%):', gwr_results.critical_tval(gwr_results.adj_alpha[1]))
        
        # Summary Statistics For GWR Parameter Estimates
        summary += "\n%s\n" % ('Summary Statistics For GWR Parameter Estimates')
        summary += '-' * 75 + '\n'
        summary += "%-20s %10s %10s %10s %10s %10s\n" % ('Variable', 'Mean', 'STD', 'Min', 'Median', 'Max')
        summary += "%-20s %10s %10s %10s %10s %10s\n" % ( '-' * 20, '-' * 10, '-' * 10, '-' * 10, '-' * 10, '-' * 10)
        for i in range(gwr_results.k):
            summary += "%-20s %10.3f %10.3f %10.3f %10.3f %10.3f\n" % (
                XNames[i], np.mean(gwr_results.params[:, i]), np.std(gwr_results.params[:, i]),
                np.min(gwr_results.params[:, i]), np.median(gwr_results.params[:, i]),
                np.max(gwr_results.params[:, i]))

        summary += '=' * 50 + '\n'

        with open(txt, 'w') as f:
            # f.write(gwr_results_summary_str)
            f.write(summary)
        f.close()


        # ************************************************************************************#
        # *************************************output to qgis*********************************#
        # ************************************************************************************#
        #
        # 1. Defined a variable, type is qgsfields 
        outFields = QgsFields()

        # 2. Defined the fields: the attributes fields of original layer
        for field in input_featuresource.fields():
            outFields.append(field)

        # 2.  Defined the fields: the attributes fields of gwr results
        outFields.append(QgsField('gwr_coefficient_intercept', QVariant.Double))
        outFields.append(QgsField('localR2', QVariant.Double))
        outFields.append(QgsField('std_res', QVariant.Double))        
        for i in range(len(parameters['explanatory_field'])):
            outFields.append(QgsField('gwr_coefficient_#'+ str(i+1)+'_' + parameters['explanatory_field'][i], QVariant.Double))
        
        #feedback.pushInfo('Before sink is created' )
        # 3. Create the output sink with the previously defined fields: outfields
        (sink, dest_id) = self.parameterAsSink(parameters, self.SINK_LAYER, context,
                                                outFields, input_featuresource.wkbType(), input_featuresource.sourceCrs())

        # 4. Save the all the values to sink layer
        total = 100.0 / input_featuresource.featureCount() if input_featuresource.featureCount() else 0
        features2 = input_featuresource.getFeatures()        
        for current, feature in enumerate(features2):
            #feedback.pushInfo('loop in********************' )
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            #create a new feature object
            feat = QgsFeature()

            #set fields of the feature
            feat.setFields(outFields)

            # set the attribute values 
            # Add the original attributes to the corresponding field column
            for i in range(len(fieldnames)):
                feat[fieldnames[i]] = feature[fieldnames[i]]                

            # Add the result of gwr to the corresponding field column
            feat['localR2'] = float(layer_attributes['localR2'][current])
            feat['std_res'] = float(layer_attributes['std_res'][current])
            feat['gwr_coefficient_intercept'] = float(layer_attributes['gwr_coefficient_intercept'][current])
            for i in range(len(sink_result_name_explanatory_field)):
                feat[sink_result_name_explanatory_field[i]] = float(layer_attributes[sink_result_name_explanatory_field[i]][current])

            # set the geometry info
            feat.setGeometry(feature.geometry())

            #add feature to sink
            sink.addFeature(feat, QgsFeatureSink.FastInsert) 
            
            # back to dest_id
            results[self.SINK_LAYER] = dest_id

            feedback.setProgress(int(current * total))

        # to get hold of the layer in post processing:
        self.dest_id=dest_id

        return results
  
    def postProcessAlgorithm(self, context, feedback):
        retval = super().postProcessAlgorithm(context, feedback)
        output = QgsProcessingUtils.mapLayerFromString(self.dest_id, context)
        if  self.geomtype == QgsWkbTypes.PointGeometry: 
            style_path = os.path.join(os.path.dirname(__file__), 'layer_style', 'mgwr_point.qml')
        elif self.geomtype == QgsWkbTypes.PolygonGeometry:
            style_path = os.path.join(os.path.dirname(__file__), 'layer_style', 'mgwr_poly.qml')
        else:
            pass

        # feedback.pushInfo('path is********************' + str(path))
        output.loadNamedStyle(style_path)
        output.triggerRepaint()

        return {self.SINK_LAYER: self.dest_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Geographically Weighted Regression'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return GWRAlgorithm()
    
    def shortHelpString(self): 
        return '''<html><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Document</title><style>        ol {            padding-left: 0.25em;            margin-left: 0.25em;        }        ol > li::marker {            font-weight: bold;        }        .interval_inputs {            margin-left: 1.25em;            counter-reset: list;        }        .interval_inputs > li {            list-style: none;        }        .interval_inputs > li:before {            content: counter(list, number)")";            counter-increment: list;            font-weight: bold;        }        .kernel_type {            display: block;            max-width: 90vw;            max-height: 250px;        }</style></head><body><h2>Algorithm Description</h2><p>Geographically Weighted Regression (GWR) is a spatial regression technique used to evaluate a local model of the         variable or process by fitting a regression equation to every feature in the dataset. Generally, it is a local         form of linear regression used to model spatially varying relationships.</p><h3>Input Layer</h3><p>Select the input layer containing all the fields used to build local regression model.</p><h3>Input Parameters</h3><p>Select only one dependent variable and one or multiple explanatory variables (a.k.a. independent variables).</p><ul><ol><li><b>Dependent Variable</b>: The field containing values dependent on explanatory variable(s) in regression model</li><li><b>Explanatory Variable</b>: The field(s) representing independent explanatory variable(s) in regression model.</li></ol></ul><h3>Spatial Kernel Type</h3><p>Select the kernel type, either fixed or adaptive, usually depending on how observations distribute in the region of interest.</p><ul><ol><li><b>Fixed</b>: The spatial context used to solve each local regression analysis is a fixed                distance. Fixed kernel type is suggested when observations distribute evenly in the research region.</li><li><b>Adaptive</b>: The spatial context is a specified number of nearest neighbors.                Where feature distribution is dense, the spatial context is smaller, while where feature distribution is                sparse, the spatial context is larger.</li></ol></ul><h3>Spatial Kernel Function</h3><p>Select one kernel function to calculate weight matrix for each observation.</p><ul><ol><li><b>Gaussian</b><li><b>Exponential</b><li><b>Bisquare</b></ol></ul><p><i><b>Note:</b>A potential issue with the Gaussian and Exponential kernel functions is that all observations retain non-zero        weight, regardless of their distance from the calibration location. This means that even faraway observations        can remain influential for moderate-to-large bandwidth parameters.<p>To avoid the issue above, the default kernel function is set to bi-square kernel. Moreover, bi-square kernel         has a much more intuitive interpretation, where the bandwidth parameter is the distance or number of nearest neighbors         away in space so that the remaining observations will not affect in searching optimal bandwidth parameters.</p></i></p><h3>Bandwidth Searching</h3><p>Specify which method to use in order to search for an optimal bandwidth.</p><ul><ol><li><p><b>Golden Section Search Method</b>: The golden section search is a technique for finding an extremum (minimum or maximum) of a                function inside a specified interval. In GWR this method helps searching for the optimal bandwidth.</p></li><li><p><b>Equal Interval Method</b>: The equal interval is an intuitive method to search for the optimal bandwidth since it simply                checks each bandwidth between the predefined minimum and maximum bandwidth based on a fixed user-input interval.<b>Therefore,                 if user chooses to use equal interval method, it is mandatory to fill the three optional fields</b>:<ol class="interval_inputs"><li><b>Bandwidth Min</b>: Bandwidth searching will start from this number.</li><li><b>Bandwidth Max</b>: Bandwidth searching will end before this number.</li><li><b>Interval</b>: Interval increment used in bandwidth search.</li></ol><b><i><p><font color="red">Important Note: Pay attention to the units of bandwidth, meters for fixed kernel type, number of nearest neighbors for adaptvie one.</font></p></b></i></li></ol></ul><h3>Bandwidth Searching Criterion</h3><p>Specify how the extent of the kernel should be determined.</p><ul><ol><li><b>CV</b>: Cross validation criterion compares the model residuals based on different bandwidths and chooses the                optimal solution.</li><li><b>AIC</b>: Akaike information criterion estimates the quality of each model, relative to each of the other                models.</li><li><b>AICc</b>: Corrected Akaike information criterion is an improved version of AIC, as well as the mostly                suggested one, since it penalizes smaller bandwidths that result in more complex models that consume                more degrees of freedom.</li><li><b>BIC</b>: Bayesian information criterion shares the same methodology with AIC, but performs better at model selection.</li></ol></ul><p align="right">Plugin Authors: Gao & Song</p><p align="right">Algorithm Version: 1.2</p></body></html>'''
