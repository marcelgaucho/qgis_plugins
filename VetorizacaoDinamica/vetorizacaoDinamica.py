# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VetorizacaoDinamica
                                 A QGIS plugin
 Vai vetorizar achando uma estrada, interpolando os pontos inicial e final
                              -------------------
        begin                : 2016-09-01
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
# Importa bibliotecas PyQt e do QGIS
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from vetorizacaoDinamica_dialog import VetorizacaoDinamicaDialog
import os.path

# Pra tentar copiar do traceDigitize
from spline_tool import Spline

from settingsdialog import SettingsDialog

class VetorizacaoDinamica:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        # Salva referência para a interface do QGIS e para a tela
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', 'VetorizacaoDinamica_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Até aqui está igual ao do plugin Spline
                
        # Cria caixa de diálogo e mantém referência a ela
        self.dlg = VetorizacaoDinamicaDialog()

   
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Pega tela do QGIS e camada atual
        mc = self.canvas
        layer = mc.currentLayer()

        # Cria uma barra de ícones (toolbar) separado para o nosso Complemento
        self.toolbar = self.iface.addToolBar(u'VetorizacaoDinamica')
        self.toolbar.setObjectName(u'VetorizacaoDinamica')  

        
        # Cria a ação que dará origem ao botão e ao submenu do plugin que será colocado dentro de algum menu: Complementos, Vetor, Raster, etc
        self.action = QAction( QIcon(":/plugins/VetorizacaoDinamica/icon.png"), "Vetoriza Estrada", self.iface.mainWindow() )
        # self.action.setObjectName(u'VetDin')
        self.action.triggered.connect(self.run)
        
        # Estabelece que botão começa desabilitado, que é possível apertar o botão mas que ele começa despressionado        
        self.action.setEnabled(False) # botão começa desabilitado
        self.action.setCheckable(True) # botão é "pressionável"
        self.action.setChecked(False) # botão começa "despressionado"      

        # Cria ação para menu de ajustes  
        self.settingsAction = QAction( "Setagem", self.iface.mainWindow() )
        self.settingsAction.setObjectName("splineAction")
        self.settingsAction.triggered.connect(self.openSettings) 

        # Adiciona menu de ajustes na barra Vetor
        self.iface.addPluginToVectorMenu("&Ajustes prog din", self.settingsAction)
 
        # Adiciona complemento para o Menu e cria ícone na Barra de Ícones do Complemento
        self.iface.addPluginToMenu("&Prog Din", self.action)
        self.toolbar.addAction(self.action)

      
        # Conecta ferramentas caso escolhamos outra camada
        # cada vez que mudamos a camada selecionada no QGIS a função conectada é rodada
        self.iface.currentLayerChanged.connect(self.toggle)

        # Conecta sinal de desativação da ferramenta (usado quando desativamos a ferramenta que estamos executando)
        QObject.connect(mc, SIGNAL("mapToolSet(QgsMapTool*)"), self.deactivate)


    # Esta função habilita ou desabilita o botão do ícone 
    def toggle(self):
        # Pega a tela e a camada corrente
        mc = self.canvas
        layer = mc.currentLayer()
    
        # Decide quando o botão do plugin está habilitado e quando está desabilitado
        # Se a camada não for NULA, ou seja, houver alguma camada selecionada
        if layer <> None:
            # Se a camada estiver em edição (edição ativa) e for linha ou polígono então habilitaremos nosso botão
            if layer.isEditable() and (layer.geometryType() == 1 or layer.geometryType() == 2):
                self.action.setEnabled(True)
                QObject.connect(layer, SIGNAL("editingStopped()"), self.toggle) # Vamos conectar este sinal que vai parar a edição quando trocarmos de camada
                QObject.disconnect(layer, SIGNAL("editingStarted()"), self.toggle) # Vamos desconectar este sinal que vai, a princípio, começar a edição quando trocarmos de camada
            # Senão vamos desabilitar o botão 
            else:
                self.action.setEnabled(False)
                QObject.connect(layer, SIGNAL("editingStarted()"), self.toggle) # caso mudemos de camada, vamos começar a edição a princípio
                QObject.disconnect(layer, SIGNAL("editingStopped()"), self.toggle)   


        
    def deactivate(self):
        self.action.setChecked(False)
        # QObject.disconnect(self.spline, SIGNAL("traceFound(PyQt_PyObject)"), None)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Remove Complemento do Menu e remove também o ícone
        self.iface.removePluginMenu("&Prog Din", self.action)
        self.iface.removeToolBarIcon(self.action)
        
        # remove a barra de ícones
        # del self.toolbar
        
        # Remove Menu de Ajustes e remove ferramenta
        self.iface.removePluginVectorMenu("&Ajustes prog din", self.settingsAction )
        # del self.spline


    def run(self):
        """Run method that performs all the real work"""
        # Sistema de coordenadas atual (on-the-fly) precisa ser projetado     
        mapCanvasSrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
        if mapCanvasSrs.geographicFlag():
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Escolha um Sistema de Coordenadas de Referencia Projetado')
            return
        
        # Limpa caixas de seleção do raster e da banda
        self.dlg.comboBox.clear()
        self.dlg.comboBox_2.clear()        
        
        # Lista rasters que estão na legenda
        camadas_raster = []
        camadas = self.iface.legendInterface().layers()
        
        for camada in camadas:
            if camada.type() == QgsMapLayer.RasterLayer:
                camadas_raster.append(camada)
                self.dlg.comboBox.addItem(camada.name())
                
        # Se não houver camadas raster na legenda
        if not camadas_raster:
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Nao ha camadas raster na legenda')
            return
            
        
        
        
        # Pega número de bandas do raster
        #numBandas = camadaSelecionada.bandCount()
        
        # Lista que armazena as bandas existentes na imagem
        lista_bandas = [str(i) for i in range(1, 11)]
        print lista_bandas
        
        # Adiciona lista de bandas para a camada
        self.dlg.comboBox_2.addItems(lista_bandas)
        
        
        
        # Mostra a caixa de diálogo
        self.dlg.show()
        # Roda o laço da caixa de diálogo esperando por apertar "Ok" ou "Cancelar" (Run the dialog event loop)
        result = self.dlg.exec_()
        
        
        
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #Here we go...
            indiceCamada = self.dlg.comboBox.currentIndex()
            print indiceCamada
            camadaSelecionada = camadas_raster[indiceCamada]
            print camadaSelecionada.name()
            
            
            # Conectamos a nossa ferramenta no botão
            self.spline = Spline(self.iface, camadaSelecionada)

            mc = self.canvas
            layer = mc.currentLayer()
      
            # Acionamos nossa ferramenta
            mc.setMapTool(self.spline)
            self.action.setChecked(True)
        
        else:
            self.action.setChecked(False)
     
    def openSettings(self):
        # button signals in SettingsDialog were not working on Win7/64
        # if SettingsDialog was created with iface.mainWindow() as parent
        #self.settingsDialog = SettingsDialog(self.iface.mainWindow())
        self.settingsDialog = SettingsDialog()
        self.settingsDialog.show()

       
