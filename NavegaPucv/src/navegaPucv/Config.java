/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package navegaPucv;

/**
 *
 * @author Ignacio
 */
public class Config
{
    public enum TipoBloque { NINGUNO, CATEDRA, AYUDANTIA }
    public static String VERSION = "1.4.2b";

    public static String capitalizeFirstLetters ( String s )
    {
        for (int i = 0; i < s.length(); i++)
        {

            if (i == 0)
            {
                // Capitalize the first letter of the string.
                s = String.format( "%s%s",
                             Character.toUpperCase(s.charAt(0)),
                             s.substring(1) );
            }

            // Is this character a non-letter or non-digit?  If so
            // then this is probably a word boundary so let's capitalize
            // the next character in the sequence.
            if (!Character.isLetterOrDigit(s.charAt(i)))
            {
                if (i + 1 < s.length())
                {
                    s = String.format( "%s%s%s",
                                 s.subSequence(0, i+1),
                                 Character.toUpperCase(s.charAt(i + 1)),
                                 s.substring(i+2) );
                }
            }

        }

        return s;
    }
}
