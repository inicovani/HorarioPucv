package horarioPucv;

import java.awt.*;
import java.awt.event.*;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URISyntaxException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.*;
import navegaPucv.*;

import java.net.URI;

public class HorarioPucv extends JPanel
                             implements ActionListener,                                        
                                        eventoProgreso
{

	/**
	 * 
	 */
	private static final long serialVersionUID = -5324580399443576563L;
	private JProgressBar barraProgreso;
    private JButton botonConectar;
    private JTextArea taskOutput;
    private JLabel lblRut;
    private JLabel lblRutDv;
    private JLabel lblContrasena;
    private JTextField rut_num;
    private JTextField rut_dv;
    private JPasswordField password;
    private JComboBox opcionHorario = new JComboBox();
    private JPanel panel;

    private JMenu menu1;
    private JMenuItem itemSalir;
    private JMenu menu2;
    private JMenuItem itemFAQ;
    private JMenuItem itemAbout;
 //   private JPopupMenu.Separator separador;
    
    private NavegaPucv task;
    private JFrame parent;

    private URI uriFAQ;
    //private tablaHorario panelHorario;
    
    public HorarioPucv(JFrame parent)
    {
        super(new BorderLayout());

        this.parent = parent;
        try
        {
            this.uriFAQ = new URI("http://wiki.github.com/inicovani/HorarioPucv/preguntas-frecuentes-acerca-de-horariopucv");
        } catch (URISyntaxException ex)
        {
            Logger.getLogger(HorarioPucv.class.getName()).log(Level.SEVERE, null, ex);
        }

        //setJMenuBar(menuBar);
        itemSalir = new JMenuItem();
        itemFAQ = new JMenuItem();
        itemAbout = new JMenuItem();

        JMenuBar menuBar = new JMenuBar();

        menu1 = new JMenu();
        menu1.setText("HorarioPucv");
        itemSalir.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_F4, java.awt.event.InputEvent.ALT_MASK));
        itemSalir.setText("Salir");
        itemSalir.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                itemSalirActionPerformed(evt);
            }
        });

        menu1.add(itemSalir);
        menuBar.add(menu1);

        menu2 = new JMenu();
        menu2.setText("Ayuda");
        itemFAQ.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_F, java.awt.event.InputEvent.ALT_MASK));
        itemFAQ.setIcon(new javax.swing.ImageIcon(getClass().getResource("/recursos/FAQ.png"))); // NOI18N
        itemFAQ.setText("Preguntas Frecuentes");
        itemFAQ.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                try
                {
                    itemFAQActionPerformed(evt);
                } catch (URISyntaxException ex) {
                    Logger.getLogger(HorarioPucv.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });
        
        menu2.add(itemFAQ);
