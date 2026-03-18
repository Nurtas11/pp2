with open("students.txt", "w") as f:
    f.write("LAB work")
with open("students.txt", "r") as f:
    content = f.read()
print(content)