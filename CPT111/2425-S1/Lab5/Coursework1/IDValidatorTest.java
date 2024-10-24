import org.junit.Test;
import static org.junit.Assert.*;

public class IDValidatorTest {
    
    @Test
    public void testValidIDs() {
        assertTrue(IDValidator.isValidID("A001-606X-17X"));
        assertTrue(IDValidator.isValidID("B123-456-789X"));
        assertTrue(IDValidator.isValidID("TEST123450"));
    }
    
    @Test
    public void testInvalidIDs() {
        assertFalse(IDValidator.isValidID("THMBB7092WD114221"));
        assertFalse(IDValidator.isValidID("A001-606X-170")); // Wrong check digit
        assertFalse(IDValidator.isValidID("TEST")); // Too short
        assertFalse(IDValidator.isValidID(null)); // Null input
    }
    
    @Test
    public void testEdgeCases() {
        assertTrue(IDValidator.isValidID("12340")); // Minimum length
        assertTrue(IDValidator.isValidID("abcd-0")); // Only one digit
        assertTrue(IDValidator.isValidID("NO-DIGITS-X")); // No digits before check character
    }
}