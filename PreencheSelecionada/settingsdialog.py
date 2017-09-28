# -*- coding: utf-8 -*-
"""
/***************************************************************************
  Spline plugin SettingsDialog
                             -------------------
        begin                : 2014-02-05
        copyright            : (C) 2014 by Radim Blažek
        email                : radim.blazek@gmail.com
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from utils import *

# Pega valores digitados pelo usuário na opção de ajustes. Importa esses valores para deixar na configuração do plugin


from ui_settingsdialog1 import Ui_Dialog

class SettingsDialog( QDialog, Ui_Dialog ):
    changed = pyqtSignal(name = 'changed')

    def __init__( self, parent = None ):
        super( SettingsDialog, self).__init__(parent )
        self.setupUi( self )
        self.setAttribute( Qt.WA_DeleteOnClose )

        # Aqui está retornando o valor padrão de USUARIO (DEFAULT_USUARIO) porque SETTINGS_NAME + "/usuario" não existe
        self.usuario = QSettings().value(SETTINGS_NAME + "/usuario", DEFAULT_USUARIO )
        self.lineEdit.setText( self.usuario )
        
        self.senha = QSettings().value(SETTINGS_NAME + "/senha", DEFAULT_SENHA )
        self.lineEdit_2.setText( self.senha )  
        
        # Conecta funções
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.ok)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.defaults)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)

    def ok(self):
        self.apply()
        self.close()

    def apply(self):
        # Aplica valores escolhidos nas Spin Box
        QSettings().setValue(SETTINGS_NAME+"/usuario", self.lineEdit.text())
        QSettings().setValue(SETTINGS_NAME+"/senha", self.lineEdit_2.text() )
                
        self.changed.emit()

    def cancel(self):
        self.close()

    def defaults(self):
        self.lineEdit.setText( DEFAULT_USUARIO )
        self.lineEdit_2.setText( DEFAULT_SENHA )

