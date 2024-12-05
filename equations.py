"""Classes for parsing and evaluating mathematical equations from
strings.
Designed and coded by Matthew Tien Wells, 2024.
"""

# Legal calculation operations in the order they should be applied.
allowedOperations = ["^","*","/","+","-"]


class operation:
    """Class representing a single mathematical operation that takes
    two inputs and produces one output. By default only supports the 
    operators in allowedOperations, but any class inheriting from this
    may override the extendCalculate method to allow additional
    operations.
    """
    def __init__(self, symbol:str, allowed=allowedOperations):
        if symbol not in allowed:
            raise ValueError(
                symbol + " is not a supported mathematical operator."
            )
        self.symbol = symbol

    def __str__(self):
        return self.symbol
    
    def calculate(self, left:float|int, right:float|int):
        """Calculate the result of applying this operation to variable
        left with variable right as input.
        """
        if self.symbol == "+":
            return left+right
        elif self.symbol == "-":
            return left-right
        elif self.symbol == "/":
            return left/right
        elif self.symbol == "*":
            return left*right
        elif self.symbol == "^":
            return left**right
        else:
            return self.extendCalculate(left, right)

    def extendCalculate(self, left:float|int, right:float|int):
        """Provides additional operations to calculate. By default this
        does nothing, and is included for convenience in building child
        classes. Any new operators passed in via overriding
        allowedOperations should have their calculations defined here.
        """
        pass

class equation:
    """A mathematical equation using the operations defined in
    allowedOperations. Additional operations can be added by passing in
    a child class of operation as 'operator' and custom list of
    allowedOperations as 'allowed'.
    """
    def __init__(
        self, symbolStr=None, allowed=allowedOperations, operator=operation
        ):
        self.allowed = allowed
        self.order = [operator(op) for op in allowed]
        self.symbols = []
        if symbolStr != None:
            self.parse(symbolStr)

    def __str__(self):
        return "(" + "".join(str(symbol) for symbol in self.symbols) + ")"
    
    def __append__(self, symbol):
        self.symbols.append(symbol)

    def parse(self, symbolStr: str):
        """Read a string into an equation, replacing the existing
        equation if one exists.
        """
        self.symbols = []
        number = None
        subequation = 0
        subequationString = ""
        for char in symbolStr:
            # If reading from open parentheses, read until the
            # parentheses are balanced and treat the read text as its
            # own equation, parsing it recursively.
            if subequation > 0:
                if char == "(":
                    subequation += 1
                elif char == ")":
                    subequation -= 1
                if subequation > 0:
                    subequationString += char
                else:
                    self.__append__(
                        equation(allowed=self.allowed).parse(subequationString)
                    )
                    subequationString = ""
                continue
            # handle minus signs after other operators as part of a
            # negative number
            if char == "-" and number == None:
                number = "-"
                continue
            # If the character is not part of a number, parse any digits
            # we've just read as a number and append it to the symbols.
            # If it is part of a number, record it as part of a string.
            if char not in "0123456789.":
                if number != None:
                    if '.' in number:
                        self.__append__(float(number))
                    else:
                        self.__append__(int(number))
                number = None
            elif number == None:
                number = char
            else:
                number = number+char
            # Record operators as instances of the operator class.
            if char in self.allowed:
                self.__append__(operation(char))
                continue
            if char not in "0123456789.":
                # If the character is an open parenthesis, begin reading
                # as a subequation.
                if char == "(":
                    subequation = 1
                    continue
                elif char == ")":
                    raise ValueError(
                        "Close parenthesis must come after an open parenthesis"
                    )
                # Ignore spaces
                elif char == " ":
                    continue
                # Treat any still unhandled characters as a variable
                # name.
                else:
                    self.__append__(variable(char))
        if number != None:
            if '.' in number:
                self.__append__(float(number))
            else:
                self.__append__(int(number))

    
    def calculate(self, **kwargs):
        """Calculate the value of the equation given a float or integer
        value for each variable in symbols. Calls itself recursively if
        any symbols in the equation are subequations. Obeys the order
        of operations in self.order.
        """
        notOperator = False
        values = []
        operations = []
        #Seperate values from operators
        for symbol in self.symbols:
            if type(symbol) == equation:
                values.append(symbol.calculate(kwargs=kwargs))
            elif type(symbol) in [int, float]:
                values.append(symbol)
            elif type(symbol) == variable:
                values.append(kwargs[symbol.symbol])
            
            if notOperator and type(symbol) != operation:
                operations.append(operation("*"))
            
            if type(symbol) == operation:
                operations.append(symbol)
                notOperator = False
            else:
                notOperator = True
        if len(values) != len(operations)+1:
            print(values)
            print([str(op) for op in operations])
            raise ValueError("Equations must end with a number or variable.")
        #Iterate through operators in the order of self.order,
        #collapsing values together for each operation.
        for operatorType in self.order:
            opIndex = 0
            finishedOps = []
            for op in operations:
                if op.symbol == operatorType.symbol:
                    values = values[:opIndex] + [
                        op.calculate(values[opIndex],values[opIndex+1])
                    ] + values[opIndex+2:]
                    finishedOps.append(op)
                else:
                    opIndex += 1
                
            for op in finishedOps:
                operations.remove(op)
        return values[0]

class variable:
    """Class meant for distinguishing mathematical variables from string
    characters. Provides no particular logic, used only for checking
    types.
    """
    def __init__(self, symbol:str):
        self.symbol = symbol

    def __str__(self):
        return self.symbol