
import shutil
import os

# creates a backup folder if it doesn't exist
os.makedirs("backup", exist_ok=True)

shutil.copy("students.txt", "backup/students.txt") #reads from students.txt and writes to backup/students.txt


if os.path.exists("students.txt"): #deletes file if it exists 
    os.remove("students.txt")
else:
    print("nothing to delete")
