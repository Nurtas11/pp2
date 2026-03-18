import os
from pathlib import Path
# create directories and files
os.makedirs("kbtu/classes", exist_ok=True)

with open("kbtu/classes/calc.txt", "w") as f:
    f.write("algebra notes")

with open("kbtu/classes/discretemath.pdf", "w") as f:
    f.write("discrete math notes")

# 2list everything
folder = Path("kbtu")
for item in folder.rglob("*"):
    print(item)

#3find by extension
for f in folder.rglob("*.txt"):
    print(f.name)
