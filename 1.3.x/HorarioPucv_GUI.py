# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import webbrowser
import cookielib
import data_rc
import sip
from NavegaPucv import NavegaPucv

version = '1.3.2b'

class Worker(QtCore.QThread):
    def iniciar(self, rut_num, rut_dv, user_pas):
        self.rut_num = rut_num
        self.rut_dv = rut_dv
        self.np = NavegaPucv(rut_num, rut_dv, user_pas)
        self.start()

    def run(self):
        self.emit(QtCore.SIGNAL("actOutput"), "Conectando al navegador...")
        self.emit(QtCore.SIGNAL("actProgreso(int)"),5)

        # Verifico si el usuario y contrase�a son validos
        if not self.np.conectar():
            self.emit(QtCore.SIGNAL("actOutput"), "Error.")
            self.emit(QtCore.SIGNAL("error"),"Usuario o contrase�a incorrectos")
            return
        else:
            self.emit(QtCore.SIGNAL("actOutput"), "OK. Conectado.")
        self.emit(QtCore.SIGNAL("actProgreso(int)"),10)

        # Pido la pagina con la lista de ramos...
        self.emit(QtCore.SIGNAL("actOutput"), "Descargando lista de ramos.")
        cursos = self.np.descargarListaCursos()
        self.emit(QtCore.SIGNAL("actProgreso(int)"),15)

        numeroCursos = len(cursos)

        if numeroCursos == 0:
            self.emit(QtCore.SIGNAL("actOutput"),
                "No hay cursos en tu horario.")
            return

        self.emit(QtCore.SIGNAL("actOutput"),
            "Hay {0} ramos inscritos.".format(len(cursos)))
        self.emit(QtCore.SIGNAL("actProgreso(int)"),20)

        avancePorCurso = 60/numeroCursos
        progreso = 20
        numeroHorarios = 0
        #lista = list()
        lista2 = {}
        ramos = list()

        # Descargo la pagina de cada ramos, extraigo los horarios y los guardo
        self.emit(QtCore.SIGNAL("actOutput"), "Descargando horarios.")
        for dato in cursos:
            for curso in self.np.descargarCurso(dato):
                progreso = progreso + (avancePorCurso/3)
                self.emit(QtCore.SIGNAL("actProgreso(int)"), progreso)
                idbloque = "{0}-{1}".format(curso[3],curso[4])
                if not idbloque in lista2:
                    lista2[idbloque] = [curso]
                else:
                    lista2[idbloque].append(curso)
                #lista.append(curso)
                numeroHorarios = numeroHorarios + 1
            self.emit(QtCore.SIGNAL("actOutput"),
                "Horario encontrado para {0}".format(curso[1][1]))
            ramos.append((curso[1][0], curso[1][1]))

        avancePorCurso = 18/numeroHorarios
        self.emit(QtCore.SIGNAL("actProgreso(int)"), progreso)

        self.emit(QtCore.SIGNAL("actOutput"), "Generando archivo javascript...")
        fp = open('horario.js',"w")
        fp.write("var version = '%s';\n" % (version))
        fp.write("var periodo = '%s';\n" % (self.np.periodo))
        fp.write('var clases = new Array();\n')
        fp.write('var topes = new Array();\n')
        fp.write('var ramos = new Array();\n\n')

        for ramo in ramos:
            fp.write("var ramo = new Array();\n")
            fp.write("ramo[0] = '%s';\n" % (ramo[0])) # sigla de asignatura
            fp.write("ramo[1] = '%s';\n" % (ramo[1])) # nombre de asignatura
            fp.write("ramos.push(ramo);\n")

        for idbloque,datos in lista2.iteritems():
            if len(datos) > 1:
                fp.write("var tope = new Array();\n")
                for tope in datos:
                    fp.write("var clase = new Array();\n")
                    fp.write("clase[0] = %s;\n" % (tope[0])) # id de asignatura
                    fp.write("clase[1] = '%s';\n" % (tope[1][0])) # sigla de asignatura
                    fp.write("clase[2] = '%s';\n" % (tope[1][1])) # nombre de asignatura
                    fp.write("clase[3] = %d;\n" % (tope[2])) # catedra o ayudantia ( 1 o 2 )
                    fp.write("clase[4] = %d;\n" % (tope[3])) # dia (1 al 6)
                    fp.write("clase[5] = %s;\n" % (tope[4])) # bloque
                    fp.write("clase[6] = '%s';\n" % (tope[5])) # sala
                    fp.write("tope.push(clase);\n\n")
                    progreso = progreso + avancePorCurso
                    self.emit(QtCore.SIGNAL("actProgreso(int)"), progreso)
                fp.write("topes.push(tope);\n\n")
                
            else:
                fp.write("var clase = new Array();\n")
                fp.write("clase[0] = %s;\n" % (datos[0][0])) # id de asignatura
                fp.write("clase[1] = '%s';\n" % (datos[0][1][0])) # sigla de asignatura
                fp.write("clase[2] = '%s';\n" % (datos[0][1][1])) # nombre de asignatura
                fp.write("clase[3] = %d;\n" % (datos[0][2])) # catedra o ayudantia ( 1 o 2 )
                fp.write("clase[4] = %d;\n" % (datos[0][3])) # dia (1 al 6)
                fp.write("clase[5] = %s;\n" % (datos[0][4])) # bloque
                fp.write("clase[6] = '%s';\n" % (datos[0][5])) # sala
                fp.write("clases.push(clase);\n\n")
                progreso = progreso + avancePorCurso
                self.emit(QtCore.SIGNAL("actProgreso(int)"), progreso)

        buf = """var dias = ["Lunes", "Martes","Miercoles","Jueves","Viernes","Sabado"];
var bloques = new Array();
bloques['1'] = '1-2';
bloques['3'] = '3-4';
bloques['5'] = '5-6';
bloques['7'] = '7-8';
bloques['9'] = '9-10';
bloques['11'] = '11-12';
bloques['13'] = '13-14';

function cargarHorario()
{
    var sigla = '<table width="80%" border="1" cellpadding="3" cellspacing="0" align="center"><tr><td class="titulo_td">Sigla</td><td class="titulo_td">Nombre Ramo</td></tr>';
    for(i=0;i < clases.length; i++)
    {
        id = clases[i][4]+'-'+clases[i][5];
        document.getElementById(id).innerHTML = '<div onmouseover="showBox(\\''+clases[i][2]+'\\', this)" onmouseout="hideBox()">'+clases[i][1] + '<br>'+clases[i][6]+'</div>';
        if(clases[i][3] == 1)
            document.getElementById(id).className = "td_catedra";
        else if(clases[i][3] == 2)
            document.getElementById(id).className = "td_ayudantia";
    }
    var i;
    var j;
    var tabla_topes = document.getElementById('tabla_topes');
    var buf = '<TABLE width="90%" border="1" cellpadding="0" cellspacing="0" align="center"><tr><td class="titulo_td" colspan="2">Detalle Topes de Horario</td></tr>';
    for (i in topes)
    {
        id = topes[i][0][4]+'-'+topes[i][0][5];
        document.getElementById(id).className = "td_tope";
        buf += '<tr><td class="topes" rowspan="'+topes[i].length+'">'+ dias[topes[i][0][4]-1] + '<br><b>Bloque '+ bloques[topes[i][0][5]] +'</b></td>';
        for(j in topes[i])
        {
            if(j != 0)
                buf += '<tr>';
            buf += '<td>'+topes[i][j][1]+' '+topes[i][j][2]+', Sala '+topes[i][j][6]+'</td>';
            if(j == 0)
                buf += '</tr>';
        }
        buf += '</tr>';
    }
    buf += '</table>';
    tabla_topes.innerHTML = buf;
    for(i=0;i < ramos.length;i++)
    {
        sigla = sigla + '<tr><td>' + ramos[i][0] + '</td><td>' + ramos[i][1] + '</td></tr>';
    }
    document.getElementById('siglas').innerHTML = sigla;
    document.getElementById('version').innerHTML = version;
    document.getElementById('periodo').innerHTML = periodo;
}
"""
        fp.write(buf)
        fp.close()
        self.emit(QtCore.SIGNAL("actOutput"), "Listo.")
        self.emit(QtCore.SIGNAL("actProgreso(int)"), 100)
        self.emit(QtCore.SIGNAL("listo"))


