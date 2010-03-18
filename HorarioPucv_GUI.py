# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import re
import urllib
import urllib2
import cookielib
import data_rc
import sip
from NavegaPucv import NavegaPucv

version = '1.3.0b'

class Worker(QtCore.QThread):
    def iniciar(self, rut_num, rut_dv, user_pas):
        self.rut_num = rut_num
        self.rut_dv = rut_dv
        self.np = NavegaPucv(rut_num, rut_dv, user_pas)
        self.start()

    def run(self):
        self.emit(QtCore.SIGNAL("actOutput"), "Conectando al navegador...")
        self.emit(QtCore.SIGNAL("actProgreso(int)"),5)

        # Verifico si el usuario y contraseña son validos
        if not self.np.conectar():
            self.emit(QtCore.SIGNAL("actOutput"), "Error.")
            self.emit(QtCore.SIGNAL("error"),"Usuario o contraseña incorrectos")
            return
        else:
            self.emit(QtCore.SIGNAL("actOutput"), "OK. Conectado.")
        self.emit(QtCore.SIGNAL("actProgreso(int)"),10)

        # Pido la pagina con la lista de ramos...
        self.emit(QtCore.SIGNAL("actOutput"), "Descargando lista de ramos.")
        cursos = self.np.descargarListaCursos()
        self.emit(QtCore.SIGNAL("actProgreso(int)"),15)

        # En que periodo de clases.?

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

        lista = list()
        ramos = list()

        # Descargo la pagina de cada ramos, extraigo los horarios y los guardo
        self.emit(QtCore.SIGNAL("actOutput"), "Descargando horarios.")
        for dato in cursos:
            for curso in self.np.descargarCurso(dato):
                progreso = progreso + (avancePorCurso/3)
                self.emit(QtCore.SIGNAL("actProgreso(int)"), progreso)
                lista.append(curso)
            self.emit(QtCore.SIGNAL("actOutput"),
                "Horario encontrado para {0}".format(curso[1][1]))
            ramos.append((curso[1][0], curso[1][1]))

        avancePorCurso = 18/len(lista)
        self.emit(QtCore.SIGNAL("actProgreso(int)"), progreso)

        self.emit(QtCore.SIGNAL("actOutput"), "Generando archivo javascript...")
        fp = open('horario.js',"w")
        fp.write("var version = '%s';\n" % (version))
        fp.write("var periodo = '%s';\n" % (self.np.periodo))
        fp.write('var clases = new Array();\n')
        fp.write('var ramos = new Array();\n\n')

        for ramo in ramos:
            fp.write("var ramo = new Array();\n")
            fp.write("ramo[0] = '%s';\n" % (ramo[0])) # sigla de asignatura
            fp.write("ramo[1] = '%s';\n" % (ramo[1])) # nombre de asignatura
            fp.write("ramos.push(ramo);\n")

        for dato in lista:
            fp.write("var clase = new Array();\n")
            fp.write("clase[0] = %s;\n" % (dato[0])) # id de asignatura
            fp.write("clase[1] = '%s';\n" % (dato[1][0])) # sigla de asignatura
            fp.write("clase[2] = '%s';\n" % (dato[1][1])) # nombre de asignatura
            fp.write("clase[3] = %d;\n" % (dato[2])) # catedra o ayudantia ( 1 o 2 )
            fp.write("clase[4] = %d;\n" % (dato[3])) # dia (1 al 6)
            fp.write("clase[5] = %s;\n" % (dato[4])) # bloque
            fp.write("clase[6] = '%s';\n" % (dato[5])) # sala
            fp.write("clases.push(clase);\n\n")
            progreso = progreso + avancePorCurso
            self.emit(QtCore.SIGNAL("actProgreso(int)"), progreso)

        fp.write('function cargarHorario()\n{\n\tvar sigla = \'<table width="80%" border="1" cellpadding="3" cellspacing="0" align="center"><tr><td class="titulo_td">Sigla</td><td class="titulo_td">Nombre Ramo</td></tr>\';\n\tfor(i=0;i < clases.length; i++)\n\t{\n\t\tid = clases[i][4]+\'-\'+clases[i][5];\n\t\tdocument.getElementById(id).innerHTML = clases[i][1] + \'<br>\'+clases[i][6];\n\t\tif(clases[i][3] == 1)\n\t\t\tdocument.getElementById(id).className = "td_catedra";\n\t\telse if(clases[i][3] == 2)\n\t\t\tdocument.getElementById(id).className = "td_ayudantia";\n\t}')
        fp.write('\n\tfor(i=0;i < ramos.length;i++)\n\t{\n\t\tsigla = sigla + \'<tr><td>\' + ramos[i][0] + \'</td><td>\' + ramos[i][1] + \'</td></tr>\';\n\t}')
        fp.write("\n\tdocument.getElementById('siglas').innerHTML = sigla;")
        fp.write("\n\tdocument.getElementById('version').innerHTML = version;")
        fp.write("\n\tdocument.getElementById('periodo').innerHTML = periodo;")
        fp.write("}")
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
        mb.setWindowTitle("Información:")
        mb.setText("Tu horario se ha descargado correctamente.\nAbre el archivo horario.html para verlo.")
        mb.setIcon(QtGui.QMessageBox.Information)
        mb.show()
        self.groupBox.setEnabled(1)

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
            self.error("Debes ingresar el dígito verificador de tu rut")
            self.rut_dv.setFocus()
            return
        if self.password.text().isEmpty():
            self.error("Debes ingresar la contraseña de tu navegador académico")
            self.password.setFocus()
            return
        self.thread.iniciar(self.rut_num.text(), self.rut_dv.text(),
            self.password.text())

#        print '\nHorario listo. Abre el archivo horario.html para ver tu horario.'

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
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Horario Pucv v" + version, None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_rut.setText(QtGui.QApplication.translate("MainWindow", "Rut:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_separador.setText(QtGui.QApplication.translate("MainWindow", " - ", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_contrasenya.setText("Contraseña:")
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

