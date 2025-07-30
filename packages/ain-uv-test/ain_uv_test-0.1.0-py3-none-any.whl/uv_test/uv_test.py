import numpy


def numpy_add(a, b):
    """
    Adds two numbers using NumPy.
    
    Args:
        a (int or float): The first number.
        b (int or float): The second number.
    
    Returns:
        int or float: The sum of a and b.
    """
    return numpy.add(a, b)  # Using NumPy's add function


def main(): 
    """
    Main function to demonstrate the usage of numpy_add.
    """
    result = numpy_add(1, 2)
    print(result)  # Should print 3

if __name__ == "__main__":
    main()
