# -*- coding: utf-8 -*-
"""
/***************************************************************************
 selecionaBNGB
                                 A QGIS plugin
 Este plugin irá selecionar a mesma feição na tabela de uma Base através de seu ID
                             -------------------
        begin                : 2016-07-18
        copyright            : (C) 2016 by Marcel
        email                : marcel.rotunno@ibge.gov.br
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
    """Load selecionaBNGB class from file selecionaBNGB.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .selecaoBngb import selecionaBNGB
    return selecionaBNGB(iface)
