# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_settingsdialog1.ui'
#
# Created: Mon Mar 27 17:44:39 2017
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(616, 458)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 20, 261, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(80, 60, 241, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.distSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.distSpinBox.setGeometry(QtCore.QRect(340, 20, 62, 22))
        self.distSpinBox.setSingleStep(0.1)
        self.distSpinBox.setProperty("value", 5.0)
        self.distSpinBox.setObjectName(_fromUtf8("distSpinBox"))
        self.espSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.espSpinBox.setGeometry(QtCore.QRect(340, 70, 62, 22))
        self.espSpinBox.setSingleStep(0.1)
        self.espSpinBox.setProperty("value", 5.0)
        self.espSpinBox.setObjectName(_fromUtf8("espSpinBox"))
        self.qpontosBox = QtGui.QSpinBox(Dialog)
        self.qpontosBox.setGeometry(QtCore.QRect(340, 120, 42, 22))
        self.qpontosBox.setProperty("value", 5)
        self.qpontosBox.setObjectName(_fromUtf8("qpontosBox"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(60, 110, 241, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(80, 170, 221, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.maxsegBox = QtGui.QSpinBox(Dialog)
        self.maxsegBox.setGeometry(QtCore.QRect(340, 170, 42, 22))
        self.maxsegBox.setProperty("value", 3)
        self.maxsegBox.setObjectName(_fromUtf8("maxsegBox"))
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(80, 230, 251, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(50, 380, 501, 23))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.RestoreDefaults)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.simplBox = QtGui.QDoubleSpinBox(Dialog)
        self.simplBox.setGeometry(QtCore.QRect(340, 240, 62, 22))
        self.simplBox.setProperty("value", 2.5)
        self.simplBox.setObjectName(_fromUtf8("simplBox"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Distância mínima entre os vértices (em m)", None))
        self.label_3.setText(_translate("Dialog", "Espaçamento entre os vértices na perpendicular ao segmento (em m)", None))
        self.label_4.setText(_translate("Dialog", "Quantidade de pontos acima e abaixo do segmento na perpendicular ao segmento", None))
        self.label_5.setText(_translate("Dialog", "Quantidade máxima de segmentos entre 2 pontos consecutivos marcados", None))
        self.label_6.setText(_translate("Dialog", "Parâmetro de simplificação Douglas-Peucker do trecho adicionado (em m)", None))

