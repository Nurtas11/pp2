class nurtas:
  mystatus = "student" # class property is shared by everything

  def __init__(self, course):
    self.course = course # instance property is shared only with this object

p1 = nurtas("first")


print(p1.course)
print(p1.mystatus)