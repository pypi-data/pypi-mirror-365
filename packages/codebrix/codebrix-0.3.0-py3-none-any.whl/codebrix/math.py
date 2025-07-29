class basic:
    def add(num1, num2) :
        return num1 + num2

    def min(num1, num2) :
        return num1 - num2

    def mul(num1, num2) :
        return num1 * num2

    def div(num1, num2) :
        try:
            return num1 / num2
    
        except ZeroDivisionError:
            return "Error(01-1): Cannot divide by zero"
        
class advanced:
    def pot(num1, num2) :
        return num1 ** num2
    
    def perc(pv, bv) :
        try:
            return bv / 100 * pv
    
        except ZeroDivisionError:
            return "Error(01-1): Cannot divide by zero"
        
    def sqrt(num) :
        try:
            return num ** 0.5
        
        except ValueError:
            print("Error(01-2) Cannot compute square root of a negative number")