//        separador = new JPopupMenu.Separator();
        //menu2.add(separador);
        itemAbout.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_A, java.awt.event.InputEvent.ALT_MASK));
        itemAbout.setIcon(new javax.swing.ImageIcon(getClass().getResource("/recursos/icono20.png"))); // NOI18N
        itemAbout.setText("Acerca de HorarioPucv");
        itemAbout.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {

                    itemAboutActionPerformed(evt);

            }
        });
 //       menu2.add(itemAbout);
        menuBar.add(menu2);

        parent.setJMenuBar(menuBar);
        
        botonConectar = new JButton("Conectar!");
        botonConectar.setActionCommand("start");
        botonConectar.addActionListener(this);

        barraProgreso = new JProgressBar(0, 100);
        barraProgreso.setValue(0);
        barraProgreso.setStringPainted(true);
        barraProgreso.setVisible(false);
        

        taskOutput = new JTextArea(10, 35);
        taskOutput.setMargin(new Insets(5,5,5,5));
        taskOutput.setEditable(false);
        taskOutput.setVisible(false);

        lblRut = new JLabel("Rut:");
        rut_num = new JTextField(6);
        rut_num.setHorizontalAlignment(JTextField.CENTER);
        lblRutDv = new JLabel("-");
        rut_dv = new JTextField(2);
        rut_dv.setHorizontalAlignment(JTextField.CENTER);
        lblContrasena = new JLabel("Contraseña:");
        password = new JPasswordField(10);
        password.setEchoChar('\u2022');
        password.setHorizontalAlignment(JTextField.CENTER);
        
        
        opcionHorario.insertItemAt("Horario Preinscripción", 0);
        opcionHorario.insertItemAt("Período actual", 0);
        opcionHorario.setSelectedIndex(0);
        
        JPanel panelLogin = new JPanel();
        panelLogin.setBorder(BorderFactory.createTitledBorder("Ingreso"));

        panelLogin.add(lblRut);
        panelLogin.add(rut_num);
        panelLogin.add(lblRutDv);
        panelLogin.add(rut_dv);
        panelLogin.add(lblContrasena);
        panelLogin.add(password);
        panelLogin.add(opcionHorario);
        panelLogin.add(botonConectar);
        
 
        panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.add(panelLogin);
        panel.add(barraProgreso);
        panel.add(taskOutput);
        panel.setVisible(true);
        
        //panelHorario = new tablaHorario();

        //add(panelHorario,BorderLayout.LINE_START);
        add(panel);

        setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
    }

    /**
     * Invocado cuando el usuario presiona el boton "Conectar!"
     */
    public void actionPerformed(ActionEvent evt)
    {
        botonConectar.setEnabled(false);
        panel.setVisible(true);
        taskOutput.setVisible(true);
        barraProgreso.setValue(0);
        barraProgreso.setVisible(true);
        parent.pack();
        
        taskOutput.setText(null);
        setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
        if(opcionHorario.getSelectedIndex() == 0)
        	task = new NavegaPucv(this, rut_num.getText(), rut_dv.getText(), password.getPassword(),false);
        else
        	task = new NavegaPucv(this, rut_num.getText(), rut_dv.getText(), password.getPassword(),true);
        
        task.execute();
    }

    
    /**
     * Crea la GUI y la muestra.
     */
    private static void createAndShowGUI()
    {
        //Create and set up the window.
        JFrame frame = new JFrame(String.format("HorarioPucv v%s",Config.VERSION));
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        //Create and set up the content pane.        
        JComponent newContentPane = new HorarioPucv(frame);
        newContentPane.setOpaque(true); //content panes must be opaque
        frame.setContentPane(newContentPane);

        //Display the window.
        frame.pack();
        frame.setVisible(true);
    }

    public static void main(String[] args)
    {
        //Schedule a job for the event-dispatching thread:
        //creating and showing this application's GUI.
        javax.swing.SwingUtilities.invokeLater(new Runnable()
        {
            public void run()
            {
                createAndShowGUI();
            }
        });
    }

    public void reportarProgreso(int progreso, String estado)
    {
        taskOutput.append(estado + "\n");
        barraProgreso.setValue(progreso);
    }

    /**
     * Metodo llamado a traves del thread via callback.
     * Indica que hubo un error, y que debe cancelar la ejecucion.
     * @param estado El mensaje de error enviado por el thread. Se muestra en pantalla.
     */
    public void error(String estado)
    {
        taskOutput.append(estado);
        task.cancel(true);
    }

    /**
     * Metodo llamado a traves del thread via callback, una vez que
     * este termina su ejecucion.
     * @param canceladoConError Indica si el thread termino con algun error. En
     * caso contrario, pregunta al usuario si desea revisar su horario en el explorador.
     */
    public void listo(boolean canceladoConError)
    {
        setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
        barraProgreso.setValue(0);
        barraProgreso.setVisible(false);
        botonConectar.setEnabled(true);
        password.setText(null);

        // Muestro el dialogo para abrir la pagina en el explorador
        if(canceladoConError == false)
        {
        	try
        	{
                extraerRecurso("horario.html");
                extraerRecurso("horario.css");
                extraerRecurso("fondo_td_titulo.png");
                extraerRecurso("icono20.png");
        	}
        	catch (Exception ex)
        	{
        		Logger.getLogger(HorarioPucv.class.getName()).log(Level.SEVERE, null, ex);
        	}
            if(JOptionPane.showConfirmDialog(parent, "Tu horario se ha descargado correctamente.\n¿Deseas ver el horario en tu explorador?",
                    "Información",JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION)
            {
                try
                {
                    Desktop.getDesktop().browse(new URI("horario.html"));
                }
                catch (URISyntaxException ex)
                {
                    Logger.getLogger(HorarioPucv.class.getName()).log(Level.SEVERE, null, ex);
                }
                catch (Exception ex)
                {
                    Logger.getLogger(HorarioPucv.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
            

        }
    }
    
    public void extraerRecurso(String recurso) throws Exception
    {
        try
        {
        	File efile = new File(".", recurso);

            InputStream in = this.getClass().getResourceAsStream("/recursos/" + recurso);
            OutputStream out = new BufferedOutputStream(new FileOutputStream(efile));
            byte[] buffer = new byte[2048];
            for (;;)
            {
            	int nBytes = in.read(buffer);
            	if (nBytes <= 0) break;
            	out.write(buffer, 0, nBytes);
            }
            out.flush();
            out.close();
            in.close();
        }
        catch (Exception e)
        {
        	throw e;
        }
    }

    /**
     * Metodo llamado al momento de presionar el item "Preguntas Frecuentes" del menu.
     * @param evt
     * @throws URISyntaxException
     */
    private void itemFAQActionPerformed(java.awt.event.ActionEvent evt) throws URISyntaxException
    {
        try
        {
            Desktop.getDesktop().browse(this.uriFAQ);
        } catch (IOException ex)
        {
            
        }
    }
    
    private void itemAboutActionPerformed(java.awt.event.ActionEvent evt)
    {
//    	AcercaDe ad = new AcercaDe(parent,true);
//    	ad.setVisible(true);
    }

    /**
     * Metodo llamado al momento de presionar el item "Salir" del menu.
     * @param evt
     */
    private void itemSalirActionPerformed(java.awt.event.ActionEvent evt)
    {
        System.exit(0);
    }

    public void nuevoBloque(BloqueHorario bloque)
    {
       //this.panelHorario.setBloque(bloque);
    }

}

class AcercaDe extends JDialog
{
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	public AcercaDe(Frame parent, Boolean modal)
	{
		super(parent,modal);
		setTitle(" Acerca de HorarioPucv");		
		setSize(400, 300);
		setResizable(false);
		setDefaultCloseOperation(JFrame.HIDE_ON_CLOSE);
		JPanel panel = new JPanel();

        panel.setLayout(new BoxLayout(panel, BoxLayout.X_AXIS));
        JPanel lblPanel = new JPanel();
        lblPanel.setLayout(new BoxLayout(lblPanel, BoxLayout.Y_AXIS));

        
		JLabel img = new JLabel(new ImageIcon("AboutImg.png"));
        JLabel lbl = new JLabel("HorarioPucv v"+Config.VERSION);
        lblPanel.add(Box.createRigidArea(new Dimension(0,30)));
        lblPanel.add(lbl);
        

        //img.setAlignmentX(getAlignmentX());
        panel.add(Box.createRigidArea(new Dimension(15,0)));
		panel.add(img);
		panel.add(lblPanel);
				

        add(panel);
        
	}
	
	
	
	
	
}
