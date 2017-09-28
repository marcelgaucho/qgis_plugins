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
from ui_settingsdialog import Ui_SettingsDialog

from ui_settingsdialog1 import Ui_Dialog

class SettingsDialog( QDialog, Ui_Dialog ):
    changed = pyqtSignal(name = 'changed')

    def __init__( self, parent = None ):
        super( SettingsDialog, self).__init__(parent )
        self.setupUi( self )
        self.setAttribute( Qt.WA_DeleteOnClose )

        # Aqui está retornando o valor padrão de DISTMIN (DEFAULT_DISTMIN) porque "SETTINGS_NAME + "/distmin"" não existe
        self.distmin = float( QSettings().value(SETTINGS_NAME + "/distmin", DEFAULT_DISTMIN ))
        self.distSpinBox.setValue( self.distmin )
        
        self.espacamento = float( QSettings().value(SETTINGS_NAME + "/espacamento", DEFAULT_ESPACAMENTO ))
        self.espSpinBox.setValue( self.espacamento )  
        
        self.qpontos = int( QSettings().value(SETTINGS_NAME + "/qpontos", DEFAULT_QPONTOS ))
        self.qpontosBox.setValue( self.qpontos )        
        
        self.maxseg = int( QSettings().value(SETTINGS_NAME + "/maxseg", DEFAULT_MAXSEG ))
        self.maxsegBox.setValue( self.maxseg )        
        
        self.simpl = float( QSettings().value(SETTINGS_NAME + "/simpl", DEFAULT_SIMPL ))
        self.simplBox.setValue( self.simpl )
        
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
        QSettings().setValue(SETTINGS_NAME+"/distmin", self.distSpinBox.value())
        QSettings().setValue(SETTINGS_NAME+"/espacamento", self.espSpinBox.value() )
        QSettings().setValue(SETTINGS_NAME+"/qpontos", self.qpontosBox.value() )
        QSettings().setValue(SETTINGS_NAME+"/maxseg", self.maxsegBox.value() )
        QSettings().setValue(SETTINGS_NAME+"/simpl", self.simplBox.value() )
                
        self.changed.emit()

    def cancel(self):
        self.close()

    def defaults(self):
        self.distSpinBox.setValue( DEFAULT_DISTMIN )
        self.espSpinBox.setValue( DEFAULT_ESPACAMENTO )
        self.qpontosBox.setValue( DEFAULT_QPONTOS )
        self.maxsegBox.setValue( DEFAULT_MAXSEG )
        self.simplBox.setValue( DEFAULT_SIMPL )
