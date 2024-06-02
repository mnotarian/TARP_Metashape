import Metashape, os, glob

path = Metashape.app.getExistingDirectory("Please choose the folder with .psx files:")
print("Overnight script started...")
doc = Metashape.app.document
doc.clear()

TYPE = ".PSX"
project_list = [file for file in glob.iglob(path + "/**/*.*" , recursive = True) if (file.upper().endswith(TYPE) and os.path.isfile(file))]

for project_name in project_list:

    doc.open(project_name)
    chunk = doc.chunks[0]

    #downscale 1 = ultra high, 2 = high, 4 = medium, 8 = low, 16 = lowest
    chunk.buildDepthMaps(downscale = 2, filter_mode = Metashape.AggressiveFiltering, reuse_depth=False)
    doc.save()
    chunk.buildModel(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation, source_data = Metashape.DepthMapsData, face_count=Metashape.CustomFaceCount, face_count_custom=2500000, vertex_colors=True, replace_asset=True, volumetric_masks=False)
    doc.save()
    chunk.buildUV(mapping_mode=Metashape.GenericMapping, page_count=1, texture_size=8192)
    chunk.buildTexture(blending_mode=Metashape.MosaicBlending, texture_size=8192, fill_holes=True, ghosting_filter=True)
    doc.save()
    chunk.buildOrthomosaic(surface_data=Metashape.ModelData, blending_mode=Metashape.MosaicBlending, fill_holes=True, ghosting_filter=False, replace_asset=True)
    doc.save()
    chunk.buildDem(source_data=Metashape.ModelData, interpolation=Metashape.EnabledInterpolation, replace_asset=True)
    doc.save()
    filename = os.path.splitext(os.path.basename(project_name))[0]
    chunk.exportModel(path="C:/TARP_Testing/PLY/" + filename + ".ply", texture_format=Metashape.ImageFormatJPEG, save_texture=True, save_normals=True, save_colors=True, format=Metashape.ModelFormatPLY, crs=Metashape.CoordinateSystem("EPSG::32632"), shift=Metashape.Vector((452000, 4413000, 0)), clip_to_boundary=True)
    compression = Metashape.ImageCompression()
    compression.tiff_compression = Metashape.ImageCompression.TiffCompressionJPEG
    compression.jpeg_quality = 50
    chunk.exportRaster(path="C:/TARP_Testing/Orthos/" + filename + ".jpg", format=Metashape.RasterFormatTiles, image_format=Metashape.ImageFormatJPEG, source_data = Metashape.OrthomosaicData, image_compression=compression, save_world=True, clip_to_boundary=True)
    compression.tiff_compression = Metashape.ImageCompression.TiffCompressionLZW
    chunk.exportRaster(path="C:/TARP_Testing/Orthos/" + filename + ".tif", format=Metashape.RasterFormatTiles, source_data = Metashape.OrthomosaicData, image_format=Metashape.ImageFormatTIFF, image_compression=compression, save_world=False, clip_to_boundary=True)
    chunk.exportRaster(path="C:/TARP_Testing/DEM/" + filename + "_dem.tif", format=Metashape.RasterFormatTiles, source_data = Metashape.ElevationData, image_format=Metashape.ImageFormatTIFF, save_world=False, clip_to_boundary=True)
    print("Processed project: " + filename)
	
print("Script finished.")