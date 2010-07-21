/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package navegaPucv;

/**
 *
 * @author Ignacio
 */
public interface eventoProgreso
{
    public void reportarProgreso(int progreso, String estado);
    public void error(String estado);
    public void listo(boolean canceladoConError);
    public void nuevoBloque(BloqueHorario bloque);
}
