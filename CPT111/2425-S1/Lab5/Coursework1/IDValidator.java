// IDValidator.java
public class IDValidator {
    public static void main(String[] args) {
        // Example usage
        String id = "12345";
        System.out.println("Is the ID valid? " + isValidID(id));
    }

    public static boolean isValidID(String id) {
        // Check minimum length requirement
        if (id == null || id.length() < 5) {
            return false;
        }
        
        // Calculate sum of digits
        int sum = 0;
        for (int i = 0; i < id.length() - 1; i++) {
            char c = id.charAt(i);
            if (Character.isDigit(c)) {
                sum += Character.getNumericValue(c);
            }
        }
        
        // Get the expected check digit
        char expectedCheck = getCheckDigit(sum);
        
        // Compare with actual check digit
        return id.charAt(id.length() - 1) == expectedCheck;
    }
    
    private static char getCheckDigit(int sum) {
        int remainder = sum % 11;
        return remainder == 10 ? 'X' : Character.forDigit(remainder, 10);
    }
}
