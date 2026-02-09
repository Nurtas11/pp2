def who_is_last(*imena):    #allows accepting any number of arguments
  print(imena[-1])

who_is_last("duh", "someone", "nurtas", "kairat") 

def my_function(**q): #using ** allows using dictionary of arguments
  print("he is a " + q["uni"] + " "+  q["status"])

my_function(uni = "kbtu" , status = "student ")