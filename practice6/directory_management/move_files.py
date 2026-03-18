import os
from pathlib import Path
import shutil
os.makedirs("kbtu/backup", exist_ok=True)

shutil.copy("kbtu/classes/calc.txt", "kbtu/backup/calc.txt")
#copy calc.txt and move it to backup folder

shutil.move("kbtu/classes/discretemath.pdf", "kbtu/backup/discretemath.pdf")
#move discretemath.pdf to backup folder and delete the initial file