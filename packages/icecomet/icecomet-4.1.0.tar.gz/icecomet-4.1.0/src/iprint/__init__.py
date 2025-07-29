def iwhat_is_this():
    print("ยังไม่ได้เขียน")

# modul cprint :--> class color_text : ct.  cprint(string)
#############################################################################################

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


ct = color_text()


# modul II :--> debug :ij  ji  show_color()
#############################################################################################


ij_tag_setting = dict()



def ij(*arg,m='default',c='default',end='default',sep='default',tag=''):
    mode = m
    global ij_tag_setting
    
    # ถ้า tag ที่ใช้ เป็น tag ใหม่ จะตั้งค่าเริ่มต้นตามนี้
    if tag not in list(ij_tag_setting.keys()):
        if m == 'default':
            m = 'v'
        if c == 'default':
            c = ct.green 
        if end == 'default':
            end = '\n' 
        if sep == 'default':
            sep = ' | '
              
        ij_tag_setting[tag]={
                            'mode':m,
                            'tag':tag,
                            'color'  :c,
                            'number_of_run_passed':0,
                            'end':end,
                            'sep':sep}
    # ถ้ามีแท็กนั้นอยู่ก่อนแล้ว จะเช็คว่ามีการตั้งค่าตัวไหนที่เปลี่ยนไปมั้ย ถ้าเปลี่ยนก็จะเปลี่ยน
    else:
        if m != 'default':
            ij_tag_setting[tag]['mode'] = m
        if c != 'default':
            ij_tag_setting[tag]['color'] = c
        if end != 'default':
            ij_tag_setting[tag]['end'] = end
        if sep != 'default':
            ij_tag_setting[tag]['sep'] = sep

        
    ij_tag_setting[tag]['number_of_run_passed']+=1
    # mode description
    #   v = value
    #   l = len
    #   t = type
    #   c = number of run passed

    output = ''
    for i in ij_tag_setting[tag]['mode']:
        if i == 'v' or i == 'i':
            output += ij_tag_setting[tag]['sep'].join([str(i) for i in arg])+ij_tag_setting[tag]['end']
        if i == 'l':
            a = []
            for i in range(len(arg)):
                try:
                    a.append(f'len({arg[i]}) = {len(arg[i])}')
                except:
                    a.append(f'{arg[i]} = xx')
            output += ij_tag_setting[tag]['sep'].join(a)+ij_tag_setting[tag]['end']

        if i == 't':
            output += ij_tag_setting[tag]['sep'].join([f'{arg[i]} : {type(arg[i])}' for i in range(len(arg))])+ij_tag_setting[tag]['end']
        if i == 'c':
            a = ij_tag_setting[tag]['tag']
            b = ij_tag_setting[tag]['number_of_run_passed']
            output += f'tag "{a}" Round : {b}'+ij_tag_setting[tag]['end']
        
    print(f"{ij_tag_setting[tag]['color']}{output}{ct.set}",end='')

