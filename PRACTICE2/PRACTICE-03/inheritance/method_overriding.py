class me:
    def plans(self):
        print("i will go to uni today")
class lazy_me(me):
    def plans(self) :
        print("nah, i won't go to uni")
action = lazy_me()
action.plans()