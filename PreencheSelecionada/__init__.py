# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PreencheSelecionada
                                 A QGIS plugin
 O plugin irá preencher a tabela t_interface com a tupla selecionada
                             -------------------
        begin                : 2017-03-28
        copyright            : (C) 2017 by Marcel Rotunno
        email                : marcel.rotunno@gmail.com
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
    """Load PreencheSelecionada class from file PreencheSelecionada.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .preenche_selecionada import PreencheSelecionada
    return PreencheSelecionada(iface)
