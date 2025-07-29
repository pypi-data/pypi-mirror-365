import math

# Basic
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return a / b if b != 0 else "Error: Divide by 0"

# Algebra
def quadratic_roots(a, b, c):
    d = b**2 - 4*a*c
    if d > 0:
        root1 = (-b + math.sqrt(d)) / (2*a)
        root2 = (-b - math.sqrt(d)) / (2*a)
        return root1, root2
    elif d == 0:
        return -b / (2*a)
    else:
        return "Complex Roots"

def lcm(x, y): return abs(x*y) // math.gcd(x, y)
def hcf(x, y): return math.gcd(x, y)

# Geometry
def area_circle(r): return math.pi * r * r
def perimeter_circle(r): return 2 * math.pi * r

def area_triangle(base, height): return 0.5 * base * height
def area_square(side): return side * side
def area_rectangle(l, b): return l * b

# Trigonometry
def sin_deg(deg): return math.sin(math.radians(deg))
def cos_deg(deg): return math.cos(math.radians(deg))
def tan_deg(deg): return math.tan(math.radians(deg))

# Exponent & Log
def power(x, y): return math.pow(x, y)
def log10(x): return math.log10(x)
def ln(x): return math.log(x)

# Derivative Approx (f(x+h) - f(x)) / h
def derivative(f, x, h=1e-5):
    return (f(x + h) - f(x)) / h
