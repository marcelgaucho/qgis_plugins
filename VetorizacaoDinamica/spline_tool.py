# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Digitize spline, based on CircularArcDigitizer (Stefan Ziegler)
    and Generalizer plugin (Piotr Pociask) which is based on GRASS v.generalize
                              -------------------
        begin                : February 2014
        copyright            : (C) 2014 by Radim Blazek
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
import numpy as np
from math import sqrt
import collections

from utils import *

class Spline(QgsMapTool):
    def __init__(self, iface, camada_raster):
        self.camada_raster = camada_raster
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        # Declara herança 
        # super(QgsMapTool, self).__init__(self.canvas)
        
        QgsMapTool.__init__(self, self.canvas)
        
        # Declara a linha que aparece enquanto restituimos
        self.rb = QgsRubberBand(self.canvas,  QGis.Polygon)
        
        # Ele está declarando a geometria como Polígono. Isto depois te dá a flexibilidade depois de ser Linha também (o polígono pode ser linha)
        self.type = QGis.Polygon # layer geometry type
        #self.type = QGis.Line
        
        # Estes são os pontos marcados pelo usuário
        self.points = [] 
        
        # Estes serão os pontos interpolados
        self.pontos_interpolados = []
        
        # Variável booleana que indica que a tecla Ctrl está pressionada
        self.mCtrl = False
        
        #self.cursor = QCursor(Qt.CrossCursor)
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                      "      c None",
                                      ".     c #FF0000",
                                    
                                    
                                      "+     c #FFFFFF",
                                      "                ",
                                      "       +.+      ",
                                      "      ++.++     ",
                                      "     +.....+    ",
                                      "    +.     .+   ",
                                      "   +.   .   .+  ",
                                      "  +.    .    .+ ",
                                      " ++.    .    .++",
                                      " ... ...+... ...",
                                      " ++.    .    .++",
                                      "  +.    .    .+ ",
                                      "   +.   .   .+  ",
                                      "   ++.     .+   ",
                                      "    ++.....+    ",
                                      "      ++.++     ",
                                      "       +.+      "]))
                                      
        
                                     

    # Método que decide as ações de fato a partir de um clique do mouse (event.button()) na tela
    def canvasPressEvent(self, event):
        # Posições x e y (em píxeis) das coordenadas no dispositivo (Tela do QGIS) 
        x = event.pos().x()
        y = event.pos().y()
        
        # Se tela for clicada com botão esquerdo do mouse
        if event.button() == Qt.LeftButton:
            # startingPoint é o ponto ainda em coordenadas do dispositivo 
            # (medida em píxeis na tela do QGIS dentro da tela do Computador)
            startingPoint = QPoint(x,y) 
            
            # objeto usado para atrair o ponto para alguma camada próxima 
            # conforme configurações de atração no QGIS
            snapper = QgsMapCanvasSnapper(self.canvas)
                        
            '''Atração para vértices. Pega configurações de ajustes do QGIS'''
            # Tenta atração para um vértice próximo na camada que está sendo editada (camada atual)  
            (retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)
                 
            # Se o ponto for atraído para algum vértice da camada atual, então o ponto será o mesmo desse vértice  
            if result <> []:
                point = QgsPoint( result[0].snappedVertex )
                            
            # Caso contrário, se não for atraído por nenhum vértice, ele vai tentar atração com as camadas de fundo 
            else:
                (retval,result) = snapper.snapToBackgroundLayers(startingPoint)
                # Caso consiga, atrai para vértice de camada de fundo
                if result <> []:
                    point = QgsPoint( result[0].snappedVertex )
                    
                # Por fim, se ele não for atraído por nenhum vértice, ficará sem atração
                else:
                    # Ponto será convertido para projeção do mapa (on-the-fly) 
                    point = self.canvas.getCoordinateTransform().toMapCoordinates( event.pos().x(), event.pos().y() )
                    
            
            # Adiciona ponto à lista de pontos marcados pelo usuário
            self.points.append(point)
            #print 'pontos = ', self.points
            
            # print 'tecla Ctrl ativada', self.mCtrl
            # Se a tecla Ctrl estiver apertada, vamos adicionar apenas o novo ponto para self.pontos_interpolados
            if self.mCtrl:
                self.pontos_interpolados.append(point)
                # print 'pontos marcados', self.points
                # print 'pontos interpolados', self.pontos_interpolados
                
            # Senão vamos adicionar os pontos interpolados para self.pontos_interpolados
            else:
                # Aqui vamos interpolar apenas o último segmento (penúltimo e último ponto)
                # E adicionar o resultado aos pontos interpolados (senão teríamos que interpolar a linha toda, o que demora bastante)
                pontos_recentes, grafo, retas_perpendiculares, result = self.interpolacao ( self.points[-2::] )
                # print "pontos recentes = ", pontos_recentes, " tipo pontos recentes = ", type(pontos_recentes), " tipo pontos interpolados = ", type(self.pontos_interpolados)
                simpl = float( QSettings().value(SETTINGS_NAME + "/simpl", DEFAULT_SIMPL )) # Parâmetro de simplificação do algoritmo Douglas-Peucker
                pontos_recentes = self.simplifyPoints(pontos_recentes, simpl) 
                self.pontos_interpolados = self.pontos_interpolados + pontos_recentes[1:] # pontos_recentes contém penúltimo ponto marcado, por isso adicionamos do segundo em diante (para não duplicar)
                # print 'pontos recentes:', pontos_recentes
                # print 'pontos marcados Ctrl desativado', self.points
                # print 'pontos interpolados Ctrl desativado', self.pontos_interpolados
                
                #Isto é para que a medida que vamos adicionando pontos a linha vá adquirindo a forma de uma Spline
                # self.setRubberBandPoints(self.pontos_interpolados )
            
            # print 'pontos interpolados = ', self.pontos_interpolados
            
        # Caso contrário, se o clique for dado pelo botão direito 
        else:
            #print 'botao direito apertado'
            # Cria a feição caso ela tenha 2 pontos ou mais
            if len( self.points ) >= 2:
                # refresh without last point
                #self.refresh()
                #self.pontos_interpolados = self.simplifyPoints(self.pontos_interpolados, 5)
                self.createFeature(self.pontos_interpolados) # self.createFeature(points)

            self.resetPoints()
            self.resetRubberBand()
            self.canvas.refresh() 
            
    # Estaf função esvazia as listas de pontos marcados e de pontos interpolados, habilitando o traçado de uma nova feição       
    def resetPoints(self):
        self.points = []
        self.pontos_interpolados = []
    
    # Create feature from digitized points, i.e. without the last moving point 
    # where right click happened. This the same way how core QGIS Add Feature works.
    def createFeature(self, pontos_interpolados):
        layer = self.canvas.currentLayer() 
        provider = layer.dataProvider()
        fields = layer.pendingFields()
        f = QgsFeature(fields)
            
        coords = []
        
        # coords, grafo, pontos_perpendiculares, result = self.interpolacao ( self.points )
        coords = pontos_interpolados
        
        # Transforma pontos da projecao on-the-fly para a projecao da camada se necessario
        if self.canvas.mapRenderer().hasCrsTransformEnabled() and layer.crs() != self.canvas.mapRenderer().destinationCrs():
            coords_tmp = coords[:]
            coords = []
            for point in coords_tmp:
                transformedPoint = self.canvas.mapRenderer().mapToLayerCoordinates( layer, point )
                coords.append(transformedPoint)
              
        ## Add geometry to feature.
        if self.isPolygon == True:
            g = QgsGeometry().fromPolygon([coords])
        else:
            g = QgsGeometry().fromPolyline(coords)
        f.setGeometry(g)
            
        ## Add attributefields to feature.
        for field in fields.toList():
            ix = fields.indexFromName(field.name())
            f[field.name()] = provider.defaultValue(ix)

        layer.beginEditCommand("Feature added")
        
        settings = QSettings()
        
        # Isto é para decidir se entrar ou não com valores na tabela de atributos 
        disable_attributes = settings.value( "/qgis/digitizing/disable_enter_attribute_values_dialog", False, type=bool)
        if disable_attributes:
            layer.addFeature(f)
            layer.endEditCommand()
        else:
            dlg = self.iface.getFeatureForm(layer, f)
            if QGis.QGIS_VERSION_INT >= 20400: 
                dlg.setIsAddDialog( True ) # new in 2.4, without calling that the dialog is disabled
            if dlg.exec_():
                if QGis.QGIS_VERSION_INT < 20400: 
                    layer.addFeature(f)
                layer.endEditCommand()
            else:
                layer.destroyEditCommand()
                # Esse método também não faz parte do "núcleo" da função
    
    # Método para desenhar no QGIS o traçado do vetor  
    def canvasMoveEvent(self,event):
        # Cor e Espessura da Linha que aparece enquanto restituímos (vetorizamos)
        color = QColor(255,0,0,100)
        self.rb.setColor(color)
        self.rb.setWidth(3)

        x = event.pos().x()
        y = event.pos().y()
        
        startingPoint = QPoint(x,y)
        snapper = QgsMapCanvasSnapper(self.canvas)
            
        # Tenta pegar um vértice da camada em edição (por atração).  
        # Se não conseguimos nós tentamos a atração para um vértice de uma camada de fundo.
        # Se ainda não conseguirmos atração, nós não fazemos atração a nenhum vértice.
        (retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)   
        if result <> []:
            point = QgsPoint( result[0].snappedVertex )
        else:
            (retval,result) = snapper.snapToBackgroundLayers(startingPoint)
            if result <> []:
                point = QgsPoint( result[0].snappedVertex )
            else:
                point = self.canvas.getCoordinateTransform().toMapCoordinates( event.pos().x(), event.pos().y() );
        
        # Declara cópias dos atuais pontos marcados pelo usuário e os interpolados    
        pontos_marcados = list( self.points )
        pontos_interpolados = list( self.pontos_interpolados)
        
        # Adiciona ponto para lista de pontos marcados
        pontos_marcados.append( point )
        
        
        # Se a tecla Ctrl estiver apertada, vamos adicionar apenas o novo ponto para pontos_interpolados
        if self.mCtrl:
            pontos_interpolados.append(point)
        # Senão vamos adicionar os pontos interpolados para pontos_interpolados
        else:
            # Interpola os 2 últimos pontos e adiciona o resultado aos pontos interpolados no momento
            pontos_recentes, grafo, pontos_perpendiculares, result = self.interpolacao ( pontos_marcados[-2::] )
            simpl = float( QSettings().value(SETTINGS_NAME + "/simpl", DEFAULT_SIMPL )) # Parâmetro de simplificação do algoritmo Douglas-Peucker
            pontos_recentes = self.simplifyPoints(pontos_recentes, simpl) 
            pontos_interpolados = pontos_interpolados + pontos_recentes[1:]
        
        
        self.setRubberBandPoints(pontos_interpolados )
        


    def refresh(self):
        # redraw, called when settings changed
        #if self.points:
        #    points, grafo, pontos_perpendiculares, result = self.interpolacao ( self.points )
        #    self.setRubberBandPoints(points )
        #self.setRubberBandPoints(self.pontos_interpolados ) # vou testar isto mais adiante
        pass
    
    # Esse método não tem função (somente é passado com pass) pois é diferente clicarmos com o botão esquerdo e o botão direito do mouse.
    # Se quiséssemos a mesma ação para ambos poderíamos utilizar esse método.
    def canvasReleaseEvent(self,event):  
        pass 

    def showSettingsWarning(self):
        pass

    def activate(self):
        ## Set our new cursor.
        # Neste método sempre estabelecemos o novo cursor com setCursor().
        self.canvas.setCursor(self.cursor)
        
        ## Check wether Geometry is a Line or a Polygon
        mc = self.canvas
        layer = mc.currentLayer()
        self.type = layer.geometryType()
        self.isPolygon = False
        if self.type == QGis.Polygon:
            self.isPolygon = True

    def resetRubberBand(self):
        self.rb.reset( self.type )

    def setRubberBandPoints(self,points):
        self.resetRubberBand()
        for point in points:
            update = point is points[-1]
            self.rb.addPoint( point, update )

    #def deactivate(self):
        # On Win7/64 it was failing if QGIS was closed with a layer opened
        # for editing with "'NoneType' object has no attribute 'Polygon'"
        # -> test QGis
    #    if QGis is not None:
    #        self.rb.reset(QGis.Polygon)
    #    self.points = []
    #    pass

    def isZoomTool(self):
        return False
  
  
    def isTransient(self):
        return False
    
    
    def isEditTool(self):
        return True

    def interpolacao(self, points):
        # Grafo Direcionado a ser criado 
        # para escolha do melhor caminho por programação dinâmica
        # Representação será por uma lista de listas, 
        # cada nó de uma etapa está ligado a todos os nós da próxima etapa
        grafo = []                               
        
        # Número de pontos marcado pelo usuário (retorna 1 ou 2)
        npoints = len(points)
        
        # Caso tenha apenas um ponto não podemos fazer nada :(
        # Retorno uma lista com 2 posições, sendo a primeira qualquer valor, pois será descartada
        # Somente agregaremos à linha os pontos da segunda posição em diante
        if npoints == 1: return [QgsPoint(1,1), points[0]], grafo, [], None
        
        # Caso o valor do segmento seja menor que 3*tolerância então retornaremos os próprios pontos (uma reta apenas)
        # A tolerância aqui é o erro gráfico. Como vamos inserir 2 pontos a princípio, teremos 3 segmentos e cada um desses não deve ser menor
        # que o erro gráfico
        #if self.pointsDist(points[0], points[1]) < float( QSettings().value(SETTINGS_NAME + "/tolerance", DEFAULT_TOLERANCE )):
        #    return points, grafo, [], None
        
        # Laço do primeiro ao penúltimo ponto (como eu estou fazendo agora só vão ter 2 pontos: o primeiro já será o penúltimo)
        for i in range(0, npoints-1):
            # Calcula conjunto de pontos que estão em reta perpendiculares ao segmento
            
            # Se 2 pontos coincidirem ocasionará um erro de divisão por 0 (distância entre eles é 0) no cálculo das retas perpendiculares
            # Neste caso vou retornar eles mesmo (geometria inválida)
            try:
                retas_perpendiculares = self.calcula_reta(points[i], points[i+1])
            except:
                return points, grafo, [], []
            

            
            # Vamos tentar escrever o grafo por uma lista de listas
            grafo.append([points[i]])
            grafo.extend(retas_perpendiculares)
        
        # Adiciona ao grafo último ponto marcado pelo usuário
        grafo.append([points[-1]])
        
        # Acha caminho otimizado pelo grafo
        result, p = self.acha_caminho(grafo, points)
        
        # Retorna lista de pontos QgsPoint que formam a linha
        return result, grafo, retas_perpendiculares, result
        
    def calcula_reta(self, p1, p2):
        erro_grafico = float( QSettings().value(SETTINGS_NAME + "/distmin", DEFAULT_DISTMIN ))
        pontos_acima_e_abaixo = int( QSettings().value(SETTINGS_NAME + "/qpontos", DEFAULT_QPONTOS )) # número de pontos acima e abaixo do ponto central (localizado no segmento que liga dois pontos marcados pelo operador)
        resolucao_y = float( QSettings().value(SETTINGS_NAME + "/espacamento", DEFAULT_ESPACAMENTO )) # espacamento vertical entre pontos do grafo
        max_seg = int( QSettings().value(SETTINGS_NAME + "/maxseg", DEFAULT_MAXSEG ) )
    
        # Vamos evitar cálculo do coeficiente angular para evitar divisão por 0
        
        # Calcula delta_x e delta_y (diferença em x e diferença em y)
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        
        # Calcula distância
        dist = sqrt(dx*dx + dy*dy)
        
        # dx e dy agora serão as componentes em x e y do vetor unitário referente ao vetor que vai de p1 a p2
        dx /= dist
        dy /= dist
        
        # Coordenadas x e y de p1 e p2
        x_p1 = p1.x()
        x_p2 = p2.x()
        y_p1 = p1.y()
        y_p2 = p2.y()
        #print 'x_p1 =', x_p1, '1/9 de x_p1 =', 
        
        # Vamos considerar aqui a resolução em y do raster para a distância entre os pontos marcados na reta perpendicular
        #resolucao_y = 2.5 # 3*self.camada_raster.rasterUnitsPerPixelY()
        
        # Cálculo das coordenadas x e y dos pontos sobre a linha p1p2
        #coord_x_sobre =   [8/9.*x_p1 + 1/9.*x_p2, 7/9.*x_p1 + 2/9.*x_p2, 2/3.*x_p1 + 1/3.*x_p2, 5/9.*x_p1 + 4/9.*x_p2, 4/9.*x_p1 + 5/9.*x_p2, 1/3.*x_p1 + 2/3.*x_p2, 2/9.*x_p1 + 7/9.*x_p2, 1/9.*x_p1 + 8/9.*x_p2]
        #coord_y_sobre =   [8/9.*y_p1 + 1/9.*y_p2, 7/9.*y_p1 + 2/9.*y_p2, 2/3.*y_p1 + 1/3.*y_p2, 5/9.*y_p1 + 4/9.*y_p2, 4/9.*y_p1 + 5/9.*y_p2, 1/3.*y_p1 + 2/3.*y_p2, 2/9.*y_p1 + 7/9.*y_p2, 1/9.*y_p1 + 8/9.*y_p2]
        #coord_x_sobre =   [2/3.*x_p1 + 1/3.*x_p2, 1/3.*x_p1 + 2/3.*x_p2]
        #coord_y_sobre =   [2/3.*y_p1 + 1/3.*y_p2, 1/3.*y_p1 + 2/3.*y_p2]        
        
        # Segmentos que vão ficar
        n = round(dist/erro_grafico)
        # n = float(n)
        
		# Estabelece quantidade máxima de segmentos
        if n > max_seg:
            n = float(max_seg)
        
		
        #n = 3.0
        # Quantidade de pontos a inserir
        q = int(n-1)
        #q = 2
        
        # Caso não insiramos nenhum ponto dá erro 
        if q == 0 or q == -1:
            raise ValueError("0 pontos inseridos")
            
        #print 'oi, dist=', dist, ' q pontos=', q, 'n segmentos=', n
            
        #print 'n=', n
        #  
        
        coord_x_sobre = []
        coord_y_sobre = []
        #print 'coord_x_sobre=', coord_x_sobre
        #print 'coord_y_sobre=', coord_y_sobre
        
        #print range(q, 0, -1)
        
        for i in range(q, 0, -1):
            coord_x_sobre.append((i/(n))*x_p1 + (1. - i/n)*x_p2) 
            coord_y_sobre.append((i/(n))*y_p1 + (1. - i/n)*y_p2) 
        
        #print 'coord_x_sobre ultimo=', coord_x_sobre
        #print 
        
        # Vamos gerar uma lista de listas de pontos que estão perpendiculares à linha em diferentes alturas da linha (um terço, metade, etc)
        retas_perpendiculares = []
        
        
        
        for i in range(len(coord_x_sobre)):
            # Pontos marcados acima do ponto central
            x_acima = [(coord_x_sobre[i] - resolucao_y*j*dy) for j in range(1,pontos_acima_e_abaixo)]
            y_acima = [(coord_y_sobre[i] + resolucao_y*j*dx) for j in range(1,pontos_acima_e_abaixo)]

            # Pontos marcados abaixo do ponto central
            x_abaixo = [(coord_x_sobre[i] + resolucao_y*j*dy) for j in range(1,pontos_acima_e_abaixo)]
            y_abaixo = [(coord_y_sobre[i] - resolucao_y*j*dx) for j in range(1,pontos_acima_e_abaixo)]        
        
            # Forma lista de coordenadas x e lista de coordenadas y
            lista_de_x = [coord_x_sobre[i]] + x_acima + x_abaixo
            lista_de_y = [coord_y_sobre[i]] + y_acima + y_abaixo
        
            # Cria lista de Pontos com as coordenadas dos pontos desta linha perpendicular 
            # (pontos estão fora de ordem, tomara que não interfira no resultado mais adiante!!)
            lista_pontos_perpendiculares = [QgsPoint(lista_de_x[j], lista_de_y[j]) for j in range(len(lista_de_x))]

            retas_perpendiculares.append(lista_pontos_perpendiculares)
        
        return retas_perpendiculares
        
    # Primeira função de mérito, de maximização do somatório dos quadrados dos níveis de cinza (dos nós)
    def Ep1(self, no1, no2, no3):
        # Media dos níveis de cinza das bandas para 3 pontos no1, no2 e no3
        no1_media = self.nivel_cinza_media(self.camada_raster, no1)
        no2_media = self.nivel_cinza_media(self.camada_raster, no2)
        no3_media = self.nivel_cinza_media(self.camada_raster, no3)       
        
        return no1_media*no1_media + no2_media*no2_media + no3_media*no3_media
        #return no1_media + no2_media + no3_media
   
    def Ep2(self, no1, no2, no3):
        # Distância total de no1 a no3
        no1no2 = self.pointsDist(no1, no2) 
        no2no3 = self.pointsDist(no2, no3) 
        #distTotal = no1no2 + no2no3
        
        # Área do trapézio formado por no1 e no2
        #areaNo1No2 = (nc_no1 + nc_no2)*no1no2/2.
        #areaNo2No3 = (nc_no2 + nc_no3)*no2no3/2.
        #mediaNo1No2 = 
        
        # Níveis de cinza dos nós em questão
        nc_no1 = self.nivel_cinza_media(self.camada_raster, no1)
        nc_no2 = self.nivel_cinza_media(self.camada_raster, no2)
        nc_no3 = self.nivel_cinza_media(self.camada_raster, no3)
        
        # Média dos níveis de cinza para os segmentos no1no2 e no2no3. 
        #Corresponde a Gm(Delta Si), ou seja, ao nível médio de cinza para o segmento.
        mediaNo1No2 = (nc_no1 + nc_no2)/2.
        mediaNo2No3 = (nc_no2 + nc_no3)/2.
        
        # Objetivo é minimizar a variação de nível de cinza. Por isto a função pega o nível de cinza do ponto e diminui ele da média.
        #GdDelta = (nc_no1 + nc_no2 + nc_no3)/3
        #somatorio_ep2 = (nc_no1 - GdDelta)**2 + (nc_no2 - GdDelta)**2 + (nc_no3 - GdDelta)**2
        #somatorio_ep2 = (nc_no1 - (nc_no1 + nc_no2)/2.)**2 + (nc_no2 - (nc_no2 + nc_no3)/2.)**2 
        
        # Somatório vai ser o somatório das integrais da função (Gd-Gm)^2 em cada segmento (equivale a uma soma de áreas de trapézios) 
        #somatorio_ep2 = ((nc_no1 - mediaNo1No2)**2 + (nc_no2 - mediaNo1No2)**2)*no1no2/2. + ((nc_no2 - mediaNo2No3)**2 + (nc_no3 - mediaNo2No3)**2)*no2no3/2. 
        somatorio_ep2 = ((nc_no1 - mediaNo1No2)*(nc_no1 - mediaNo1No2) + (nc_no2 - mediaNo1No2)*(nc_no2 - mediaNo1No2)) + ((nc_no2 - mediaNo2No3)*(nc_no2 - mediaNo2No3) + (nc_no3 - mediaNo2No3)*(nc_no3 - mediaNo2No3)) 
        
        return somatorio_ep2
        '''
        # Cálculos para o segmento de no1 até no2
        dist_no1_no2 = self.pointsDist(no1, no2)
        GdDelta_no1_no2 = (nc_no1 + nc_no2)/2 # média dos níveis de cinza de no1 e no2
        somatorio_no1_no2 = (nc_no1 - GdDelta_no1_no2)**2 + (nc_no2 - GdDelta_no1_no2)**2
        
        # Cálculos para o segmento de no2 até no3
        dist_no2_no3 = self.pointsDist(no2, no3)
        GdDelta_no2_no3 = (nc_no2 + nc_no3)/2
        somatorio_no2_no3 = (nc_no2 - GdDelta_no2_no3)**2 + (nc_no3 - GdDelta_no2_no3)**2
        '''
    
    def Ep4(self, no1, no2, no3):
		pass
        # Função que diz que a curvatura na rodovia deve ser mínima
        
        # Distância total de no1 a no3
		no1no2 = self.pointsDist(no1, no2) 
		no2no3 = self.pointsDist(no2, no3) 
		no1no3 = self.pointsDist(no1, no3)
		distTotal = no1no2 + no2no3
        
        # Ângulo interno entre no1no2no3 calculado pela Lei dos Cossenos
		cosseno_interno = ( (no1no2*no1no2 + no2no3*no2no3 - no1no3*no1no3) / (2*no1no2*no2no3) ) 
    
        # Como o ângulo de deflexão é o ângulo suplementar: cos(180-y) = -cos(y) 
		cosseno_deflexao = -1*cosseno_interno
		
        
		#return (1 + cosseno_deflexao) /distTotal
		return (1 + cosseno_deflexao) /no1no2
        
        
    def nivel_cinza_media(self, raster, ponto):
        # Identifica provedor da camada (se é postgres, gdal (para raster), etc)
        provedor = raster.dataProvider()        

        # Pega Sistema de coordenadas atual (on-the-fly). Observa-se que ele precisa ser projetado     
        mapCanvasSrs = self.iface.mapCanvas().mapRenderer().destinationCrs()

        # Sistema de coordenadas do raster
        rasterSrs = raster.crs()
        
        # Transformação entre o sistema de coordenadas atual (on-the-fly) e o sistema de coordenadas do raster
        srsTransform = QgsCoordinateTransform(mapCanvasSrs, rasterSrs)
        
        # Transformação dos nós para sistema de coordenadas do raster
        # self.camada_raster.dataProvider().identify(QgsCoordinateTransform(self.canvas.mapRenderer().destinationCrs(), self.camada_raster.crs()).transform(self.canvas.getCoordinateTransform().toMapCoordinates(x, y)), QgsRaster.IdentifyFormatValue).results()
        ponto_transform = srsTransform.transform(ponto)
        
        # Valores dos níveis de cinza dos nós no raster (são dicionários, a cada banda corresponde a um nível de cinza)
        ponto_valor = provedor.identify(ponto_transform, QgsRaster.IdentifyFormatValue).results()
        
        # Valores das médias para os níveis de cinza. Estrada tem boa resposta espectral (nível de cinza alto) nas bandas R, G, B.
        # Portanto só funciona com imagens RGB. Com outras, que incluem outras bandas, o resultado ficará comprometido. Problema a ser solucionado...
        
        # Vamos retornar a média para as 3 primeiras bandas (esperamos que estas sejam R,G e B...) se imagem tiver mais que 3 bandas
        if len(ponto_valor) > 3:
            ponto_media = sum([ponto_valor[i] for i in [1, 2, 3]])/3.
        else:
            ponto_media = sum([ponto_valor[i] for i in ponto_valor])/float(len(ponto_valor))
        
        return ponto_media        
        
    def acha_caminho(self, grafo, points):
        # Declara lista de tabelas (dicionários em python) que vai nos ajudar na recursão
        lista_dic = []
        lista_dic.append({})
        
        # Pega nó inicial do grafo
        no_inicial = grafo[0][0]                                                                                              
        
        # Preenche passo inicial da iteração com 0s 
        for no in grafo[1]:
            lista_dic[0][(no_inicial, no)] = {'MAX': 0} # ou = 0, vamos ver...
        
        # Laço passando pelas etapas do grafo
        for i in range(len(grafo)):
            # Etapa atual
            g = grafo[i]

            # Teste para ver se existe próximas etapas no Grafo. 
            # Como o algoritmo pega vértices de 3 etapas, na penúltima etapa ele sai do laço
            try:
                g_k_mais_dois = grafo[i+2]
            except:
                # print 'Penultima etapa. Saindo do laço'
                break
        
            # Etapa seguinte
            g_k_mais_um = grafo[i+1]
        
            # Adiciona um dicionário para armazenar os resultados desta etapa
            lista_dic.append({})
        
            # Para todas as etapas dos nós nas etapas posterior e depois que a posterior
            for j in range(len(g_k_mais_um)):
                for k in range(len(g_k_mais_dois)):
                    # Vou armazenar cada possibilidade em variáveis (estas são as que serão fixadas)
                    no_k_mais_um = g_k_mais_um[j]
                    no_k_mais_dois = g_k_mais_dois[k]
                                        
                    # Cria dicionário (linha da tabela auxílio para programação dinâmica) 
                    lista_dic[i+1][(no_k_mais_um, no_k_mais_dois)] = {}
                                        
                    #return lista_dic, points
                
                    # Laço para percorrer todos nós da etapa atual (este nó será variável e descobriremos o melhor nó para (no_k_mais_um, no_k_mais_dois)
                    for z in range(len(g)):
                        no_atual = g[z] # um dentre os nós da etapa atual
                        
                        # Se for impossível calcular (por exemplo, ponto fora do raster), então retorna apenas
                        # os pontos marcados pelo usuário 
                        try:                                            
                            res_parcial = lista_dic[i][(no_atual, no_k_mais_um)]['MAX'] + (self.Ep1(no_atual, no_k_mais_um, no_k_mais_dois) - self.Ep2(no_atual, no_k_mais_um, no_k_mais_dois))*self.Ep4(no_atual, no_k_mais_um, no_k_mais_dois)
                        except:
                            return points, points                             
                        
                        # Adiciona valor calculado para ((no_k_mais_um, no_k_mais_dois), no_atual)
                        lista_dic[i+1][(no_k_mais_um, no_k_mais_dois)][no_atual] = res_parcial
                                            

                    # Extrai máximo das opções buscadas
                    lista_dic[i+1][(no_k_mais_um, no_k_mais_dois)]['MAX'] = max([lista_dic[i+1][(no_k_mais_um, no_k_mais_dois)][el] for el in lista_dic[i+1][(no_k_mais_um, no_k_mais_dois)]])
                    


        # Inverte a lista de dicionários (lista de tabelas que apoiam a programação dinâmica)
        lista_dic_inv = lista_dic[-1:0:-1] # Ponto de partida da lista, posição final e passo
        
        # Pega primeiro valor da lista invertida (se refere aos últimos nós)
        prima = lista_dic_inv[0]
        
        # Pega dupla de ultimos nos conforme maior valor 'MAX', o valor a eles correspondente e o nó escolhido
        ultimos, f_acum, no_escolhido = max([(chave, valor['MAX'], self.no_maximo(valor)) for chave, valor in prima.iteritems()], key = lambda par_facum: par_facum[1])
    
        no_anterior, no_posterior = ultimos # aqui no_posterior é o ultimo e no_anterior é o penultimo
    
    
        # Declara caminho otimizado.
        # Vamos preenche-lo de tras para frente e o invertemos depois
        caminho = []
        caminho += (no_posterior, no_anterior, no_escolhido)
    
        # Preenche restante do caminho
        for elemento in lista_dic_inv[1::]:
            no_posterior, no_anterior = no_anterior, no_escolhido
            no_escolhido = self.no_maximo(elemento[(no_anterior, no_posterior)])
            # print 'no_escolhido_dessa_vez = ', no_escolhido
            caminho.append(no_escolhido)    
        
       
        # Inverte caminho para ficar certo ja que esta de tras para frente
        caminho.reverse()
    
        return caminho, points
            

    def no_maximo(self, dic):
        for elem in dic:
            if elem == 'MAX':
                continue
            if dic[elem] == dic['MAX']:
                return elem

    
    def simplifyPoints( self, points, tolerance):
        geo = QgsGeometry.fromPolyline( points )
        geo = geo.simplify( tolerance );
        return geo.asPolyline()


    def pointsDist(self, a, b):
        dx = a.x()-b.x()
        dy = a.y()-b.y()
        return sqrt( dx*dx + dy*dy )
        
    # Aqui vamos saber se a tecla ctrl está pressionada
    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            if self.mCtrl is True:
                self.mCtrl = False
            else:
                self.mCtrl = True
        if event.key() == Qt.Key_Escape:
            self.createFeature(self.pontos_interpolados)
            self.resetPoints()
            self.resetRubberBand()
            self.canvas.refresh() 
            
    # Se ela é pressionada e mantida vamos fazer isso
    def keyReleaseEvent(self,  event):
        #if event.key() == Qt.Key_Control:
        #    self.mCtrl = False
        #remove the last added point when the delete key is pressed
        if event.key() == Qt.Key_Backspace:
            self.removeLastPoint()            

    def removeLastPoint(self):
        
        # Com 0 elementos na lista de pontos marcados vamos apenas jogar uma mensagem para usuário
        # Estamos nos referindo a self.points porque ao mudar de ação, por exemplo para o Pan (com o ícone da mão)
        # e voltar para nosso plugin apertando o botão direito do mouse, acontece alguma coisa que esvazia a lista de self.points.
        # Por isso self.points retorna ao estágio de como se estivéssemos iniciando a linha
        if len(self.points) == 0:
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Nenhum ponto marcado ainda')
        
        # Com 1 elemento vamos retirar esse elemento 
        elif len(self.points) == 1:
            self.points.pop()
            self.pontos_interpolados.pop()
        
        # Com mais de um elemento vamos retornar ao penúltimo passo. Isso significa dizer que vamos retirar o último elemento
        # da lista de pontos marcados 
        else:
            penultimo_elemento_marcado = self.points[-2]
            self.pontos_interpolados = self.pontos_interpolados[0:self.pontos_interpolados.index(penultimo_elemento_marcado)+1]
            self.points.pop()
            
            



        '''
        # Retira último ponto adicionado (tanto de self.points como de self.pontos_interpolados - estes são coincidentes)
        try:
            self.points.pop()
            self.pontos_interpolados.pop()
        # Senão podemos é porque não há nenhum ponto para tirar
        except:
            QMessageBox.information(self.iface.mainWindow(), 'Aviso', 'Nenhum ponto marcado ainda')
        
        


        # Retira últimos outros 2 últimos pontos interpolados (para remover toda última interpolação - adicionamos 2 pontos entre um inicial e um final)
        try:
            self.pontos_interpolados.pop()
            self.pontos_interpolados.pop()
        # Se não podemos, não fazemos nada (pode acontecer caso haja somente o primeiro ponto adicionado)
        except:
            pass
        '''    
    
    
            
            
