class kbtu:
  def __init__(self, foundation_year, current_year):
    self.foundation_year = foundation_year
    self.current_year = current_year
  def years_passed(self): 
  	print(self.current_year - self.foundation_year)

class inheritance(kbtu):
  pass

x = inheritance(2001 , 2026) 
x.years_passed()
