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

class SettingsDialog( QDialog, Ui_SettingsDialog ):
    changed = pyqtSignal(name = 'changed')

    def __init__( self, parent = None ):
        super( SettingsDialog, self).__init__(parent )
        self.setupUi( self )
        self.setAttribute( Qt.WA_DeleteOnClose )

        self.tolerance = float( QSettings().value(SETTINGS_NAME + "/tolerance", DEFAULT_TOLERANCE ))
        self.splineToleranceSpinBox.setValue( self.tolerance )

        self.tightness = float( QSettings().value(SETTINGS_NAME + "/tightness", DEFAULT_TIGHTNESS ) )
        self.splineTightnessSpinBox.setValue(  self.tightness )
        
        self.espacamento = float( QSettings().value(SETTINGS_NAME + "/espacamento", DEFAULT_ESPACAMENTO ))
        self.splineEspacamentoSpinBox.setValue(  self.espacamento )
        
        self.qpontos = float( QSettings().value(SETTINGS_NAME + "/qpontos", DEFAULT_QPONTOS ))
        self.splineQpontosSpinBox.setValue(  self.qpontos )

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.ok)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        #self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.reset)
        self.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.defaults)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)

    def ok(self):
        self.apply()
        self.close()

    def apply(self):
        QSettings().setValue(SETTINGS_NAME+"/tolerance", self.splineToleranceSpinBox.value())
        QSettings().setValue(SETTINGS_NAME+"/tightness", self.splineTightnessSpinBox.value() )
        QSettings().setValue(SETTINGS_NAME+"/espacamento", self.splineEspacamentoSpinBox.value() )
        QSettings().setValue(SETTINGS_NAME+"/qpontos", self.splineQpontosSpinBox.value() )
        self.changed.emit()

    def cancel(self):
        self.close()

    # Disabled because there were too many buttons
    #def reset(self):
        ## reset to orig values (when dialog was opened)
        #self.splineToleranceSpinBox.setValue( self.tolerance )
        #self.splineTightnessSpinBox.setValue(  self.tightness )

    def defaults(self):
        self.splineToleranceSpinBox.setValue( DEFAULT_TOLERANCE )
        self.splineTightnessSpinBox.setValue( DEFAULT_TIGHTNESS )
        self.splineEspacamentoSpinBox.setValue( DEFAULT_ESPACAMENTO )
        self.splineQpontosSpinBox.setValue( DEFAULT_QPONTOS)
