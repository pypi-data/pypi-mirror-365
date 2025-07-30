
#import geopandas as gpd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import fiona
import rasterio
from rasterio.plot import show
import geopandas as gpd
from shapely.geometry import Polygon, Point

from skimage.feature import match_template
from mpl_toolkits.axes_grid1 import make_axes_locatable
from skimage.feature import match_template
from sklearn.cluster import Birch

from hatariTools.utils import (isRunningInJupyter, 
                    printBannerHtml, 
                    printBannerText)
    
class cropCounting():
    def __init__(self):
        self.rasterPath = ''
        self.shapePath = ''
        self.pointRatio = 10
        self.surveyRowCol = []
        self.selectedBand = ''
        self.matchXYList = []

        #insert banner
        if isRunningInJupyter():
            printBannerHtml()
        else:
            printBannerText()

        print('\n/-------------------------------------------/')
        print('\nThe crop recognition engine has been started')
        print('\n/-------------------------------------------/')
        

    def defineRaster(self, rasterPath):
        #open raster file
        cropRaster = rasterio.open(rasterPath)
        print('\n/-------------------------------------------/')
        print('\nCRS of Raster Data: ' + str(cropRaster.crs))
        print('Number of Raster Bands: ' + str(cropRaster.count))
        print('Interpretation of Raster Bands: ' + str(cropRaster.colorinterp))
        self.cropRaster = cropRaster
        #self.rasterBand = cropRaster.read(self.bandNumber)
        self.redBand = cropRaster.read(1)
        self.greenBand = cropRaster.read(2)
        self.blueBand = cropRaster.read(3)

        #explore the raster units and resolution
        units = cropRaster.crs.linear_units
        res = cropRaster.res[0]
        print("Raster unit is %s and resolution is %.2f \n"%(units,res))
        print('/-------------------------------------------/\n')
        self.rasterRes = res

        bounds = cropRaster.bounds
        self.boundPoly = Polygon([(bounds.left, bounds.top),
                                (bounds.left, bounds.bottom),
                                (bounds.right, bounds.bottom),
                                (bounds.right, bounds.top)])
        
    def definePoints(self, pointPath):
        pointDf = gpd.read_file(pointPath)
        print('\n CRS of Point Data:' + str(pointDf.crs))
        if self.cropRaster.crs.to_epsg() == pointDf.crs.to_epsg():
            xList = pointDf.geometry.x.to_list()
            yList = pointDf.geometry.y.to_list()
            self.pointCoords = list(zip(xList,yList))
            self.pointDf = pointDf
        else:
            print("[ERROR] The coordinate reference system of the raster and points don't match")
        
    def plotRasterandPoints(self):
        coordList = [item['geometry']['coordinates'] for item in self.pointData]
        xCoord = [pair[0] for pair in coordList ]
        yCoord = [pair[1] for pair in coordList ]
        
        #show point and raster on a matplotlib plot
        fig, ax = plt.subplots(figsize=(18,18))
        ax.scatter(xCoord,yCoord, color='orangered')
        show(self.cropRaster, ax=ax)
        #return fig
        
    def getPointRowCol(self):
        self.surveyRowCol = []
        for index, point in enumerate(self.pointCoords):
            row,col = self.cropRaster.index(point[0],point[1])
            print("Point N°:%d corresponds to row, col: %d, %d"%(index,row,col))
            self.surveyRowCol.append({
                'index':index,
                'row':row,
                'col':col,
                'array':self.selectedBand[row-self.pointRatio:row+self.pointRatio, 
                                        col-self.pointRatio:col+self.pointRatio]
            })
    
    def plotReferenceImages(self):
        fig, ax = plt.subplots(1, len(self.surveyRowCol),figsize=(20,5))
        for index, item in enumerate(self.surveyRowCol):
            imx = ax[index].imshow(item['array'], cmap='Spectral' )
            divider = make_axes_locatable(ax[index])
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(imx, cax=cax, orientation='vertical')
            #ax[index].plot(item['col'],item['row'],
            #               color='red', linestyle='dashed', marker='+',
            #               markerfacecolor='blue', markersize=8)
            #ax[index].set_xlim(col-radio,col+radio)
            #ax[index].set_ylim(row-radio,row+radio)
            ax[index].axis('off')
            ax[index].set_title(item['index'])
        #fig.colorbar()
        
    def singleMatchTemplate(self, item, outPath):
        templateArray = self.surveyRowCol[item]['array']
        matchTemplate = match_template(self.selectedBand, templateArray,
                                       pad_input=True)
        profile = self.cropRaster.profile
        profile.update(count=1, dtype=rasterio.float64)
        outRaster = rasterio.open(outPath,'w',**profile)
        outRaster.write(matchTemplate,1)
        outRaster.close()
        return matchTemplate
        
    def singleMatchHistogram(self, item, interval=None):
        templateArray = self.surveyRowCol[item]['array']
        matchTemplate = match_template(self.selectedBand, templateArray,
                                       pad_input=True)
        sns.set(style="whitegrid", palette="muted", font_scale=1.2)

        # Create histogram
        sns.histplot(matchTemplate.flatten(), bins=30, kde=True, color="royalblue", 
                     edgecolor="white")

        # Customize plot
        plt.title("Histogram")
        plt.xlabel("Match Value")
        plt.ylabel("Frequency")
        
        if interval:
            plt.xlim(interval[0],interval[1])

        # Show plot
        plt.show()
        
    def pointsMatchTemplate(self, method, value):

        matchTemplateList = []

        for index, item in enumerate(self.surveyRowCol):
            print('Processing image Nº %d'%index)
            matchTemplate = match_template(self.selectedBand, item['array'],
                                           pad_input=True)
            if method == 'quantile':
                templateFiltered = np.where(matchTemplate > 
                                        np.quantile(matchTemplate,value))
            elif method == 'threshold':
                templateFiltered = np.where(matchTemplate > value)
            else:
                print('Incorrect method')
                break
                
            for item in zip(templateFiltered[0],templateFiltered[1]):
                x, y = self.cropRaster.xy(item[0], item[1])
                self.matchXYList.append((x,y))
        #return self.matchXYList

        
    def saveMatchShp(self,outShpPath, limit=None):
        cropSchema = {'properties':{'id': 'int'}, 'geometry': 'Point'}
        cropShp = fiona.open(outShpPath, mode='w', 
                     driver='ESRI Shapefile', schema=cropSchema,
                     crs = self.cropRaster.crs)
        if limit:
            for index, point in enumerate(self.matchXYList):
                if index < limit:
                    cropShp.write({
                        'geometry' : {'type':'Point', 'coordinates':tuple(point)},
                        'properties' : {'id':index}
                    }) 
                else:
                    break
        else:
            for index, point in enumerate(self.matchXYList):
                cropShp.write({
                    'geometry' : {'type':'Point', 'coordinates':tuple(point)},
                    'properties' : {'id':index}
                }) 
        cropShp.close()
        
    def plotAllTemplates(self):
        fig, ax = plt.subplots(figsize=(20, 20))
        matchXYArray = np.array(self.matchXYList)
        ax.scatter(matchXYArray[:,0],matchXYArray[:,1], marker='o',
                   c='orangered', s=100, alpha=0.25)
        show(self.cropRaster, ax=ax)
        plt.show()

    def birchFilter(self):
        threshold=self.cropRaster.res[0]*self.pointRatio
        brc = Birch(branching_factor=10000, n_clusters=None, 
                    threshold=threshold, compute_labels=True)
        matchXYSet = list(set(self.matchXYList))
        
        buffPoly = self.boundPoly.buffer(-self.pointRatio*self.rasterRes)
        matchXYBuff = []
        for match in matchXYSet:
            matchPoint = Point(match)
            if matchPoint.intersects(buffPoly):
                matchXYBuff.append(match)

        matchXYArray = np.array(matchXYBuff)

        brc.fit(matchXYArray)
        self.birchPoint = brc.subcluster_centers_
        
    def saveBirchCsv(self,outCsvPath):  
        np.savetxt(outCsvPath, self.birchPoint, delimiter=",")
        
    def saveBirchShp(self,outShpPath):
        cropSchema = {'properties':{'id': 'int'}, 'geometry': 'Point'}
        cropShp = fiona.open(outShpPath, mode='w', 
                     driver='ESRI Shapefile', schema=cropSchema,
                     crs = self.cropRaster.crs)
        for index, point in enumerate(self.birchPoint):
            cropShp.write({
                'geometry' : {'type':'Point', 'coordinates':tuple(point)},
                'properties' : {'id':index}
            }) 
        cropShp.close()
        
    def plotBirchPoints(self):
        fig = plt.figure(figsize=(20, 20))
        ax = fig.add_subplot(111)
        ax.scatter(self.birchPoint[:,[0]],self.birchPoint[:,[1]],
                   marker='o',color='crimson', edgecolors='white',
                   s=100, label='Recognized Crops', alpha=0.7)
        ax.scatter(self.pointDf.geometry.x, self.pointDf.geometry.y,
                    marker='o',color='teal', edgecolors='white',
                    s=100, label='Sample Crops')
        show(self.cropRaster, ax=ax)
        ax.legend()
        plt.show()
