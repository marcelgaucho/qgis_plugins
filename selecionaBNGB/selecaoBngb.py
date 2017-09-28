# -*- coding: utf-8 -*-
"""
/***************************************************************************
 selecionaBNGB
                                 A QGIS plugin
 Este plugin irá selecionar a mesma feição na tabela de uma Base através de seu ID
                              -------------------
        begin                : 2016-07-18
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Marcel
        email                : marcel.rotunno@ibge.gov.br
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QColor
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from selecaoBngb_dialog import selecionaBNGBDialog
import os.path
from PyQt4.QtSql import *
from qgis.core import *






class selecionaBNGB:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # self.plugin_dir fica sendo o diretório onde o plugin está localizado  
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'selecionaBNGB_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = selecionaBNGBDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Seleciona BNGB')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'selecionaBNGB')
        self.toolbar.setObjectName(u'selecionaBNGB')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('selecionaBNGB', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/selecionaBNGB/icon.png'
        action = self.add_action(
            icon_path,
            text=self.tr(u'Seleciona mesma feição na Base'),
            callback=self.run,
            parent=self.iface.mainWindow())

        

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Seleciona BNGB'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        

    def run(self):
        """Run method that performs all the real work"""
        # Cria variável com Camada com o nome t_interface
        try:
            camadaAtiva = QgsMapLayerRegistry.instance().mapLayersByName("t_interface")[0]
        # Se nome da camada selecionada for diferente de t_interface dá erro
        except:
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Na LEGENDA precisa existir camada com nome t_interface')
            return
        
        print "Ok"
        
        # Armazena seleção de t_interface
        selecao = camadaAtiva.selectedFeatures()
        # Se selecionar mais de 1 elemento ocorre erro
        if len(selecao) != 1:
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Selecionar apenas 1 feicao')
        else:
            # Cria mesma URI da conexão (banco e usuário) que adicionou a camada ativa
            uri = QgsDataSourceURI(camadaAtiva.dataProvider().dataSourceUri())
            # print uri.uri()
                
            # nome_visao é o nome da visão que será adicionada
            if selecao[0]['tp_geom'].lower() == 'poligono':
                nome_visao = selecao[0]['nm_sigla_categoria'] + '_' + selecao[0]['nm_classe'].lower() + '_' + 'a'
            else:
                nome_visao = selecao[0]['nm_sigla_categoria'] + '_' + selecao[0]['nm_classe'].lower() + '_' + selecao[0]['tp_geom'].lower()[0]
                
            # Identificação da Visão de Tabela que será adicionada
            uri.setDataSource(selecao[0]['nm_esquema_base'], nome_visao, "geom") #, "id_objeto = " + str(selecao[0]['id_objeto_producao'])) 
            uri.setKeyColumn('id_objeto')
                
            # print uri.uri()
                
            # Adiciona camada apenas se ela não existir na legenda 
            camadasAbertas = self.iface.legendInterface().layers()
            
            # Variável para determinar se a camada existe. Inicialmente assumimos que ela não existe
            camadaExiste = False
            for camadaLegenda in camadasAbertas:
                try:
                    uri_camadaLegenda = QgsDataSourceURI(camadaLegenda.dataProvider().dataSourceUri())
                    if uri.uri() == uri_camadaLegenda.uri():
                        camadaExiste = True
                        camada_adicionada = camadaLegenda
                        break
                except:
                    pass
            
            # Caso a camada não exista vamos adicioná-la
            if not camadaExiste:
                # Adição da tabela na interface do QGIS
                camada_adicionada = self.iface.addVectorLayer(uri.uri(), nome_visao, "postgres")
                
                
            # Seleciona feição correspondente ao id da feição selecionada em t_interface
            nova_selecao = camada_adicionada.getFeatures(QgsFeatureRequest().setFilterExpression(u'"id_objeto" = ' + str(selecao[0]['id_objeto_producao'])))
            camada_adicionada.setSelectedFeatures([feicao.id() for feicao in nova_selecao])

            # Sistema de coordenadas atual (on-the-fly) precisa ser projetado     
            mapCanvasSrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
            
            # Sistema de coordenadas do raster
            camadaSrs = camada_adicionada.crs()
            
            # Transformação entre o sistema de coordenadas atual (on-the-fly) e o sistema de coordenadas do raster
            srsTransform = QgsCoordinateTransform(camadaSrs, mapCanvasSrs)
        
            # Cria retângulo envolvente à selecão da nova camada e faz zoom para ela. Nova camada fica sendo a camada ativa 
            box = camada_adicionada.boundingBoxOfSelected()
            box = srsTransform.transform(box)
            # print type(box)
            self.iface.mapCanvas().setExtent(box)
            self.iface.mapCanvas().refresh()
                
            self.iface.setActiveLayer(camada_adicionada)


                
            
            