class Ui_MainWindow(object):
    def error( self, mensaje ):
        self.groupBox.setEnabled(1)
        self.progreso.hide()
        self.lbl_preconectar.setText(mensaje)
        self.lbl_preconectar.show()

    def listo(self):
        mb = QtGui.QMessageBox(self.MainWindow)
        QtCore.QObject.connect(mb, QtCore.SIGNAL("buttonClicked(QAbstractButton*)"), self.OKPresionado)
        mb.setWindowTitle("Informaci�n:")
        mb.setText("Tu horario se ha descargado correctamente.\nPresiona OK para verlo en tu explorador.")
        mb.setIcon(QtGui.QMessageBox.Information)
        mb.show()
        self.password.clear()
        self.groupBox.setEnabled(1)

    def OKPresionado(self,boton):
        webbrowser.open("horario.html")
        
    def conectar(self):
        self.groupBox.setEnabled(0)
        self.lv_output.clear()
        self.lbl_preconectar.hide()
        self.progreso.setValue(0)
        self.progreso.show()
        if self.rut_num.text().isEmpty():
            self.error("Debes ingresar tu rut")
            self.rut_num.setFocus()
            return
        if self.rut_dv.text().isEmpty():
            self.error("Debes ingresar el d�gito verificador de tu rut")
            self.rut_dv.setFocus()
            return
        if self.password.text().isEmpty():
            self.error("Debes ingresar la contrase�a de tu navegador acad�mico")
            self.password.setFocus()
            return
        self.thread.iniciar(self.rut_num.text(), self.rut_dv.text(),
            self.password.text())

    def setupUi(self, MainWindow):
        self.thread = Worker()
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(433, 320)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icono/icono"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setMaximumSize(QtCore.QSize(433, 320))

        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 411, 71))
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")

        self.lbl_rut = QtGui.QLabel(self.groupBox)
        self.lbl_rut.setGeometry(QtCore.QRect(10, 30, 31, 20))
        self.lbl_rut.setObjectName("lbl_rut")

        self.rut_num = QtGui.QLineEdit(self.groupBox)
        self.rut_num_validator = QtGui.QIntValidator(1,99999999, self.rut_num)
        self.rut_num.setGeometry(QtCore.QRect(40, 30, 61, 20))
        self.rut_num.setObjectName("rut_num")
        self.rut_num.setValidator(self.rut_num_validator)

        self.lbl_separador = QtGui.QLabel(self.groupBox)
        self.lbl_separador.setGeometry(QtCore.QRect(100, 30, 16, 20))
        self.lbl_separador.setObjectName("lbl_separador")

        self.rut_dv = QtGui.QLineEdit(self.groupBox)
        self.rut_dv_validator = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9kK]"), self.rut_dv)
        self.rut_dv.setGeometry(QtCore.QRect(110, 30, 21, 20))
        self.rut_dv.setObjectName("rut_dv")
        self.rut_dv.setMaxLength(1)
        self.rut_dv.setValidator(self.rut_dv_validator)

        self.lbl_contrasenya = QtGui.QLabel(self.groupBox)
        self.lbl_contrasenya.setGeometry(QtCore.QRect(150, 30, 71, 20))
        self.lbl_contrasenya.setObjectName("lbl_contrasenya")

        self.password = QtGui.QLineEdit(self.groupBox)
        self.password.setGeometry(QtCore.QRect(220, 30, 81, 20))
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName("password")

        self.btn_conectar = QtGui.QPushButton(self.groupBox)
        self.btn_conectar.setGeometry(QtCore.QRect(320, 20, 81, 31))
        self.btn_conectar.setObjectName("btn_conectar")

        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 110, 411, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")

        self.progreso = QtGui.QProgressBar(self.centralwidget)
        self.progreso.setEnabled(True)
        self.progreso.setGeometry(QtCore.QRect(10, 90, 411, 23))
        self.progreso.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.progreso.setProperty("value", QtCore.QVariant(0))
        self.progreso.setTextVisible(True)
        self.progreso.setOrientation(QtCore.Qt.Horizontal)
        self.progreso.setObjectName("progreso")
        self.progreso.hide()

        self.lbl_preconectar = QtGui.QLabel(self.centralwidget)
        self.lbl_preconectar.setGeometry(QtCore.QRect(0, 90, 431, 21))
        self.lbl_preconectar.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_preconectar.setObjectName("lbl_preconectar")

        self.lv_output = QtGui.QListWidget(self.centralwidget)
        self.lv_output.setGeometry(QtCore.QRect(10, 130, 411, 150))
        self.lv_output.setObjectName("lv_output")

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 433, 19))
        self.menubar.setObjectName("menubar")

        self.menuAyuda = QtGui.QMenu(self.menubar)
        self.menuAyuda.setObjectName("menuAyuda")

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

        MainWindow.setStatusBar(self.statusbar)

        self.actionPreguntas_Frecuentes = QtGui.QAction(MainWindow)
        self.actionPreguntas_Frecuentes.setObjectName("actionPreguntas_Frecuentes")
        self.actionBuscar_Actualizacion = QtGui.QAction(MainWindow)
        self.actionBuscar_Actualizacion.setObjectName("actionBuscar_Actualizacion")
        self.actionAcerca_de_HorarioPucv = QtGui.QAction(MainWindow)
        self.actionAcerca_de_HorarioPucv.setObjectName("actionAcerca_de_HorarioPucv")

        self.menuAyuda.addAction(self.actionPreguntas_Frecuentes)
        self.menuAyuda.addSeparator()
        self.menuAyuda.addAction(self.actionBuscar_Actualizacion)
        self.menuAyuda.addSeparator()
        self.menuAyuda.addAction(self.actionAcerca_de_HorarioPucv)
        self.menubar.addAction(self.menuAyuda.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.btn_conectar, QtCore.SIGNAL("clicked(bool)"), self.conectar)
        QtCore.QObject.connect(self.thread, QtCore.SIGNAL("actProgreso(int)"), self.progreso.setValue)
        QtCore.QObject.connect(self.thread, QtCore.SIGNAL("actOutput"), self.lv_output.addItem)
        QtCore.QObject.connect(self.thread, QtCore.SIGNAL("error"), self.error)
        QtCore.QObject.connect(self.thread, QtCore.SIGNAL("listo"), self.listo)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "HorarioPucv v" + version, None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_rut.setText(QtGui.QApplication.translate("MainWindow", "Rut:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_separador.setText(QtGui.QApplication.translate("MainWindow", " - ", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_contrasenya.setText("Contrase�a:")
        self.btn_conectar.setText(QtGui.QApplication.translate("MainWindow", "Conectar!", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_preconectar.setText(QtGui.QApplication.translate("MainWindow", "Ingresa tus datos y presiona \"Conectar!\" para descargar tu horario.", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAyuda.setTitle(QtGui.QApplication.translate("MainWindow", "Ayuda", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreguntas_Frecuentes.setText(QtGui.QApplication.translate("MainWindow", "Preguntas Frecuentes", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBuscar_Actualizacion.setText(QtGui.QApplication.translate("MainWindow", "Buscar Actualizaciones", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAcerca_de_HorarioPucv.setText(QtGui.QApplication.translate("MainWindow", "Acerca de HorarioPucv", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

