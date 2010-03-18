#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import urllib
import urllib2
import cookielib
import re
import sys

class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        if str(headers).find('nofoto.JPG'):
            raise NoFotoError
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

opener = urllib2.build_opener(MyHTTPRedirectHandler)
urllib2.install_opener(opener)

class NoFotoError(Exception):
    def __init__(self, msg = "No tiene foto."):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class ErrorEnLogin(Exception):
    def __init__(self, msg = "Rut o clave incorrectos."):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class NavegaPucv:
    def __init__(self, rut_num, rut_dv, user_pas):
        # Parametros de login para enviar via POST
        self.params = urllib.urlencode({'rut_num': rut_num, 'rut_dv': rut_dv,\
        'user_pas': user_pas, 'rb_aplicacion': 1})
        self.CJ = cookielib.CookieJar()
        self.conectado = False
        # Las expresiones regulares para extraer los datos
        self.reNombreCurso = re.compile("class=\"w80\">\s+<strong>\s+(.+?)</strong>")
        self.reHorario = re.compile("<form name=sala action=horario-sala.php method=post>(.+)")
        self.reAyudantia = re.compile("Ay. Cátedra</td>(.+)")
        self.reColumnas = re.compile("<tr(.+?)>(.+?)</tr>")
        self.reFilas = re.compile("<td(.?)>(.+?)</td>")
        self.reBloques = re.compile("(\d+)(.+?) - (\d+)")
        self.reSala = re.compile("<a(.+?)>(.+?)</a>")
        self.periodo = ''

    def conectar(self):
        request = urllib2.Request("https://nave10.ucv.cl/inicio/signon.php", self.params)
        f = urllib2.urlopen(request)
        text = f.read()
        # Verifico si el usuario y contraseña son validos
        reLogin = re.compile("El usuario y/o clave no existen")
        login = reLogin.findall(text)
        if login:
            return False
        # Se guarda la sesion valida para usarla despues
        self.CJ.extract_cookies(f, request)
        self.conectado = True
        return True
    
    def descargarListaCursos(self):
        """
        Descarga desde la pagina de la ficha consolidada el listado de cursos
        inscritos en el periodo academico actual y sus respectivos links.

        Devuelve una lista conteniendo los datos de cada curso.
        [(curso1),(curso2),(curso3),...]
        """
        if not self.conectado:
            return
        request = urllib2.Request("https://nave10.ucv.cl//alumno/fichas/ficha_consolidada.php")
        self.CJ.add_cookie_header(request)
        f = urllib2.urlopen(request)
        texto = f.read()
        # En que periodo de clases.?
        rePeriodo = re.compile("<strong>Período:</strong>(.+?)&nbsp;")
        periodo = rePeriodo.findall(texto)
        if periodo:
            periodo = periodo[0]
            periodo = periodo.strip()
        else:
            periodo = ''

        self.periodo = periodo

        reCursos = re.compile("javascript:enviar_curso\('(\d+)','(\d+)','(\d+)','(\d+)','(\d+)'")
        cursos = reCursos.findall(texto)
        if not cursos:
	        return []
        return cursos

    def descargarCurso(self, curso):
        """
        Descarga el horario de un curso a traves de su pagina en el navegador.

        curso -- Los datos de un curso (recibidos desde descargarListaCursos())

        Devuelve una lista conteniendo datos del curso y el horario.
        [(id_curso,[nombre], tipo, dia, bloque, sala)]
        """
        lista = []
        if not self.conectado:
            return
        # Agrego el POST para solicitar el curso
        params = urllib.urlencode({'c_asignatura': curso[0],'ano': curso[3],
            'n_periodo': curso[1],'t_periodo': curso[2],'paralelo': curso[4]})
        request = urllib2.Request("https://nave10.ucv.cl//docencia/cursos/ficha_curso.php",params)
        self.CJ.add_cookie_header(request)
        f = urllib2.urlopen(request)
        text = f.read()
        # Buscamos el nombre del curso...
        nombre = self.reNombreCurso.findall(text)
        if nombre:
            nombre[0] = nombre[0].replace('&nbsp; ',' ')
            nombre[0] = nombre[0].replace('\t','')
            nombre = nombre[0].split('   ')
            nombre[1] = nombre[1].capitalize()
            # nombre = [sigla,nombre_completo]
        else:
            print 'Hubo un error descargando el curso:'
            print curso
            return ()
        horario = self.reHorario.findall(text)
        if horario:
            horario = horario[0]
            """
            Primero se busca el horario de ayudantia, luego de encontrarlo
            se borra para seguir analizando.
            """
            ayudantia = self.reAyudantia.findall(horario)
            if ayudantia:
                ayudantia = self.reColumnas.findall(ayudantia[0])
                i = 1
                for ayud in ayudantia:
                    if i >= 2:
                        datos = self.reFilas.findall(ayud[1])
                        bloques = self.reBloques.findall(datos[1][1])
                        bloque = bloques[0][0]
                        sala = self.reSala.findall(datos[2][1])
                        sala = sala[0][1].strip()
                        dia = datos[0][1]
                        if dia.startswith('Lu'):
                            dia = 1
                        elif dia.startswith('Ma'):
                            dia = 2
                        elif dia.startswith('Mi'):
                            dia = 3
                        elif dia.startswith('Ju'):
                            dia = 4
                        elif dia.startswith('Vi'):
                            dia = 5
                        elif dia.startswith('Sá'):
                            dia = 6
                        lista.append((curso[0], nombre, 2, dia, bloque, sala))
                    i = i + 1
                # se borran las ayudantias del horario, estan listas
                horario = re.sub(self.reAyudantia,'',horario)
            # Ahora el horario de catedra.
            catedra = self.reColumnas.findall(horario)
            i = 1
            for cat in catedra:
                if i >= 2:
                    datos = self.reFilas.findall(cat[1])
                    j = 1
                    for dato in datos:
                        if j % 3 == 1:
                            dia = dato[1]
                        if j % 3 == 2:
                            bloques = self.reBloques.findall(dato[1])
                            bloque = bloques[0][0]
                        if j % 3 == 0:
                            sala = self.reSala.findall(dato[1])
                            sala = sala[0][1].strip()
                        j = j + 1
                    try:
                        if dia.startswith('Lu'):
                            dia = 1
                        elif dia.startswith('Ma'):
                            dia = 2
                        elif dia.startswith('Mi'):
                            dia = 3
                        elif dia.startswith('Ju'):
                            dia = 4
                        elif dia.startswith('Vi'):
                            dia = 5
                        elif dia.startswith('Sá'):
                            dia = 6
                        lista.append((curso[0],nombre, 1, dia, bloque, sala))
                    except:
                        pass 

                i = i + 1
            #print 'OK.'
        return lista


    def descargarFoto(self, rut):
        request = urllib2.Request("https://webun2prod.ucv.cl:8443/imagenapp/jpgservlet?rut=" + str(rut))
        self.CJ.add_cookie_header(request)
        try:
            f = urllib2.urlopen(request)
            imagen = f.read()
            fp = open('img/' + str(rut) + '.jpg', 'wb')
            fp.write(imagen);
            fp.close()
            print str(rut) + " foto guardada."
            return True
        except NoFotoError as e:
            print "%s %s" % (str(rut),e.msg)
            return False