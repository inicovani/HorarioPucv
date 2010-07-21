/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package navegaPucv;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.swing.SwingWorker;

/**
 *
 * @author Ignacio
 */
public class NavegaPucv extends SwingWorker<Void, Void>
{
    private String data;
    private Pattern reLogin;
    private Pattern rePeriodo;
    private Pattern reListaCursos;
    private Pattern reNombreCurso;
    private Pattern reColumnas;
    private Pattern reFilas;
    private String cookieValida;
    private String periodo;
    private eventoProgreso ep;
    private boolean descargaPreinscripcion;
    private boolean canceladoConError;
    
    public NavegaPucv(eventoProgreso ep, String rut_num, String rut_dv, char [] user_pas, boolean descargaPreinscripcion)
    {
        try
        {
            String pass = new String(user_pas);
            this.data = URLEncoder.encode("rut_num", "UTF-8") + "=" + URLEncoder.encode(rut_num, "UTF-8");
            data += "&" + URLEncoder.encode("rut_dv", "UTF-8") + "=" + URLEncoder.encode(rut_dv, "UTF-8");
            data += "&" + URLEncoder.encode("user_pas", "UTF-8") + "=" + URLEncoder.encode(pass, "UTF-8");
            data += "&" + URLEncoder.encode("rb_aplicacion", "UTF-8") + "=" + URLEncoder.encode("1", "UTF-8");
        } 
        catch (UnsupportedEncodingException ex)
        {
            Logger.getLogger(NavegaPucv.class.getName()).log(Level.SEVERE, null, ex);
        }
        this.reLogin = Pattern.compile("<META CONTENT=\\\"0;URL=https://nave10.ucv.cl//alumno/fichas/ficha_consolidada.php\\\" HTTP-EQUIV=Refresh>");
        this.rePeriodo = Pattern.compile("<strong>Período:</strong>\\s*(.+?)&nbsp;");
        this.reListaCursos = Pattern.compile("javascript:enviar_curso\\('(\\d+)','(\\d+)','(\\d+)','(\\d+)','(\\d+)'");
        this.reNombreCurso = Pattern.compile("class=\"w80\">\\s*?<strong>\\s*(.*?)&nbsp; &nbsp; &nbsp; (.*?)\\t*?</strong>");
        this.reColumnas = Pattern.compile("<tr (?:class='color'){0,1}>(.+?)</tr>");
        this.reFilas = Pattern.compile("<td>(.*?)</td>");
        this.cookieValida = "";
        this.periodo = "";
        this.ep = ep;
        this.canceladoConError = false;
        this.descargaPreinscripcion = descargaPreinscripcion;
    }

    /*
     * Main task. Executed in background thread.
     */
    @Override
    public Void doInBackground()
    {
        ep.reportarProgreso(0,"Conectando al navegador.");
        if(conectar())
        {
            ep.reportarProgreso(10,"Ingreso correcto.");
            descargarHorarioCompleto();
        }
        
        return null;
    }


    @Override
    protected void done()
    {
        ep.listo(this.canceladoConError);
    }

    private void error(String estado)
    {
        this.canceladoConError = true;
        //System.out.println(estado);
        ep.error(estado);        
    }

    /**
     * 
     * @return
     */
    public boolean conectar()
    {
        try
        {
            URL url = new URL("https://nave10.ucv.cl/inicio/signon.php");
            URLConnection conn = url.openConnection();
            conn.setDoOutput(true);
            OutputStreamWriter wr = new OutputStreamWriter(conn.getOutputStream());
            wr.write(data);
            wr.flush();

            String texto = "";
            String linea;
            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));

            while ((linea = rd.readLine()) != null)
            {
                texto += linea + '\n';
            }

            wr.close();
            rd.close();

