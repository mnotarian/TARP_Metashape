import Metashape, os, glob

def get_marker(chunk, label):
    for marker in chunk.markers:
        if marker.label == label:
             return marker
    return None

path = Metashape.app.getExistingDirectory("Please choose the folder with .psx files:")
print("Overnight script started...")
doc = Metashape.app.document
doc.clear()

TYPE = ".PSX"
project_list = [file for file in glob.iglob(path + "/**/*.*" , recursive = True) if (file.upper().endswith(TYPE) and os.path.isfile(file))]

for project_name in project_list:

    doc.open(project_name)
    chunk = doc.chunks[0]

    chunk.detectMarkers(target_type=Metashape.CircularTarget12bit, tolerance=50)
    doc.save()
    #downscale 0 - Highest, 1 - High, 2 - Medium, 4 - Low, 8 - Lowest
    chunk.matchPhotos(downscale=1, generic_preselection=True, reference_preselection = True, reference_preselection_mode=Metashape.ReferencePreselectionEstimated, keypoint_limit=60000, tiepoint_limit=10000, guided_matching=False)
    chunk.alignCameras(adaptive_fitting=True)
    doc.save()
    m4 = get_marker(chunk, "target 4")
    m5 = get_marker(chunk, "target 5")
    chunk.addScalebar(m4, m5)
    m6 = get_marker(chunk, "target 6")
    chunk.addScalebar(m5, m6)
    m12 = get_marker(chunk, "target 12")
    m13 = get_marker(chunk, "target 13")
    chunk.addScalebar(m12, m13)
    m14 = get_marker(chunk, "target 14")
    chunk.addScalebar(m13, m14)
    m20 = get_marker(chunk, "target 20")
    m21 = get_marker(chunk, "target 21")
    chunk.addScalebar(m20, m21)
    m22 = get_marker(chunk, "target 22")
    chunk.addScalebar(m21, m22)
    chunk.scalebar_accuracy = 0.0001
    chunk.sortScalebars()
    chunk.scalebars[0].reference.distance = 0.25036
    chunk.scalebars[0].reference.enabled = True
    chunk.scalebars[1].reference.distance = 0.25006
    chunk.scalebars[1].reference.enabled = True
    chunk.scalebars[2].reference.distance = 0.25026
    chunk.scalebars[2].reference.enabled = True
    chunk.scalebars[3].reference.distance = 0.25011
    chunk.scalebars[3].reference.enabled = True
    chunk.scalebars[4].reference.distance = 0.25026
    chunk.scalebars[4].reference.enabled = True
    chunk.scalebars[5].reference.distance = 0.25012
    chunk.scalebars[5].reference.enabled = True
    chunk.updateTransform()
    chunk.crs = Metashape.CoordinateSystem("EPSG::32632")
    chunk.importReference("C:/TARP_Testing/Trench 10000/GCPs_2023_EPSG_32632_10000 UPDATED AFTER TRENCH EXPANSION 6-20-23.csv", delimiter=",", columns="nxyz", create_markers=False,
                          items=Metashape.ReferenceItemsMarkers, crs=Metashape.CoordinateSystem("EPSG::32632"))
    chunk.updateTransform()
    doc.save()
    if "10000" in project_name:
        #new shapes don't need the outer outer boundary for use in aligning the reconstruction region
        chunk.importShapes(path="C:/SynologyDrive/Models_to_process/Bounding Regions/10000_bounding_UPDATED_with_Extension_6-20-23.shp",replace=False,boundary_type=Metashape.Shape.BoundaryType.OuterBoundary)
        print ("imported Trench 10000 boundary")
    else:
        if "9000" in project_name:
            chunk.importShapes(path="C:/SynologyDrive/Models_to_process/Bounding Regions/9000_bounding_UPDATED_with_Extension_7-3-23.shp",replace=False,boundary_type=Metashape.Shape.BoundaryType.OuterBoundary)
            print ("imported Trench 9000 boundary")
        else:
            chunk.importShapes(path="C:/SynologyDrive/Models_to_process/Bounding Regions/8000_bounding.shp",replace=False,boundary_type=Metashape.Shape.BoundaryType.OuterBoundary)
            print ("imported Trench 8000 boundary")

    if "10000" in project_name:
        T0 = Metashape.Matrix([[0.09148898889661944, 0.6175052850948705, 0.0770160716796606, 4848544.124156246],
                               [-0.6165210325712953, 0.07936939503942445, 0.09600418238123326, 719530.9193362945],
                               [0.08453442384193306, -0.08945506982484616, 0.6168194299588282, 4067359.4307051036],
                               [0.0, 0.0, 0.0, 1.0]])
        T = Metashape.app.document.chunk.transform.matrix.inv() * T0

        R = Metashape.Matrix([[T[0, 0], T[0, 1], T[0, 2]], [T[1, 0], T[1, 1], T[1, 2]], [T[2, 0], T[2, 1], T[2, 2]]])

        scale = R.row(0).norm()
        R = R * (1 / scale)

        R0 = Metashape.Matrix([[-0.9996215604496385, 0.00793491750996221, -0.026339570390198127],
                               [-0.023512921292570314, -0.7434491800998473, 0.6683789786798762],
                               [-0.014278599949557403, 0.6687453578851783, 0.7433544026172882]])

        new_region = Metashape.Region()
        new_region.rot = R * R0
        c = T.mulp(Metashape.Vector([-6.0098288041687935, -0.9958430582827799, -6.2225569856919005]))
        new_region.center = c
        new_region.size = Metashape.Vector([32.355807031247366, 7.118239791236585, 12.493753072369682]) * scale / 1.

        Metashape.app.document.chunk.region = new_region
        print("imported Trench 10000 reconstruction region")
    #else:
        #if "9000" in project_name:
            #insert script here for 9000
        #else:
            #insert script here for 8000

    doc.save()
    filename = os.path.splitext(os.path.basename(project_name))[0]
    print("Processed project: " + filename)
	
print("Script finished. Manually check targets and ground control points.")