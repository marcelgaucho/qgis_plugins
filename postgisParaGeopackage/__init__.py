# -*- coding: utf-8 -*-
"""
/***************************************************************************
 postgisParaGeopackage
                                 A QGIS plugin
 Irá converter um recorte de uma base para GeoPackage
                             -------------------
        begin                : 2016-07-29
        copyright            : (C) 2016 by Marcel
        email                : marcelsorri@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load postgisParaGeopackage class from file postgisParaGeopackage.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .conversaoBaseGeopackage import postgisParaGeopackage
    return postgisParaGeopackage(iface)