            Matcher m = reLogin.matcher(texto);
            if(m.find())
            {
                // System.out.println("Ingreso correcto, guardando cookies.");
                String headerName=null;
                int j = 0;
                for (int i=1; (headerName = conn.getHeaderFieldKey(i))!=null; i++)
                {
                    if (headerName.equals("Set-Cookie"))
                    {
                        String cookie = conn.getHeaderField(i);
                        cookie = cookie.substring(0, cookie.indexOf(";"));

                        if(j == 0)
                            this.cookieValida += cookie;
                        else
                            this.cookieValida += String.format("; %s", cookie);
                        j++;
                    }
                }
                return true;
            }
            else
            {
                error("Usuario o contraseña incorrectos.");
                return false;
            }


        } catch (MalformedURLException ex)
        {
            Logger.getLogger(NavegaPucv.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex)
        {
            Logger.getLogger(NavegaPucv.class.getName()).log(Level.SEVERE, null, ex);
        }

        return false;
    }

    private ArrayList<String []> getListaCursos()
    {
        try
        {            
            URL url = new URL("https://nave10.ucv.cl//alumno/fichas/ficha_consolidada.php");
            URLConnection conn = url.openConnection();
            conn.setRequestProperty("Cookie", this.cookieValida);
            conn.connect();
            
            String texto = "";
            String linea;
            
            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream(),"iso-8859-1"));

            while ((linea = rd.readLine()) != null)
            {
                texto += linea + '\n';
            }

            rd.close();
            
            Matcher m = rePeriodo.matcher(texto);
            if(m.find())
            {
                periodo = m.group(1);
                //System.out.println(periodo);
            }

            m = reListaCursos.matcher(texto);

            ArrayList<String []> cursos = new ArrayList<String []>();
            while(m.find())
            {
                String curso[] = {m.group(1),m.group(2),m.group(3),m.group(4),m.group(5)};
                cursos.add(curso);
            }
            return cursos;
        }
        catch (IOException ex)
        {
            Logger.getLogger(NavegaPucv.class.getName()).log(Level.SEVERE, null, ex);
        }

        return new ArrayList<String []>();
    }
    
    private ArrayList<String []> getListaCursosPreinscripcion()
    {
        try
        {   
        	// En la preinscripcion usan los parametros de enviar_curso sin comillas simples...
        	Pattern reListaCursosPreinscripcion = Pattern.compile("javascript:enviar_curso\\((\\d+),(\\s*\\d+),(\\d+),(\\s*\\d+),(\\s*\\d+)");
            URL url = new URL("https://nave10.ucv.cl/alumno/preinscripcion/ofac_frame_consulta.php");
            URLConnection conn = url.openConnection();
            conn.setRequestProperty("Cookie", this.cookieValida);
            conn.connect();
            
            String texto = "";
            String linea;
            
            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream(),"iso-8859-1"));

            while ((linea = rd.readLine()) != null)
            {
                texto += linea + '\n';
            }

            rd.close();
            
            //System.out.println(texto);
            
            /*Matcher m = rePeriodo.matcher(texto);
            if(m.find())
            {
                periodo = m.group(1);
                //System.out.println(periodo);
            }*/
            Matcher m;

            m = reListaCursosPreinscripcion.matcher(texto);

            ArrayList<String []> cursos = new ArrayList<String []>();
            while(m.find())
            {
                String curso[] = {m.group(1),m.group(2),m.group(3),m.group(4),m.group(5)};
                cursos.add(curso);
                System.out.println("Curso encontrado con id " + curso[0]);
            }
            return cursos;
        }
        catch (IOException ex)
        {
            Logger.getLogger(NavegaPucv.class.getName()).log(Level.SEVERE, null, ex);
        }

        return new ArrayList<String []>();
    }

    private Curso descargarCurso(String c_asignatura, String n_periodo,
                    String t_periodo, String ano, String paralelo)
    {
        try
        {
            String data = URLEncoder.encode("c_asignatura", "UTF-8") + "=" + URLEncoder.encode(c_asignatura, "UTF-8");
            data += "&" + URLEncoder.encode("n_periodo", "UTF-8") + "=" + URLEncoder.encode(n_periodo, "UTF-8");
            data += "&" + URLEncoder.encode("t_periodo", "UTF-8") + "=" + URLEncoder.encode(t_periodo, "UTF-8");
            data += "&" + URLEncoder.encode("ano", "UTF-8") + "=" + URLEncoder.encode(ano, "UTF-8");
            data += "&" + URLEncoder.encode("paralelo", "UTF-8") + "=" + URLEncoder.encode(paralelo, "UTF-8");
            Curso curso = null;
            URL url = new URL("https://nave10.ucv.cl//docencia/cursos/ficha_curso.php");
            URLConnection conn = url.openConnection();
            conn.setRequestProperty("Cookie", this.cookieValida);            
            conn.setDoOutput(true);
            OutputStreamWriter wr = new OutputStreamWriter(conn.getOutputStream());
            wr.write(data);
            wr.flush();
            conn.connect();

            String texto = "";
            String linea;
            String siglaCurso = "";
            String nombreCurso = "";

            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream(),"iso-8859-1"));

            while ((linea = rd.readLine()) != null)
            {
                texto += linea + '\n';
            }

            wr.close();
            rd.close();

            Matcher m = reNombreCurso.matcher(texto);
            if(m.find())
            {
                siglaCurso = m.group(1);
                nombreCurso = m.group(2).toLowerCase();
            }

            curso = new Curso(siglaCurso,nombreCurso);
            Pattern reHorario = Pattern.compile("<form name=sala action=horario-sala.php method=post>(.+)");
            m = reHorario.matcher(texto);
            if(m.find())
            {
                String texto2 = m.group(0);
                int errores = 0;
                Pattern reAyudantia = Pattern.compile("Ay. Cátedra</td>(.+)");
                Pattern reBloques = Pattern.compile("(\\d+)(?:.+?) - (\\d+)");
                Pattern reSala = Pattern.compile("<a(?:.+?)>(.+?)\\s*</a>");
                Matcher m2 = reAyudantia.matcher(texto2);
                if(m2.find())
                {
                    String texto3 = m2.group(0);
                    Matcher m3 = reColumnas.matcher(texto3);
                    while(m3.find())
                    {
                        BloqueHorario datoHorario = new BloqueHorario(Config.TipoBloque.AYUDANTIA);
                        datoHorario.setSigla(siglaCurso);
                        datoHorario.setNombreCompleto(nombreCurso);
                        errores = 0;
                        Matcher m4 = reFilas.matcher(m3.group(0));
                        int indice = 0;
                        while(m4.find())
                        {
                            if(indice == 0)
                            {
                                if(!datoHorario.setDia(m4.group(1)))
                                    errores++;
                            }
                            else if(indice == 1)
                            {
                                Matcher m5 = reBloques.matcher(m4.group(1));
                                if(m5.find())
                                    datoHorario.setBloque(m5.group(1));
                                else
                                    errores++;
                            }
                            else if(indice == 2)
                            {
                                Matcher m5 = reSala.matcher(m4.group(1));
                                if(m5.find())
                                    datoHorario.setSala(m5.group(1));
                                else
                                    errores++;
                            }
                            indice++;                            
                        }
                        curso.agregarHorario(datoHorario);
                        ep.nuevoBloque(datoHorario);
                    }
                    texto = m2.replaceFirst("");
                }
                Matcher m3 = reColumnas.matcher(texto);
                while(m3.find())
                {
                    BloqueHorario datoHorario = new BloqueHorario(Config.TipoBloque.CATEDRA);
                    datoHorario.setSigla(siglaCurso);
                    datoHorario.setNombreCompleto(nombreCurso);
                    errores = 0;
                    Matcher m4 = reFilas.matcher(m3.group(0));
                    int indice = 0;
                    while(m4.find())
                    {
                        if(indice == 0)
                        {
                            if(!datoHorario.setDia(m4.group(1)))
                                errores++;
                        }
                        else if(indice == 1)
                        {
                            Matcher m5 = reBloques.matcher(m4.group(1));
                            if(m5.find())
                                datoHorario.setBloque(m5.group(1));
                            else
                                errores++;
                        }
                        else if(indice == 2)
                        {
                            Matcher m5 = reSala.matcher(m4.group(1));
                            if(m5.find())
                                datoHorario.setSala(m5.group(1));
                            else
                                errores++;
                        }
                        indice++;                       
                   }
                   
                   curso.agregarHorario(datoHorario);
                   ep.nuevoBloque(datoHorario);
                }
                if(errores > 0)
                {
                    // TODO: HUBO ERRORES
                    return null;
                }                
            }
            
            return curso;
        }
        catch (MalformedURLException ex)
        {
            Logger.getLogger(NavegaPucv.class.getName()).log(Level.SEVERE, null, ex);
        }
        catch (UnsupportedEncodingException ex)
        {
            Logger.getLogger(NavegaPucv.class.getName()).log(Level.SEVERE, null, ex);
        }
        catch (IOException ex)
        {
            Logger.getLogger(NavegaPucv.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }

    @SuppressWarnings("unchecked")
	private void descargarHorarioCompleto()
    {
    	String strInscritos;
    	
        if(this.descargaPreinscripcion)
        	strInscritos = "preinscritos";
        else
        	strInscritos = "inscritos";
        
        ep.reportarProgreso(15, "Descargando lista de ramos "+strInscritos+".");
        
        ArrayList<String[]> cursos;
        
        if(this.descargaPreinscripcion)
        	cursos = this.getListaCursosPreinscripcion();
        else
        	cursos = this.getListaCursos();
        
        Hashtable htHorarios = new Hashtable();
        int numeroCursos = cursos.size();
        String buf = "";
        int progreso = 20;
        int avancePorCurso = 60 / numeroCursos;

        ep.reportarProgreso(progreso, String.format("Hay %d ramos %s.", numeroCursos, strInscritos));

        for(String[] preCurso : cursos)
        {
            Curso curso = this.descargarCurso(preCurso[0], preCurso[1], preCurso[2], preCurso[3], preCurso[4]);
            // System.out.println(curso.getNombre());
            progreso += avancePorCurso;

            if(curso == null)
                return;

            ep.reportarProgreso(progreso, String.format("Horario encontrado para %s %s.",curso.getSigla(),curso.getNombre()));
            for(BloqueHorario bh: curso.getListaHorarios())
            {
                String keyId = String.format("%d-%s", bh.getDia(),bh.getBloque());
                if(htHorarios.containsKey(keyId))
                {
                    ((ArrayList<BloqueHorario>) htHorarios.get(keyId)).add(bh);
                }
                else
                {
                    htHorarios.put(keyId, new ArrayList<BloqueHorario>());
                    ((ArrayList<BloqueHorario>) htHorarios.get(keyId)).add(bh);
                }
                
            }

            buf += curso.getJSCurso();
        }
        try
        {
            ep.reportarProgreso(90, "Generando archivo javascript.");
            OutputStreamWriter out = new OutputStreamWriter(new FileOutputStream("horario.js"),"iso-8859-1");

            out.write("var version = '"+Config.VERSION+"';\n");
            out.write("var periodo = '"+this.periodo+"';\n");
            out.write("\n");
            out.write("var clases = new Array();\n");
            out.write("var topes = new Array();\n");
            out.write("var ramos = new Array();\n");
            out.write("\n");
            out.write(buf+"\n");

            for(Object horario : htHorarios.values())
            {
                if(((ArrayList<BloqueHorario>) horario).size() > 1)
                {
                    out.write("var tope = new Array();\n");
                    for(BloqueHorario bh : (ArrayList<BloqueHorario>) horario)
                    {
                        out.write(String.format("var clase = new Array(0,'%s','%s',%d,%d,%s,'%s');\n",
                                bh.getSigla(),bh.getNombreCompleto(),
                                bh.getTipoHorario().ordinal(),bh.getDia(),
                                bh.getBloque(), bh.getSala()));
                        out.write("tope.push(clase);\n");
                        out.write("\n");
                    }
                    out.write("topes.push(tope);\n");
                    out.write("\n");
                }
                else
                {
                    BloqueHorario bh = ((ArrayList<BloqueHorario>) horario).get(0);
                    out.write(String.format("var clase = new Array(0,'%s','%s',%d,%d,%s,'%s');\n",
                                bh.getSigla(),bh.getNombreCompleto(),
                                bh.getTipoHorario().ordinal(),bh.getDia(),
                                bh.getBloque(), bh.getSala()));
                    out.write("clases.push(clase);\n");
                    out.write("\n");
                }
            }
            out.close();
            ep.reportarProgreso(100, "Listo.");
        }
        catch(IOException e)
        {
            System.out.println(e.toString());
        }
        

    }
}
