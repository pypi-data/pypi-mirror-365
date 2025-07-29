class color_text:
    def __init__(self) -> None:
        self.gray = '\033[90m'
        self.red = '\033[91m'
        self.green = '\033[92m'
        self.yello = '\033[93m'
        self.blue = '\033[94m'
        self.magenta = '\033[95m'
        self.sky = '\033[96m'
        self.white = '\033[97m'


        self.grayk = '\033[100m'
        self.redk = '\033[101m'
        self.greenk = '\033[102m'
        self.yellok = '\033[103m'
        self.bluek = '\033[104m'
        self.magentak = '\033[105m'
        self.skyk = '\033[106m'
        self.whitek = '\033[107m'

        self.set = '\033[0m'
    
    def iwhat_is_this(self):
        a = '''example as 
import icolor
ct = icolor.color_text()
print(ct.green,'This text is green.')
print(ct.set,'Use this for set color text to default')'''
        print(a)

def iwhat_is_this():
    a = '''example as 
import icolor
ct = icolor.color_text()
print(ct.green,'This text is green.')
print(ct.set,'Use this for set color text to default')'''
    print(a)

ct = color_text()