import numpy as np

def mgm(a: int, x0: int, m: int, count: int = 10):
    """
    Multiplicative Generative Method (MGM) to generate pseudo-random numbers.

    Parameters:
        a (int): Multiplier
        x0 (int): Initial seed value
        m (int): Modulus
        count (int): Number of random numbers to generate (default is 10)

    Returns:
        tuple: A tuple containing:
            - y (list): List of generated random numbers
            - u (numpy.ndarray): Normalized values (y/m)
    """
    y = [x0] + [0] * (count - 1)
    for i in range(count - 1):
        y[i+1] = (a * y[i]) % m
    u = np.divide(y, m)
    return y, u