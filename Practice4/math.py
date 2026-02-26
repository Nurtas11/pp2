import math

degree = float(input("Input degree: "))
radian = math.radians(degree)
print("Output radian:", round(radian, 6))

h = float(input("Height: "))
b1 = float(input("Base, first value: "))
b2 = float(input("Base, second value: "))
area = ((b1 + b2) / 2) * h
print("Area of trapezoid:", area)

n = int(input("Input number of sides: "))
s = float(input("Input the length of a side: "))
area = (n * s ** 2) / (4 * math.tan(math.pi / n))
print("The area of the polygon is:", round(area))

base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))
area = base * height
print("Expected Output:", area)