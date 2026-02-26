n = int(input())

def squaree(n):
    for i in range(n+1): 
        yield i ** 2

for s in squaree(n):
    print(s)
print()

def even_numbers(n):
    for i in range(0, n+1, 2):
        yield i
print(",".join(map(str, even_numbers(n))))

print()

def divisible(n):
    for i in range(n+1):
        if i % 3 == 0 and i % 4 == 0:
            yield i
for num in divisible(n):
    print(num)

print()

def squares(a, b):
    for i in range(a, b+1):
        yield i ** 2

for s in squares(2, 5):
    print(s)

print()

def countdown(n):
    while n >= 0:
        yield n
        n -= 1
for num in countdown(n):
    print(num)