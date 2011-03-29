/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package horarioPucv;

//import navegaPucv.BloqueHorario;
import java.awt.*;
//import java.awt.event.*;
import javax.swing.*;

/**
 *
 * @author Ignacio
 */
public class tablaHorario extends JPanel
{
    /**
	 * 
	 */
	private static final long serialVersionUID = -4081998729437678601L;
	final static String [] diasSemana = {"","Lu", "Ma", "Mi","Ju","Vi"};
    final static String [] bloques = {"","  1-2 ", "  3-4 ", "  5-6 ","  7-8 "," 9-10","11-12","13-14"};
    int [][] datosBloque;
    public tablaHorario()
    {
        super();
        setOpaque(false);
        setLayout(new BorderLayout());
        //setBorder(BorderFactory.createLineBorder(Color.gray));
        datosBloque = new int[7][5];
        for(int i = 0;i<7;i++)
            for(int j = 0;j<5;j++)
                datosBloque[i][j] = 0;
    }
    
    @Override
    public Dimension getPreferredSize()
    {
        Dimension layoutSize = super.getPreferredSize();
        int max = Math.max(layoutSize.width,layoutSize.height);
        return new Dimension(max+280,max+280);
    }

    @Override
    protected void paintComponent(Graphics g)
    {
        Dimension size = getSize();
        int x = 0;
        int y = 5;
        int i = 0;
        int j = 0;
        int alturaPorBloque = (size.height - 40) / 8;
        int anchoPorBloque = (size.width - 20) / 6;

        for(i = 0; i < 8; i++)
        {
            x = 0;
            for(j=0; j<6; j++)
            {
                if(i == 0 && j == 0)
                {
                    x += anchoPorBloque + 3;
                    continue;
                }

                if(i != 0 && j != 0)
                {
                    if(datosBloque[i-1][j-1] == 0)
                    {
                        g.setColor(Color.white);
                        g.fillRect(x, y, anchoPorBloque, alturaPorBloque);
                    }
                    else if(datosBloque[i-1][j-1] == 1)
                    {
                        g.setColor(Color.orange);
                        g.fillRect(x, y, anchoPorBloque, alturaPorBloque);
                    }
                    else if(datosBloque[i-1][j-1] == 2)
                    {
                        g.setColor(Color.green);
                        g.fillRect(x, y, anchoPorBloque, alturaPorBloque);
                    }
                    else if(datosBloque[i-1][j-1] == 3)
                    {
                        g.setColor(Color.red);
                        g.fillRect(x, y, anchoPorBloque, alturaPorBloque);
                    }
                }
                else
                {
                    g.setColor(Color.blue);
                    g.fillRect(x, y, anchoPorBloque, alturaPorBloque);
                }

                // El borde de cada rectangulo
                g.setColor(Color.black);
                g.drawRect(x, y, anchoPorBloque, alturaPorBloque);

                g.setColor(Color.white);
               
                if(i == 0)
                    g.drawString(diasSemana[j], x+13, y+19);
                else if(j == 0)
                    g.drawString(bloques[i], x+3, y+20);
                x += anchoPorBloque + 3;
            }

            y += alturaPorBloque + 3;
        }

    }

    public void setBloque(int dia, int bloque, int tipo)
    {
        datosBloque[bloque][dia-1] = tipo;
            
        this.updateUI();
    }
}
