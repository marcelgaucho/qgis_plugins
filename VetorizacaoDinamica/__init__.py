# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VetorizacaoDinamica
                                 A QGIS plugin
 Vai vetorizar achando uma estrada, interpolando os pontos inicial e final
                             -------------------
        begin                : 2016-09-01
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
    """Load VetorizacaoDinamica class from file VetorizacaoDinamica.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .vetorizacaoDinamica import VetorizacaoDinamica
    return VetorizacaoDinamica(iface)
