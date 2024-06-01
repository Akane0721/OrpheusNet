class NumberNote():
    def __init__(self, name):
        self.name = name
        self.octave = 4
        self.shift = 0
        self.duration = 1
        self.isnote = True

    def setDown(self, down_symbols):
        for symbol in down_symbols:
            if symbol == "dot":
                self.octave -= 1
            elif symbol == "dash":
                self.duration /= 2
            else:
                raise ValueError("Unknown down symbol")
            
def is_equal_tie(note_list, left, right):
    n1 = note_list[left]
    n2 = note_list[right]
    if n1.name == n2.name:
        if n1.octave == n2.octave:
            if n1.shift == n2.shift:
                adjacence = True
                for i in range(left + 1, right):
                    if note_list[i].isnote:    # 连音线
                        return False
                if adjacence:  #延音线
                    return True
    return False

def ArrangeLine(note_list, accompany=False):
    useless_notes = ["(", ")", "breath", "repeat"]

    i = 0
    while i < len(note_list):
        if note_list[i].name in useless_notes:
            note_list[i].isnote = False
            if note_list[i].name == "(":
                accompany = True
            if note_list[i].name == ")": 
                if accompany == False: #1误判断为)
                    note_list[i].name = "1"
                    note_list[i].isnote = True
                else:
                    accompany = False
            i += 1
        elif note_list[i].name == "sharp" or note_list[i].name == "flat":
            note_list[i + 1].shift = 1 if note_list[i].name == "sharp" else -1
            note_list[i].isnote = False
            i += 1

        elif note_list[i].name == "dot":
            if i + 1 < len(note_list) and note_list[i + 1].name == "dot":  # 复附点音符
                note_list[i - 1].duration *= 1.75
                note_list[i + 1].isnote = False
                note_list[i].isnote = False
                i += 2
            else:
                note_list[i - 1].duration *= 1.5
                note_list[i].isnote = False
                i += 1

        elif note_list[i].name == "dash":
            j = i - 1
            while note_list[j].isnote == False:
                j -= 1
            note_list[j].duration += 1
            note_list[i].isnote = False
            i += 1

        else:
            i += 1
    
    return note_list, accompany

def SetUp(note_list, up_symbols):
    cross_line_ties = []
    for target, symbol in up_symbols:
        if symbol == "line":  # 保持音记号
            pass
        elif symbol == "dot":
            note_list[target].octave += 1  

    extension = False

    for target, symbol in up_symbols:   #额外循环
        if extension:
            if symbol == "dot":
                note_list[target].octave -= 1
                note_list[target].duration *= 2
                extension = False

        if symbol == "tie": 
            left, right = target
            if left == -1 and right == -1:  # 延长记号
                extension = True     

            elif left == -1 or right == -1:
                cross_line_ties.append(target)

            elif left == right:  # dot错误识别为tie
                note_list[left].octave += 1

            elif is_equal_tie(note_list, left, right):
                    note_list[left].duration += note_list[right].duration
                    note_list[right].isnote = False
    
    return note_list, cross_line_ties

def wholeprocess(note_list, cross_line_ties): #无法处理一行同时多个跨行连音线
    if len(cross_line_ties) % 2 != 0:
        raise ValueError("Incorrect numbers of cross-line ties! ")
    
    i = 0
    while i < len(cross_line_ties):
        if cross_line_ties[i][0] != -1:
            left = cross_line_ties[i][0]
            while cross_line_ties[i][1] == -1:
                i += 1
            if i < len(cross_line_ties):
                right = cross_line_ties[i][1]
                if is_equal_tie(note_list, left, right):
                    note_list[left].duration += note_list[right].duration
                    note_list[right].isnote = False
        i += 1
    
    i = len(note_list) - 1
    while i >= 0:
        if note_list[i].isnote == False:
            del note_list[i]
        i -= 1

    return note_list









