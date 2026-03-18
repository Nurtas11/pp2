with open("students.txt", "a") as f:
    f.write(" My name is Nurtas")
with open("students.txt", "r") as f:
    s = f.read()
print(s)