class nurtas:
  def __init__(self, grade):
    self.grade = grade

  def evaluate(self):
    if self.grade == 1:
        print("GREAT!!!")
    else:
        print(":(")

p1 = nurtas(1)
p1.evaluate()