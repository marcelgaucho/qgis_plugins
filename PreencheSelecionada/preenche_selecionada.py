# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PreencheSelecionada
                                 A QGIS plugin
 O plugin irá preencher a tabela t_interface com a tupla selecionada
                              -------------------
        begin                : 2017-03-28
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Marcel Rotunno
        email                : marcel.rotunno@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QPyNullVariant
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from preenche_selecionada_dialog import PreencheSelecionadaDialog
import os.path
from settingsdialog import SettingsDialog

# Importa classes dos módulos para lidar com SQL, do Qt, e do núcleo do QGIS
from PyQt4.QtSql import *
from qgis.core import *

# Importa valores padrão das configurações do plugin
from utils import *

class PreencheSelecionada:
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
            'PreencheSelecionada_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Preenche feicoes selecionadas')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PreencheSelecionada')
        self.toolbar.setObjectName(u'PreencheSelecionada')

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
        return QCoreApplication.translate('PreencheSelecionada', message)


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

        # Create the dialog (after translation) and keep reference
        self.dlg = PreencheSelecionadaDialog()

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

        icon_path = ':/plugins/PreencheSelecionada/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Preenche feicoes selecionadas na t_interface'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Cria ação para menu de ajustes  
        self.settingsAction = QAction( "Configura", self.iface.mainWindow() )
        self.settingsAction.setObjectName("preencheSelecionadaAction")
        self.settingsAction.triggered.connect(self.openSettings) 

        # Adiciona menu de ajustes na barra Vetor
        self.iface.addPluginToMenu("&PreencheSelecionada: Usuario e Senha", self.settingsAction)

        
    def openSettings(self):
        # button signals in SettingsDialog were not working on Win7/64
        # if SettingsDialog was created with iface.mainWindow() as parent
        #self.settingsDialog = SettingsDialog(self.iface.mainWindow())
        self.settingsDialog = SettingsDialog()
        self.settingsDialog.show()        
        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Preenche feicoes selecionadas'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Roda método que faz todo o trabalho real"""
        
        """Executa tarefas antes de apertar o OK da janela do Complemento"""

        
        
        # Pega camada ativa na legenda
        camadaAtiva = self.iface.activeLayer()
        
        # Se não tiver nenhuma camada ativa selecionada (se não tiver nenhum dataProvider) acusa erro
        try:
            provedor = camadaAtiva.dataProvider()
        except:
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Selecione alguma camada')
            return
        
        # Se o dataProvider da camada não for Postgres também acusa erro
        if provedor.name() != 'postgres':
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Selecione uma camada com conexao PostGIS')
            return
            
        # Cria mesma URI da camada ativa
        uri_camadaAtiva = QgsDataSourceURI(camadaAtiva.dataProvider().dataSourceUri())
        # print uri_camadaAtiva
        
        
        # Pega tabela selecionada para ser usada como dado da consulta 
        tabela = uri_camadaAtiva.table()
        esquema = uri_camadaAtiva.schema()
        #print 'Tabela = ', uri.table()
        #print 'Esquema = ', uri.schema()
            
            
        # Estabelece nomes a serem usados na cláusula WHERE da consulta
        ultima_letra_geom = tabela[-1]
        dic_geom = {'a': 'poligono', 'p': 'ponto', 'l':'linha'}
        sigla_classe = tabela[0:-2]
        #print 'sigla_classe = ', sigla_classe
        #print ultima_letra_geom, 'vamos ver: ', dic_geom[ultima_letra_geom]  

        # Lista de camadas presente na legenda
        camadasAbertas = self.iface.legendInterface().layers()
        #for camada in camadasAbertas:
        #    print camada.name()
        
        # Percorre camadas na legenda para determinar se existe a mesma classe da camada selecionada em outra escala. Caso ela exista a URI dela será adicionada 
        # para InfoUriCamadasOutraEscala e o objeto da camada será adicionado para CamadasOutraEscala
        InfoUriCamadasOutraEscala = []
        CamadasOutraEscala = []
        
        for camadaLegenda in camadasAbertas:
            try:
                uri_camadaLegenda = QgsDataSourceURI(camadaLegenda.dataProvider().dataSourceUri())
                                
                # Testa para ver se é mesma camada só que em outra escala - Não está funcionando ainda
                if uri_camadaAtiva.table() == uri_camadaLegenda.table() and uri_camadaAtiva.schema() != uri_camadaLegenda.schema():
                    # print 'Tabela_selecao: ', uri.table(), ' Esquema_selecao: ', uri.schema(), ' diferente de Tabela_legenda: ', uri_camadaLegenda.table(), ' Esquema_legenda: ', uri_camadaLegenda.schema()
                    #QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Tem mesma(s) camada(s) em escala diferente')
                    if uri_camadaLegenda.uri() not in InfoUriCamadasOutraEscala:
                        # print 'Vou adicionar camada'
                        InfoUriCamadasOutraEscala.append(uri_camadaLegenda)
                        CamadasOutraEscala.append(camadaLegenda)
                    else:
                        # print 'Não vou adicionar camada'
                        pass
            except:
                pass

        
        #print InfoUriCamadasOutraEscala 
        #print CamadasOutraEscala
        
        mensagem_uri = ''
        for uri in InfoUriCamadasOutraEscala:
            #print uri
            mensagem_uri = mensagem_uri + 'tabela: ' + uri.table() + '; esquema: ' + uri.schema() + '\n'
        
        #print 'Camadas iguais em escalas diferentes: ' + mensagem_uri
        QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Tem mesma(s) camada(s) em escala diferente: \n' + mensagem_uri)
        
        # Cria uma conexão ao Postgres através de QSqlDatabase - QPSQL se refere ao Postgres
        db = QSqlDatabase.addDatabase("QPSQL");
        
        
        # Dados da conexão são os mesmos da camada ativa (mesmo servidor, mesmo banco e mesma porta)
        db.setHostName(uri_camadaAtiva.host())
        db.setDatabaseName(uri_camadaAtiva.database())
        db.setPort(int(uri_camadaAtiva.port()))

        
        # Pega nome e senha de usuários nas configurações do plugin        
        usuario = QSettings().value(SETTINGS_NAME + "/usuario", DEFAULT_USUARIO )
        senha = QSettings().value(SETTINGS_NAME + "/senha", DEFAULT_SENHA )
        #print usuario, senha
        
        # Estabelece usuário e senha para conexão com o banco        
        db.setUserName(usuario)
        db.setPassword(senha)  
        
        # Feições selecionadas
        selecao = camadaAtiva.selectedFeatures()
        #print selecao
        selecao_outras_camadas = [camada.selectedFeatures() for camada in CamadasOutraEscala]
        #print "Selecao outras camadas = ", selecao_outras_camadas
        
        # cria lista do id_objeto das feições selecionadas de todas as classes iguais de escalas diferentes presentes na legenda
        lista_id_objeto = [feicao['id_objeto'] for feicao in selecao]
        lista_id_objeto_outras_camadas = [[feicao['id_objeto'] for feicao in camada] for camada in selecao_outras_camadas]
        #print 'lista_id_objeto_outras_camadas = ', lista_id_objeto_outras_camadas
        #lista_unica_id_objeto_outras_camadas = [id_objeto for elemento in lista_id_objeto_outras_camadas for id_objeto in elemento]
        #lista_unica_id_objeto = lista_id_objeto + lista_unica_id_objeto_outras_camadas

        
        #print lista_id_objeto, type(lista_id_objeto[0])  
        
        # converte elementos da lista de id_objeto em string para usá-los na consulta
        lista_id_objeto = [str(el) for el in lista_id_objeto]
        lista_id_objeto_string = ','.join(lista_id_objeto)
        
        lista_id_objeto_outras_camadas = [[str(subel) for subel in el] for el in lista_id_objeto_outras_camadas]
        #print 'Lista de objetos de outras camadas =', lista_id_objeto_outras_camadas
        
        #lista_unica_id_objeto = [str(el) for el in lista_unica_id_objeto]
        #lista_unica_id_objeto_string = ','.join(lista_unica_id_objeto)

        
        

        #print 'vou conectar no banco'
        
        # Abre conexão ao banco de dados para adicionar os esquemas que têm tabelas espaciais contidos lá
        if db.open():        
            # Tenho que rever essa consulta
            string_consulta = "SELECT id_objeto_producao, id_nomebngb, nm_geografico_producao, cd_validacao_operador, tx_apontamento_crng FROM bngb_interface.t_interface WHERE id_objeto_producao IN (" + lista_id_objeto_string + ") " + \
            "AND nm_esquema_base = '" + esquema + "' AND concat_ws('_', nm_sigla_categoria, nm_classe) ILIKE '" + sigla_classe + "' AND tp_geom ILIKE '" + dic_geom[ultima_letra_geom] +"' "
            #print "string consulta exibir comboBox = ", string_consulta
            msg_add = ""
            for indice, uri in enumerate(InfoUriCamadasOutraEscala):
                # Verifica se a lista de id_objeto contém algum valor (alguma seleção)
                if lista_id_objeto_outras_camadas[indice]:
                    msg_add = msg_add + "UNION SELECT id_objeto_producao, id_nomebngb, nm_geografico_producao, cd_validacao_operador, tx_apontamento_crng FROM bngb_interface.t_interface WHERE id_objeto_producao IN (" + ','.join(lista_id_objeto_outras_camadas[indice]) + ") " + \
                    "AND nm_esquema_base = '" + uri.schema() + "' AND concat_ws('_', nm_sigla_categoria, nm_classe) ILIKE '" + sigla_classe + "' AND tp_geom ILIKE '" + dic_geom[ultima_letra_geom] +"' "
            
            string_consulta = string_consulta + msg_add
            #print string_consulta
            
            #print string_consulta
            consulta = db.exec_(string_consulta) #IN (" + lista_id_objeto_string + ")")        
        
            resultado_consulta = []
            
            # Adiciona resultados da consulta (id_objeto_producao, id_nomebngb, nm_geografico_producao)
            # na lista Python para posterior adição à comboBox
            while consulta.next():
                record = consulta.record()
                
                #print 'Comecando'
                # Pega o id_objeto_producao (na tabela t_interface) correspondente ao id_objeto das feições selecionadas
                id_objeto_producao = str(record.field('id_objeto_producao').value()).decode("utf-8")
                #print id_objeto_producao, ' - tipo ', type(id_objeto_producao)
                
                # Pega id_nomebngb 
                id_nomebngb = str(record.field('id_nomebngb').value()).decode("utf-8")
                #print id_nomebngb, ' - tipo ', type(id_nomebngb)
                
                # Pega nm_geografico_producao
                if isinstance(record.field('nm_geografico_producao').value(), QPyNullVariant):
                    nome_bngb = str(record.field('nm_geografico_producao').value()).decode("utf-8")
                    #print nome_bngb, ' - tipo1 ', type(nome_bngb)
                    
                else:
                    nome_bngb = record.field('nm_geografico_producao').value()
                    #print nome_bngb, ' - tipo1 ', type(nome_bngb)
                    
                cd_validacao_operador = str(record.field('cd_validacao_operador').value()).decode("utf-8");
                
                if isinstance(record.field('tx_apontamento_crng').value(), QPyNullVariant):
                    tx_apontamento_crng = str(record.field('tx_apontamento_crng').value()).decode("utf-8")
                    #print nome_bngb, ' - tipo1 ', type(nome_bngb)
                    
                else:
                    tx_apontamento_crng = record.field('tx_apontamento_crng').value()
                    #print nome_bngb, ' - tipo1 ', type(nome_bngb)
                
                
                # Tupla a ser adicionada para a lista que será posteriormente adicionada à ComboBox
                tupla_add = (id_objeto_producao, id_nomebngb, nome_bngb, cd_validacao_operador, tx_apontamento_crng)
                resultado_consulta.append(tupla_add)

                
                
            #print 'Resultado da consulta = ', resultado_consulta
            
            # Parei aqui. Até aqui tudo bem, resultado_consulta guarda a tupla (id_objeto_producao, id_nomebngb, nome_bngb) da t_interface referente a todos os registros selecionados nas diversas camadas da legenda que se referem a uma classe em escalas distintas
            # Cria lista de strings a partir de resultado_consulta para adição à ComboBox
            resultado_consulta_string = []
            for el in resultado_consulta:
                item_comboBox = el[0] + '\ ' + el[1] + '\ ' + el[2] + '\ ' + el[3] + '\ ' + el[4]
                resultado_consulta_string.append(item_comboBox)
        
            #print resultado_consulta_string
        
            # Limpa e adiciona elementos na Combo Box (caixa de opção)
            self.dlg.comboBox.clear()
            self.dlg.comboBox.addItems(resultado_consulta_string)

            # Indica na caixa de diálogo uma linha para mostrar a camada que está sendo editada na t_interface
            self.dlg.lineEdit.clear()
            self.dlg.lineEdit.setText(uri_camadaAtiva.schema() + '.' + uri_camadaAtiva.table())
        else:
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Conexao rejeitada')
            return


        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        
        """ Executa tarefas caso o OK seja pressionado """
        if result:

            # Pega índice e tupla (id_objeto_producao, id_nomebngb, nm_geografico_producao) escolhidos no ComboBox 
            indice = self.dlg.comboBox.currentIndex() 
            stringSelecionada = resultado_consulta_string[indice] 
            
            #print 'String Selecionada = ', stringSelecionada
            
            # Transforma opção selecionada na ComboBox em lista
            listastringSelecionada = stringSelecionada.split("\ ")
            #print 'Lista selecionada =', listastringSelecionada
            #print 'Lista selecionada[2] =', listastringSelecionada[2], 'tipo = ', type(listastringSelecionada[2])
            listastringSelecionada[2] = listastringSelecionada[2].replace("'", "''")
            listastringSelecionada[4] = listastringSelecionada[4].replace("'", "''")
            print listastringSelecionada[4]
            
            #print 'Lista selecionada[2] depois =', listastringSelecionada[2], 'tipo = ', type(listastringSelecionada[2])
            print
            print
            print
            
            
            # Estabelece string para consulta na Camada Ativa (nm_geografico_producao e tx_apontamento_crng podem ser nulos)
            if listastringSelecionada[2] == 'NULL':            
                string_consulta = "UPDATE bngb_interface.t_interface SET cd_validacao_operador = '" + listastringSelecionada[3] + "', id_nomebngb = " + listastringSelecionada[1] + ", nm_geografico_producao = " + listastringSelecionada[2]  
                #print "UPDATE referente à camada ativa =", string_consulta
            else:
                string_consulta = "UPDATE bngb_interface.t_interface SET cd_validacao_operador = '" + listastringSelecionada[3] + "', id_nomebngb = " + listastringSelecionada[1] + ", nm_geografico_producao = '" + listastringSelecionada[2] + "'" 
                #print "UPDATE referente à camada ativa =", string_consulta

            if listastringSelecionada[4] == 'NULL':            
                string_consulta = string_consulta + ", tx_apontamento_crng = " + listastringSelecionada[4] + \
                " WHERE id_objeto_producao IN (" + lista_id_objeto_string + ") " + \
                "AND nm_esquema_base = '" + esquema  + "' AND concat_ws('_', nm_sigla_categoria, nm_classe) ILIKE '" + sigla_classe + "' AND tp_geom ILIKE '" + dic_geom[ultima_letra_geom] +"'"
                print u"UPDATE referente à camada ativa =", string_consulta
            else:
                string_consulta = string_consulta + ", tx_apontamento_crng = '" + listastringSelecionada[4] + \
                "' WHERE id_objeto_producao IN (" + lista_id_objeto_string + ") " + \
                "AND nm_esquema_base = '" + esquema  + "' AND concat_ws('_', nm_sigla_categoria, nm_classe) ILIKE '" + sigla_classe + "' AND tp_geom ILIKE '" + dic_geom[ultima_letra_geom] +"'"
                print u"UPDATE referente à camada ativa =", string_consulta

                
            # Executa atualização (update)
            db.exec_(string_consulta)
            
            # Percorre a mesma classe nas outras escalas 
            for indice, uri in enumerate(InfoUriCamadasOutraEscala):
                # Verifica se a lista de id_objeto contém algum valor (alguma seleção)
                if lista_id_objeto_outras_camadas[indice]:
                    if listastringSelecionada[2] == 'NULL':            
                        string_consulta = "UPDATE bngb_interface.t_interface SET cd_validacao_operador = '" + listastringSelecionada[3] + "', id_nomebngb = " + listastringSelecionada[1] + ", nm_geografico_producao = " + listastringSelecionada[2] 
                        #print "UPDATE referente à camada auxiliar = ", string_consulta
                    else:
                        string_consulta = "UPDATE bngb_interface.t_interface SET cd_validacao_operador = '" + listastringSelecionada[3] + "', id_nomebngb = " + listastringSelecionada[1] + ", nm_geografico_producao = '" + listastringSelecionada[2] + "'"
                        #print "UPDATE referente à camada auxiliar = ", string_consulta
 
                    if listastringSelecionada[4] == 'NULL':            
                        string_consulta = string_consulta + ", tx_apontamento_crng = " + listastringSelecionada[4] + \
                        " WHERE id_objeto_producao IN (" + ','.join(lista_id_objeto_outras_camadas[indice]) + ") " + \
                        "AND nm_esquema_base = '" + uri.schema()  + "' AND concat_ws('_', nm_sigla_categoria, nm_classe) ILIKE '" + sigla_classe + "' AND tp_geom ILIKE '" + dic_geom[ultima_letra_geom] +"'"
                        print u"UPDATE referente à camada auxiliar =", string_consulta
                    else:
                        string_consulta = string_consulta + ", tx_apontamento_crng = '" + listastringSelecionada[4] + \
                        "' WHERE id_objeto_producao IN (" + ','.join(lista_id_objeto_outras_camadas[indice]) + ") " + \
                        "AND nm_esquema_base = '" + uri.schema()  + "' AND concat_ws('_', nm_sigla_categoria, nm_classe) ILIKE '" + sigla_classe + "' AND tp_geom ILIKE '" + dic_geom[ultima_letra_geom] +"'"
                        print u"UPDATE referente à camada auxiliar =", string_consulta
 
                    # Executa atualização (update)
                    db.exec_(string_consulta)
            
            
            
            
            
            
