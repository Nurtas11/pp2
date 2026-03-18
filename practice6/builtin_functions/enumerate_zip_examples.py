students = ["Nurtas", "Someone", "student3"]
scores = [85, 92, 78]

# enumerate: loop with index
for i, name in enumerate(students, start=1):
    print(i, name)

#zip  pair students with scores

for name, score in zip(students, scores):
    print(name, score)

# type checking
values = [42, "hello", 3.14, True, [1, 2, 3]]
for v in values:
    print(v, type(v))

# type conversions
print(int("42"))
print(float("3.14"))
print(str(100))
print(list("hello"))
print(bool(0), bool(1))
