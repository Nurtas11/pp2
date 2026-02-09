class me:
    def __init__(self, date, mystatus):
        self.date = date
        self.mystatus = mystatus


class inheritance(me):
    def __init__(self, date, mystatus, name):
        super().__init__(date, mystatus)
        self.name = name

x = inheritance(2007, "student", "nurtas") 
print(x.date)
print(x.mystatus)
print(x.name)
