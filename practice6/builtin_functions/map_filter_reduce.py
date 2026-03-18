from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

#map  square every number
squared = list(map(lambda x: x ** 2, numbers))
print(squared)

#filter  keep only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)

#reduce  multiply all numbers together
product = reduce(lambda a, b: a * b, numbers)
print( product)
