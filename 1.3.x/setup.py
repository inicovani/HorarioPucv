from distutils.core import setup
import py2exe

setup(
        console=[
			{
				"script" : 'HorarioPucv_GUI.py',
				"icon_resources": [(0, "HorarioPucv.ico")]
			}],
		zipfile='bin/library.zip',
        options={
                "py2exe":{
                        "dist_dir": 'HorarioPucv',
                        "excludes": ["doctest","pdb","unittest","difflib","inspect" ],
                        "compressed": True
                         }
                },
        data_files=[ ("",["horario.html","horario.css", "fondo_td_titulo.png", "icono20.png"])]
)