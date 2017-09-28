# -*- coding: utf-8 -*-
"""
/***************************************************************************
 postgisParaGeopackage
                                 A QGIS plugin
 Irá converter um recorte de uma base para GeoPackage
                              -------------------
        begin                : 2016-07-29
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Marcel
        email                : marcelsorri@gmail.com
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
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QColor, QFileDialog

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from conversaoBaseGeopackage_dialog import postgisParaGeopackageDialog
import os.path

# Importa classes dos módulos para lidar com SQL, do Qt, e do núcleo do QGIS
from PyQt4.QtSql import *
from qgis.core import *

# Importa módulo subprocess para rodar linha de comando e classe expanduser 
# para ir para diretório do usuário na hora de escolher o shapefile
import subprocess
from os.path import expanduser


class postgisParaGeopackage:
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
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'postgisParaGeopackage_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = postgisParaGeopackageDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&convertePostgisParaGeopackage')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'postgisParaGeopackage')
        self.toolbar.setObjectName(u'postgisParaGeopackage')

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
        return QCoreApplication.translate('postgisParaGeopackage', message)


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
        self.dlg.botaoShape.clicked.connect(self.selecionar_shape)
        self.dlg.botaoSaida.clicked.connect(self.selecionar_saida)
        
        icon_path = ':/plugins/postgisParaGeopackage/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Exporta recorte de banco para GeoPackage'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&convertePostgisParaGeopackage'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    
    def selecionar_shape(self):
        nomeShape = QFileDialog.getOpenFileName(self.dlg, "Selecione o shapefile para recorte ", expanduser("~"), '*.shp')
        self.dlg.linhaShape.setText(nomeShape)
        return

    def selecionar_saida(self):
        nomeGeopackage = QFileDialog.getSaveFileName(self.dlg, "Selecione o arquivo GeoPackage de saida ", expanduser("~"), '*.gpkg')
        self.dlg.linhaGeopackage.setText(nomeGeopackage)
        return
        
    def run(self):
        """Roda método que faz todo o trabalho real"""
        
        """Executa tarefas antes de apertar o OK da janela do Complemento"""        
        camadaAtiva = self.iface.activeLayer()
        # Se não tiver nenhuma camada selecionada acusa erro
        try:
            provedor = camadaAtiva.dataProvider()
        except:
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Selecione alguma camada')
            return
        
        # Se não for camada Postgres também acusa erro
        if provedor.name() != 'postgres':
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Selecione uma camada com conexao PostGIS')
            return
        else:
            # Adiciona opção para exportação na comboBox: Tabelas ou Visões 
            self.dlg.visaoOuTabela.clear()
            tabelas_visoes_opcao = ['Visoes', 'Tabelas']
            self.dlg.visaoOuTabela.addItems(tabelas_visoes_opcao)
            
            # Cria mesma URI da conexão (banco e usuário) que adicionou a camada do banco Postgres
            uri = QgsDataSourceURI(camadaAtiva.dataProvider().dataSourceUri())
            
            # Cria uma conexão ao Postgres através de QSqlDatabase - QPSQL se refere ao Postgres
            db = QSqlDatabase.addDatabase("QPSQL");
            
            db.setHostName(uri.host())
            db.setDatabaseName(uri.database())
            db.setPort(int(uri.port()))
            db.setUserName(uri.username())
            db.setPassword(uri.password())
            
            # Abre conexão ao banco de dados para adicionar os esquemas que têm tabelas espaciais contidos lá
            if db.open():
                # print 'Opened %s' % uri.uri()
                # Executa uma consulta que pega os esquemas nos quais há uma tabela com a coluna 'geom'
                consulta = db.exec_("SELECT DISTINCT table_schema FROM information_schema.columns WHERE column_name = 'geom'") # pega esquemas da geometry_columns: select distinct f_table_schema from t_geometry_columns
                
                self.dlg.esquemasPostgis.clear()
                esquemas_opcao = []
                
                # Adiciona esquemas na lista Python para posterior adição à comboBox
                while consulta.next():
                    record = consulta.record()
                    esquemas_opcao.append(record.field('table_schema').value())
                    #print record.field('f_table_schema').value()
                
                # Adiciona esquemas na comboBox
                self.dlg.esquemasPostgis.addItems(esquemas_opcao)

            else:
                QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Conexao com o banco nao estabelecida. Salve usuario e senha por favor.')
                return
                
            # Limpa linha onde vai ficar armazenado o caminho do Shapefile
            self.dlg.linhaShape.clear()

            # Limpa linha onde vai ficar armazenado o caminho da Saida
            self.dlg.linhaGeopackage.clear()
            
            # show the dialog
            self.dlg.show()
            # Run the dialog event loop
            result = self.dlg.exec_()
            
            """ Executa tarefas caso o OK seja pressionado """
            if result:
                # Pega opção de exportação do usuário: tabelas ou esquemas
                indiceCamada = self.dlg.visaoOuTabela.currentIndex()
                opcao_tab_visao = tabelas_visoes_opcao[indiceCamada]
                # print opcao_tab_visao 
                
                
                # Pega esquema selecionado pelo usuário
                indiceEsquema = self.dlg.esquemasPostgis.currentIndex()
                opcao_esquema = esquemas_opcao[indiceEsquema]
                # print opcao_esquema
                
                # Pega shapefile escolhido pelo usuário
                shapeRecorte = self.dlg.linhaShape.text()
                if shapeRecorte == '':
                    #print "Oi pessoal"
                    pass
                else:
                    #print shapeRecorte
                    pass
                
                # Pega shapefile escolhido pelo usuário
                nomeGeopackage = self.dlg.linhaGeopackage.text()
                if nomeGeopackage == '':
                    #print "Oi pessoal"
                    pass
                else:
                    #print nomeGeopackage
                    pass

                
                # Se a opção for por exportar as tabelas
                if opcao_tab_visao =='Tabelas':
                    # Imprime mensagem "Eu escolhi Tabelas" só para identificar se o fluxo do programa está funcionando
                    print 'Eu escolhi Tabelas'
                    
                    # Agora faz consulta ao banco para listar todas as tabelas do esquema escolhido
                    consulta_tab_vis = db.exec_("select table_name FROM information_schema.tables WHERE table_type = '%s' AND table_schema = '%s' ORDER BY table_name" % ('BASE TABLE', opcao_esquema))
                    tabelas = []
                    while consulta_tab_vis.next():
                        record = consulta_tab_vis.record()
                        tabelas.append(record.field('table_name').value())
                        # print record.field('table_name').value()
                        
                    # print tabelas
                    '''"-clipsrc", shapeRecorte,'''
                    # print ' '.join(tabelas)
                    # print "ogr2ogr", "-f", "GPKG", "-overwrite", nomeGeopackage, "PG:\"host=" + uri.host() + " dbname=" + \
                    #                 uri.database() + " schemas=" + opcao_esquema + " port=" + uri.port() + " user=" + uri.username() + " password=" + uri.password() + "\"", ' '.join(tabelas)
                    
                    
                    # Roda linha de comando ogr2ogr para conversão de formato
                    
                    # Exibe mensagem de espera no canto da tela para usuário 
                    self.iface.mainWindow().statusBar().showMessage("Espere um pouco...")
                    
                    # Caso shapefile de recorte seja válido, recortamos a base pelo shape
                    if QgsVectorLayer(shapeRecorte, 'testando', 'ogr').isValid():
                        erro_sim_nao = subprocess.call(["ogr2ogr", "-f", "GPKG", "-overwrite", "-clipsrc", shapeRecorte, nomeGeopackage, "PG:host=" + uri.host() + " dbname=" + \
                                     uri.database() + " schemas=" + opcao_esquema + " port=" + uri.port() + " user=" + uri.username() + " password=" + uri.password()] + tabelas, shell=True) # não pode ser assim: ..., ' '.join(tabelas) ], shell=True). Temos que concatenar listas
                    
                    # Caso seja inválido, tomamos a base inteira
                    else:
                        erro_sim_nao = subprocess.call(["ogr2ogr", "-f", "GPKG", "-overwrite", nomeGeopackage, "PG:host=" + uri.host() + " dbname=" + \
                                    uri.database() + " schemas=" + opcao_esquema + " port=" + uri.port() + " user=" + uri.username() + " password=" + uri.password()] + tabelas, shell=True)
                                    
                    # Limpa mensagem de espera
                    self.iface.mainWindow().statusBar().clearMessage()
                                        
                    # Se houver algum erro na linha de comando, mostra mensagem
                    if erro_sim_nao != 0:
                        QMessageBox.information(self.iface.mainWindow(), 'Erro', 'A operacao retornou um erro')
                        return
                    
                    
                    
                # Caso contrário, se for para exportar as visões
                else:
                    # Imprime mensagem "Eu escolhi Visões" só para identificar se o fluxo do programa está funcionando
                    print 'Eu escolhi Visoes'
                    
                    # Agora faz consulta ao banco para listar todas as visões do esquema escolhido
                    consulta_tab_vis = db.exec_("select table_name FROM information_schema.views WHERE table_schema = '%s' ORDER BY table_name" % (opcao_esquema))
                    visoes = []
                    while consulta_tab_vis.next():
                        record = consulta_tab_vis.record()
                        visoes.append(record.field('table_name').value())
                        # print record.field('table_name').value()
                        # print visoes
                    
                    # Roda linha de comando ogr2ogr para conversão de formato
                    
                    # Exibe mensagem de espera no canto da tela para usuário 
                    self.iface.mainWindow().statusBar().showMessage("Espere um pouco...")
                    
                    # Caso shapefile de recorte seja válido, recortamos a base pelo shape
                    if QgsVectorLayer(shapeRecorte, 'testando', 'ogr').isValid():
                        erro_sim_nao = subprocess.call(["ogr2ogr", "-f", "GPKG", "-overwrite", "-clipsrc", shapeRecorte, nomeGeopackage, "PG:host=" + uri.host() + " dbname=" + \
                                                    uri.database() + " schemas=" + opcao_esquema + " port=" + uri.port() + " user=" + uri.username() + " password=" + uri.password()] + visoes, shell=True)
                                                    
                    # Caso seja inválido, tomamos a base inteira
                    else:
                        erro_sim_nao = subprocess.call(["ogr2ogr", "-f", "GPKG", "-overwrite", nomeGeopackage, "PG:host=" + uri.host() + " dbname=" + \
                                                    uri.database() + " schemas=" + opcao_esquema + " port=" + uri.port() + " user=" + uri.username() + " password=" + uri.password()] + visoes, shell=True)
                                                    
                    # Limpa mensagem de espera                                
                    self.iface.mainWindow().statusBar().clearMessage()
                    
                    # Se houver algum erro na linha de comando, mostra mensagem
                    if erro_sim_nao != 0:
                        QMessageBox.information(self.iface.mainWindow(), 'Erro', 'A operacao retornou um erro')
                        return