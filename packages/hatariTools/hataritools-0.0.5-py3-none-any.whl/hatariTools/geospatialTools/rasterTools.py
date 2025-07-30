import rasterio
import geopandas as gpd
from shapely.geometry import Point
from rasterio.features import geometry_mask
from typing import Union

def modifyRasterwithRasterOnMask(wholeRasterPath:str,
                                 partialRasterPath:str,
                                 maskLayerPath:str,
                                 modifiedRasterPath:str):
    wholeRaster = rasterio.open(wholeRasterPath)
    partialRaster = rasterio.open(partialRasterPath)
    maskLayerGeom = gpd.read_file(maskLayerPath).iloc[0].geometry

    wholeArray = wholeRaster.read(1)
    wholeProfile = wholeRaster.profile

    ncols = wholeRaster.width
    nrows = wholeRaster.height

    for row in range(nrows):
        for col in range(ncols):
            x,y = wholeRaster.xy(row,col)
            pointXy = Point(x,y)
            if pointXy.intersects(maskLayerGeom):
                sampleArray = list(partialRaster.sample([(x,y)]))[0]
                wholeArray[row,col] = sampleArray.tolist()[0]

    with rasterio.open(modifiedRasterPath, "w", **wholeProfile) as dst:
        dst.write(wholeArray, 1)

def modifyRasterwithElevOnMask(wholeRasterPath:str,
                               elevValue:Union[int,float],
                               maskLayerPath:str,
                               modifiedRasterPath:str):
    wholeRaster = rasterio.open(wholeRasterPath)
    maskLayerGeom = gpd.read_file(maskLayerPath).iloc[0].geometry

    wholeArray = wholeRaster.read(1)
    wholeProfile = wholeRaster.profile

    ncols = wholeRaster.width
    nrows = wholeRaster.height

    for row in range(nrows):
        for col in range(ncols):
            x,y = wholeRaster.xy(row,col)
            pointXy = Point(x,y)
            if pointXy.intersects(maskLayerGeom):
                wholeArray[row,col] = elevValue

    with rasterio.open(modifiedRasterPath, "w", **wholeProfile) as dst:
        dst.write(wholeArray, 1)