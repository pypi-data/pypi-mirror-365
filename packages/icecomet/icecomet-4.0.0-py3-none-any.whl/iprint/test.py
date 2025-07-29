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
    global ij_tag_setting
    # mode description
    #   v,i = value
    #   l = len
    #   t = type
    #   c,r = number of run passed

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


    round_passed = f"Tag {0} runned round {1}".format(ij_tag_setting[tag]['number_of_run_passed'],ij_tag_setting[tag]['tag'])
    output = ''+ij_tag_setting[tag]['color']
    if 'r' in ij_tag_setting[tag]['mode'] or 'c' in ij_tag_setting[tag]['mode']:
        output+=round_passed+ij_tag_setting[tag]['end']

    value_of_each_arg = []
    for i in arg:
        if len(str(i))<=30:
            value_of_each_arg.append(str(i))
        else:
            a = str(i)[:16]
            b = str(i)[-11:]
            value_of_each_arg.append(f'{a}...{b}')

    type_of_each_arg = [str(type(i)).split("'")[1] for i in arg]

    len_of_each_arg = []
    for i in arg:
        try:
            len_of_each_arg.append(str(len(i)))
        except:
            len_of_each_arg.append('xx')

    # หาความยาวข้อความสำหรับแต่ละอากิวเมนต์ โดยอิงจากว่าเลือกให้แสดงอะไรบ้าง
    if not (str(ij_tag_setting[tag]['mode']).find('i') > -1 or str(ij_tag_setting[tag]['mode']).find('v') > -1) : value_of_each_arg = ['' for _ in range(len(arg))]
    if str(ij_tag_setting[tag]['mode']).find('t') == -1 : type_of_each_arg = ['' for _ in range(len(arg))]
    if str(ij_tag_setting[tag]['mode']).find('l') == -1 : len_of_each_arg = ['' for _ in range(len(arg))]
    length_of_each_arg = []

    for i in zip(value_of_each_arg,type_of_each_arg,len_of_each_arg):
        length_of_each_arg.append(max([len(v) for v in i]))
    
    for i in ij_tag_setting[tag]['mode']:
        
        if i == 'v' or i == 'i':
            a = []
            for value,length in zip(value_of_each_arg,length_of_each_arg):
                exec("a.append(f'{value:^"+str(length)+"}')")
                # _ = "f'{"+str(value)+":^"+str(length)+"}'"
                # print(_)
                # exec("a.append(f'{"+str(value)+":^"+str(length)+"}')")
            output += ij_tag_setting[tag]['sep'].join(a)+ij_tag_setting[tag]['end']
        elif i == 'l':
            a = []
            for value,length in zip(len_of_each_arg,length_of_each_arg):
                exec("a.append(f'{value:^"+str(length)+"}')")
            output += ij_tag_setting[tag]['sep'].join(a)+ij_tag_setting[tag]['end']
        elif i == 't':
            a = []
            for value,length in zip(type_of_each_arg,length_of_each_arg):
                exec("a.append(f'{value:^"+str(length)+"}')")
            output += ij_tag_setting[tag]['sep'].join(a)+ij_tag_setting[tag]['end']
    
    print(f"{ij_tag_setting[tag]['color']}{output}{ct.set}",end='')

