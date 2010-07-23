/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package navegaPucv;

import java.util.ArrayList;

/**
 *
 * @author Ignacio
 */
public class Curso
{
    private String sigla;
    private String nombre;
    private ArrayList<BloqueHorario> listaHorarios;

    public Curso(String sigla, String nombre)
    {
        this.sigla = Config.capitalizeFirstLetters(sigla);
        this.nombre = Config.capitalizeFirstLetters(nombre);
        this.listaHorarios = new ArrayList<BloqueHorario>();
    }

    public void agregarHorario(BloqueHorario horario)
    {
        listaHorarios.add(horario);
    }

    public ArrayList<BloqueHorario> getListaHorarios()
    {
        return this.listaHorarios;
    }
    
    public String getSigla()
    {
        return this.sigla;
    }

    public String getNombre()
    {
        return this.nombre;
    }

    public String getJSCurso()
    {
        return String.format("var ramo = new Array('%s','%s');\nramos.push(ramo);\n",this.getSigla(),this.getNombre());
    }
}
