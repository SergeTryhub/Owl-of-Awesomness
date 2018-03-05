from lxml import etree
from lxml.builder import E

camera_matrix=[[ 532.80990646 ,0.0,342.49522219],[0.0,532.93344713,233.88792491],[0.0,0.0,1.0]]
dist_coeff = [-2.81325798e-01,2.91150014e-02,1.21234399e-03,-1.40823665e-04,1.54861424e-01]

def triada(itm):
    a, b, c = itm
    return E.Triada(a = str(a), b = str(b), c = str(c))

camera_matrix_xml = E.CameraMatrix(*map(triada, camera_matrix))
dist_coeff_xml = E.DistCoef(*map(E.Coef, map(str, dist_coeff)))


xmldoc = E.CameraData(camera_matrix_xml, dist_coeff_xml)

fname = "data.xml"
with open(fname, "w") as f:
    f.write(etree.tostring(xmldoc, pretty_print=True))
