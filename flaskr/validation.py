
def non_zero_positive_float(value):
    if float(value) <= 0:
        raise ValueError("The parameter must be non zero positive value")

    return float(value)

def positive_int(value):
    if int(value) <= 0:
        raise ValueError("The parameter must be a positive integer")

    return int(value)
