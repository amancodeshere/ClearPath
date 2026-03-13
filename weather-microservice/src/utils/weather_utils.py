from decimal import Decimal


def decimal_converter(x):
    if isinstance(x, Decimal):
        return float(x)
