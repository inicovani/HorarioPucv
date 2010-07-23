/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package navegaPucv;

/**
 *
 * @author Ignacio
 */
public class BloqueHorario
{
        private String sigla;
        private String nombreCompleto;
        private String sala;
        private int dia;
        private String strDia;
        private String bloque;
        private Config.TipoBloque tipoHorario;

        public BloqueHorario(Config.TipoBloque tipo)
        {
            this.tipoHorario = tipo;
        }

        public void setSigla(String sigla)
        {
            this.sigla = sigla;
            return;
        }
        
        public String getSigla()
        {
            return this.sigla;
        }

        public void setNombreCompleto(String nombre)
        {
            this.nombreCompleto = Config.capitalizeFirstLetters(nombre);
            return;
        }

        public String getNombreCompleto()
        {
            return this.nombreCompleto;
        }

        public void setBloque(String bloque)
        {
            this.bloque = bloque;
            return;
        }

        public String getBloque()
        {
            return this.bloque;
        }

        public int getIndiceBloque()
        {
            if(this.bloque.equals("1")) return 0;
            else if(this.bloque.equals("3")) return 1;
            else if(this.bloque.equals("5")) return 2;
            else if(this.bloque.equals("7")) return 3;
            else if(this.bloque.equals("9")) return 4;
            else if(this.bloque.equals("11")) return 5;
            else return 6;
        }

        public void setTipoHorario(Config.TipoBloque tipo)
        {
            this.tipoHorario = tipo;
            return;
        }

        public Config.TipoBloque getTipoHorario()
        {
            return this.tipoHorario;
        }

        public int getDia()
        {
            return this.dia;
        }
        
        public String getStrDia()
        {
        	return this.strDia;
        }

        public void setSala(String sala)
        {
            this.sala = sala;
            return;
        }

        public String getSala()
        {
            return this.sala;
        }

        public boolean setDia(String dia)
        {
            if (dia.startsWith("Lu"))
                this.dia = 1;
            else if (dia.startsWith("Ma"))
                this.dia = 2;
            else if (dia.startsWith("Mi"))
                this.dia = 3;
            else if (dia.startsWith("Ju"))
                this.dia = 4;
            else if (dia.startsWith("Vi"))
                this.dia = 5;
            else
                return false;

            this.strDia = dia;
            
            return true;
        }
}
