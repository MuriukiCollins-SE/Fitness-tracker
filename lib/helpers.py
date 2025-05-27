from tabulate import tabulate

def validate_positive_int(value, field_name):
    try:
        val = int(value)
        if val <= 0:
            raise ValueError(f"{field_name} must be positive")
        return val
    except ValueError:
        raise ValueError(f"Invalid {field_name}: must be a positive integer")

def validate_float(value, field_name):
    try:
        val = float(value)
        if val < 0:
            raise ValueError(f"{field_name} cannot be negative")
        return val
    except ValueError:
        raise ValueError(f"Invalid {field_name}: must be a number")

def print_table(data, headers):
    print(tabulate(data, headers=headers, tablefmt="grid"))