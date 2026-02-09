class student:
    def study(self):
        print("have to do my calc and pp2")

class gamer:
    def play(self):
        print("will play games for 5 hours straight")
class lazy_me(student, gamer):  #inherits from both gamer and student
    def plans(self):
        print("too many things to do")

action = lazy_me()
action.study()
action.play()
action.plans()