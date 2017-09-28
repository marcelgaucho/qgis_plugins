Rem Estabelece caminhos importantes do QGIS
SET ROOT=C:\Program Files\QGIS Essen
SET QGIS_APP = %ROOT%\apps\qgis

Rem Adiciona diretório de módulos Python
SET PYTHONPATH=%QGIS_APP%\python

Rem Estabelece diretório padrão das bibliotecas do Python
SET PYTHONHOME=%ROOT%\apps\Python27

Rem Estabelece diretórios executáveis do QGIS para buscar informações
SET PATH=%ROOT%\bin; %QGIS_APP%\bin;%PATH%





pyuic4 C:\Users\marcel.rotunno\.qgis2\python\plugins\PreencheSelecionada\ui_settingsdialog1.ui -o ui_settingsdialog1.py


PAUSE