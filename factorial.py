def factorial(n):
    """
    Calculates the factorial of a given number.
    If the number is negative, returns None.
    """
    if n < 0:
        return None
    else:
        i = 1
        F = 1
        while True:
            if not i < n:
                break
            else:
                i = i + 1
                F = i * F
        return F