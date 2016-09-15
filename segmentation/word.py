# ------------------------------------------------------------
# Final Project of Introduction to Computation
# Project Name: Chinese Word Segmentation
# Team Name: TIPO
# Members: Chris Tse, Binbin Lee, York Lee, Xiaobo Chao
# Date of last update: 2012.1.2
# Copyright 2011-2012
# ------------------------------------------------------------

# -*- coding=gb2312 -*-
#-*- coding: cp936 -*-

from Tkinter import *
from tkMessageBox import *
from tkSimpleDialog import *
from tkFileDialog import *
import string    # Import the string module.
import tkFont    # Import the tkFont module.

# ------------------------------------------------------------
# Now here are some functions of user interface.
# ------------------------------------------------------------

# Show the instruction.
def Instruction():
    tl = Toplevel()
    tl.geometry('600x350')
    infile = open('instruction.txt', 'r')
    content = infile.read().decode('gb2312')
    infile.close()
    Label(tl, font = 'Verdana', text = content, justify='left').pack()

# Show 'Copyright' of this program.
def Copyright():
    tl = Toplevel()
    tl.geometry('600x300')
    infile = open('copyright.txt', 'r')
    content = infile.read().decode('gb2312')
    infile.close()
    Label(tl, font = 'Verdana', text = content, justify='left').pack()

# Show 'About' of this program.
def AboutProgram():
    tl = Toplevel()
    tl.geometry('300x300')
    infile = open('program.txt', 'r')
    content = infile.read().decode('gb2312')
    infile.close()
    Label(tl, font = 'Verdana', text = content, justify='left').pack()

# Select a sentence to segment.
def SelectSent():
    global retVal, sentnum, max_len, new_data, rules, dict_tf, text3
    retVal = askinteger("Select Sentence", "Enter the number of the sentence to segment: ")
    if (retVal != None) and (type(retVal) == type(1)) and (1 <= retVal <= sentnum):
        result = WordSeg(new_data[retVal - 1], rules['symb'], rules['symbs'], rules['surname'], max_len, dict_tf)
        text3.delete('1.0', END)
        text3.insert('1.0', result)
    elif retVal == None:
        text3.insert('1.0', '')
    else:
        text3.delete('1.0', END)
        text3.insert('1.0', 'Out of range! Please select again!')

# ------------------------------------------------------------
# Now here are some functions of word segmentation.
# ------------------------------------------------------------

# This function opens files.
def OpenFiles():
    global dict_file, rule_file, rules
    rule_file = open("rules.txt", 'r')
    rules = {}
    for line in rule_file:
        line = line.decode('utf-8').encode('utf-8')
        line = line.decode('utf-8')
        if line[-1] == '\n':
            line = line[:-1]
        if line[0] == u'\ufeff':
            line = line[1:]
        temp = line.split(' ')
        rules[temp[0]] = temp[1:]
    rules['symb'] += [' ']

# This function loads the rules.
def Loadrule():
    global dict_file, rule_file, rules
    path = askopenfilename(title = 'Load rules')
    if type(path) == unicode:
        rule_file = open(path, 'r')
        rules = {}
        for line in rule_file:
            line = line.decode('utf-8').encode('utf-8')
            line = line.decode('utf-8')
            if line[-1] == '\n':
                line = line[:-1]
            if line[0] == u'\ufeff':
                line = line[1:]
            temp = line.split(' ')
            rules[temp[0]] = temp[1:]
        rules['symb'] += [' ']

# Close files.
def CloseFile(dict_file, rule_file):
    dict_file.close()
    rule_file.close()

# Open a text file.
def OpenFile():
    global text
    path = askopenfilename(title = 'Sentences Input')
    if type(path) == unicode:
        text.delete('1.0', END)
        file_in = open(path, 'r')
        s = file_in.read().decode('utf-8', 'ignore')
        text.insert('1.0', s)
        file_in.close()

# Read the lexicon.
def ReadDict():
    global dict_tf, dict_idf, dict_attr, dict_file
    dict_tf, dict_idf, dict_attr = {}, {}, {}
    for line in dict_file:
        line = line.decode('utf-8').encode('utf-8')
        line = line.decode('utf-8')
        temp = line.split('\t')
        dict_tf[temp[0]] = float(temp[1])
        dict_idf[temp[0]] = float(temp[2])
        dict_attr[temp[0]] = temp[3][:-1]

# Load the lexicon.
def LoadLex():
    global dict_file, text
    path = askopenfilename(title = 'Open lexicon')
    if type(path) == unicode:
        dict_file = open(path, 'r')
        ReadDict()

# Make a list with a file.
def MakeList(filename):
    line = filename.readline()
    line = line.decode('utf-8').encode('utf-8')
    line = line.decode('utf-8')
    return line.split(' ')

# Preprocess the input data.
def Preprocess(content):
    data = []
    temp = ''.decode('utf-8')
    for letter in content:
        if letter != '\n':
            temp += letter
        else:
            if temp != '':
                data += [temp]
            temp = ''.decode('utf-8')
    return data

# Add a sentence to a list.
def AddSentence(data, sentence):
    if sentence[0] == u'\u201d':    # Move the right quote punctuation.
        data[-1] += sentence[0]
        sentence = sentence[1:]
    if sentence[0] == u'\u2026':    # Deal with the ellipsis.
        data[-1] += sentence[0]
        return data
    if sentence[0] == u'\ufeff':    # Deal with an unknown symbol.
        sentence = sentence[1:]
    data += [sentence]
    return data

# Deal with punctures, numbers and English characters.
def DealSNE(sent, symbs):
    nlst = []
    i = 0
    while i < len(sent):
        if sent[i] in symbs:
            length = 0
            while sent[i+length] in symbs:
                length += 1
                if i + length == len(sent):
                    break
            nlst += [sent[i:i+length]]
            sent = sent[:i] + '@' + sent[i+length:]
                #This symbol help us to seperate it from others.
        i += 1
    return sent, nlst

# Whether a letter is single in forward sequence.
def SingleWord(sent, i, n, dict_tf, symb):
    if n == 1 and sent[i] not in symb:
        return True
    else:
        while sent[i:i+n] not in dict_tf:
            n -= 1
            if n == 1:
                break
    if n == 1 and sent[i] not in symb:
        return True
    else:
        return False

# Deal with names.
def GetName(sent, surname, max_len, dict_tf, symb):
    if sent[-1] not in symb:
        a = 1
    else:
        a = 0
    nlst1 = nlst2 = []
    i = 0
    while i < len(sent)-3+a:
        if sent[i:i+2] in surname:
            n = min(max_len, i)
            while sent[i-n:i+2] not in dict_tf:
                if n == 0:
                    # This just in case the character is the first character of the sentence.
                    break
                n -= 1
                if n == 0:
                    break
            if n == 0:
                if i == len(sent)-4+a:
                    nlst1 += [sent[i:i+3]]
                    sent = sent[:i] + 'a' + sent[i+3]
                else:
                    n = min(max_len, len(sent)-i-3)
                    if SingleWord(sent, i+3, n, dict_tf, symb) or sent[i:i+4] in dict_tf:
                        nlst1 += [sent[i:i+4]]
                        sent = sent[:i] + 'a' + sent[i+4:]
                    else:
                        nlst1 += [sent[i:i+3]]
                        sent = sent[:i] + 'a' + sent[i+3:]
        i += 1
    i = 0
    while i < len(sent)-2+a:
        if sent[i] in surname:
            head = max(0, i-max_len+1)
            single = True
            while head <= i:
                length = min(max_len, len(sent)-head)
                while head+length > i:
                    if sent[head:head+length] in dict_tf:
                        if length != 1:
                            single = False
                    length -= 1
                head += 1
            if single:
                n = min(max_len, len(sent)-i-2)
                if SingleWord(sent, i+2, n, dict_tf, symb):
                    nlst2 += [sent[i:i+3]]
                    sent = sent[:i] + 'b' + sent[i+3:]
                else:
                    nlst2 += [sent[i:i+2]]
                    sent = sent[:i] + 'b' + sent[i+2:]
        i += 1
    return sent, nlst1, nlst2                    

# Match backward with maximum word.
def MatchBackward(part, max_len, dict_tf, symb):
    result = []
    word_num = single_word = 0
    weight = 1.0
    tail = len(part) - 1
    while tail >= 0:
        if part[tail] in symb:
            if part[tail] == u'\u2026':    # Deal with the ellipsis.
                result = [part[tail-1:tail+1]] + result
                tail -= 2
                continue
            result = [part[tail]] + result
            tail -= 1
            continue
        head = max(0, tail - max_len + 1)
        while not dict_tf.has_key(part[head:tail+1]):
            if head == tail:
                break
            head += 1
        result = [part[head:tail+1]] + result
        word_num += 1
        weight *= dict_tf[part[head:tail+1]]
        if tail - head == 0:
            single_word += 1
        else:
            weight *= (tail - head) ** 4
        tail = head - 1
    if word_num + single_word == 1:
        return result, 2, weight
    return result, word_num + single_word, weight

# Match forward with maximum word.
def MatchForward(part, max_len, dict_tf, symb):
    result = []
    word_num = single_word = 0
    weight = 1.0
    head = 0
    while head <= len(part) - 1:
        if part[head] in symb:
            if part[head] == u'\u2026':    # Deal with the ellipsis.
                result += [part[head:head+2]]
                head += 2
                continue
            result += [part[head]]
            head += 1
            continue
        tail = min(len(part) - 1, head + max_len - 1)
        while not dict_tf.has_key(part[head:tail+1]):
            if head == tail:
                break
            tail -= 1
        result += [part[head:tail+1]]
        word_num += 1
        weight *= dict_tf[part[head:tail+1]]
        if tail - head == 0:
            single_word += 1
        else:
            weight *= (tail - head) ** 4
        head = tail + 1
    if word_num + single_word == 1:
        return result, 2, weight
    return result, word_num + single_word, weight

# Find the maximum weight.
def FindMaxWgt(w_dict):
    weight = -1.0
    for entry in w_dict:
        if w_dict[entry] >= weight:
            weight = w_dict[entry]
            result = entry
    return weight, result

# Get sentence back to normal.
def GetBack(result, a, nlst):
    i = k = 0
    nresult = ''
    while i < len(result):
        if result[i] == a:
            nresult += '%s' %nlst[k]
            k += 1
            i += 1
            continue
        nresult += result[i]
        i += 1
    return nresult

# Deal with word segmentation.
def WordSeg(sent, symb, symbs, surname, max_len, dict_tf):
    sent, nlst = DealSNE(sent, symbs)
    sent, nlst1, nlst2 = GetName(sent, surname, max_len, dict_tf, symb+symbs)
    weight = -1.0
    for i in range(len(sent) + 1):
        if 0 < i < len(sent) and sent[i-1] == u'\u2026' and sent[i] == u'\u2026':
            continue    # Deal with the ellipsis.
        leftb, sm1b, w1b = MatchBackward(sent[:i], max_len, dict_tf, symb)
        leftf, sm1f, w1f = MatchForward(sent[:i], max_len, dict_tf, symb)
        rightf, sm2f, w2f = MatchForward(sent[i:], max_len, dict_tf, symb)
        rightb, sm2b, w2b = MatchBackward(sent[i:], max_len, dict_tf, symb)
        w_dict = {}
        w_dict['|'.join(leftb + rightf)] = w1b * w2f / (sm1b + sm2f - 1) ** 5      
        w_dict['|'.join(leftb + rightb)] = w1b * w2b / (sm1b + sm2b - 1) ** 5
        w_dict['|'.join(leftf + rightf)] = w1f * w2f / (sm1f + sm2f - 1) ** 5
        w_dict['|'.join(leftf + rightb)] = w1f * w2b / (sm1f + sm2b - 1) ** 5
        nweight, nresult = FindMaxWgt(w_dict)
        if nweight >= weight:
            weight = nweight
            result = nresult
    result = GetBack(result, 'a', nlst1)
    result = GetBack(result, 'b', nlst2)
    result = GetBack(result, '@', nlst)
    return result

# Produce the output.txt.
def SegmentAll():
    global new_data, rules, max_len, dict_tf
    out_file = open("output.txt", 'w')
    for i in range(len(new_data)):
        temp = WordSeg(new_data[i], rules['symb'], rules['symbs'], rules['surname'], max_len, dict_tf)
        temp = temp.encode('utf-8')
        out_file.write('%d) %s\n' % (i + 1, temp))
    out_file.close()

# Segment sentences.
def SegSentence():
    global dict_file, rules, text, text2, sentnum, new_data, max_len
    text2.delete('1.0', END)
    content = text.get('1.0', END)
    data = Preprocess(content)
    new_data = []
    for element in data:
        sentence = ''.decode('utf-8')
        for letter in element:
            sentence += letter
            if letter in rules['punc']:
                new_data = AddSentence(new_data, sentence)
                sentence = ''.decode('utf-8')
        if sentence != '':
            new_data = AddSentence(new_data, sentence)
    max_len = 10
    sentnum = len(new_data)
    for i in range(sentnum):
        text2.insert('%d.0' % (i + 1), "%d) %s\n" % (i + 1, new_data[i]))
    SegmentAll()

# Add word into the lexicon.
def add_word():
    global lex_cont, text4, path
    content = text4.get('1.0', END)
    content = content.encode('utf-8')
    files = open(path, 'w')
    files.write(lex_cont)
    files.write(content)
    files.close()
    toplevel.destroy()

# Prepare for adding words into the lexicon.
def addword():
    global lex_cont, text4, path, root, toplevel
    path = askopenfilename(title = 'Choose a lexicon to add words')
    if type(path) == unicode:
        files = open(path, 'r')
        lex_cont = files.read().decode('utf-8', 'ignore')
        lex_cont = lex_cont.encode('utf-8')
        files.close()
        toplevel = Toplevel(root)
        text4 = Text(toplevel)
        msg1 = 'You should pay attention to the format:\n'
        msg2 = '1. There is one word in each line\n'
        msg3 = '2. The format of each line:\n'
        msg4 = '   word+a tab+tf+a tab+idf+a tab+attribute\n'
        msg5 = '3. See examples in dict.txt'
        Label(toplevel, font = 'Consolas', text = msg1+msg2+msg3+msg4+msg5, justify='left').pack()
        text4.pack()
        Button(toplevel, text = 'OK', command = add_word).pack()

# Add rule into the rules.
def add_rule():
    global rule_cont, text5, paths
    content = text5.get('1.0', END)
    content = content.encode('utf-8')
    files = open(paths, 'w')
    files.write(rule_cont)
    files.write(content)
    files.close()
    toplevels.destroy()
    
# Prepare for adding new rule into the rules.
def Addrule():
    global rule_cont, text5, paths, root, toplevels
    paths = askopenfilename(title = 'Choose a rules file to add rules')
    if type(paths) == unicode:
        files = open(paths, 'r')
        rule_cont = files.read().decode('utf-8','ignore')
        rule_cont = rule_cont.encode('utf-8')
        files.close()
        toplevels = Toplevel(root)
        text5 = Text(toplevels)
        msg1 = 'You should pay attention to the format:\n'
        msg2 = '1. There is one rule in each line\n'
        msg3 = '2. The format of each line:\n'
        msg4 = '   rule name+a space+rule content\n'
        msg5 = '3. See examples in rules.txt'
        Label(toplevels, font = 'Consolas', text = msg1+msg2+msg3+msg4+msg5, justify='left').pack()
        text5.pack()
        Button(toplevels, text = 'OK', command = add_rule).pack()

# Save the result of sentences segmentation.
def save1():
    content = text2.get('1.0', END)
    contents = content.encode('utf-8')
    path = asksaveasfilename(title = 'Sentences Output')
    if type(path) == unicode:
        infile = open(path, 'w')
        infile.write(contents)
        infile.close()
    
# Save the result of words segmentation.
def save2():
    content = text3.get('1.0', END)
    contents = content.encode('utf-8')
    path = asksaveasfilename(title = 'Words Output')
    if type(path) == unicode:
        infile = open(path, 'w')
        infile.write(contents)
        infile.close()

# ------------------------------------------------------------
# Now here is the main function.
# ------------------------------------------------------------

def main():
    global text, text2, text3, root
    # Open the default rules.
    OpenFiles()
    
    # Create the root.
    root = Tk()
    root.geometry('1200x700')
    root.title('Chinese Word Segmentation')
    
    # Create the memu.
    menu = Menu(root)
    root.config(menu = menu)
    filemenu = Menu(menu)
    menu.add_cascade(label = 'File', menu = filemenu)
    filemenu.add_command(label = 'Open...', command = OpenFile)
    filemenu.add_separator()
    filemenu.add_command(label = 'Save sentence as...', command = save1)
    filemenu.add_command(label = 'Save word as...', command = save2)
    filemenu.add_separator()
    filemenu.add_command(label = 'Exit', command = root.destroy)
    loadmenu = Menu(menu)
    menu.add_cascade(label = 'Lexicon', menu = loadmenu)
    loadmenu.add_command(label = 'Load lexicon...', command = LoadLex)
    loadmenu.add_command(label = 'Add word to lexicon...', command = addword)
    rulemenu = Menu(menu)
    menu.add_cascade(label = 'Rule', menu = rulemenu)
    rulemenu.add_command(label = 'Load rule...', command=Loadrule)
    rulemenu.add_command(label = 'Modify rule...', command=Addrule)
    helpmenu = Menu(menu)
    menu.add_cascade(label = 'Help', menu = helpmenu)
    helpmenu.add_command(label = 'Instruction...', command = Instruction)
    aboutmenu = Menu(menu)
    menu.add_cascade(label = 'About', menu = aboutmenu)
    aboutmenu.add_command(label = 'About this program...', command = AboutProgram)
    aboutmenu.add_command(label = 'Copyright...', command = Copyright)
    
    # Create the status of root.
    status = Label(root, text = 'Now you are segmenting sentences and words...', anchor=S)
    status.pack(side = BOTTOM, fill = X)
    
    # Create the frame for inputting the text.
    framex = Frame(root, height = 700, width = 1200, bg = 'lightblue')
    frame = Frame(framex, height = 700, width = 300, bg = 'lightblue')
    frame0 = Frame(frame, height = 150, width = 600)
    frame1 = Frame(frame, height = 30, width = 300, bg = 'lightblue')
    frame2 = Frame(frame, height = 100, width = 300, bg = 'lightblue')
    framey = Frame(frame, height = 30, width = 300, bg = 'lightblue')
    
    # Create the fonts.
    ft1 = tkFont.Font(family = 'Jokerman', size=60, weight = tkFont.BOLD)
    ft2 = tkFont.Font(family = 'Chaparral Pro', size = 16, weight = tkFont.NORMAL)
    ft3 = tkFont.Font(family = 'Hobo Std', size=13, weight = tkFont.NORMAL)
    Label(frame0, text = 'Welcome', font = ft1, bg = 'lightblue').grid()
    msg1 = '1. Please load the lexicon: Lexicon --> Load lexicon...\n'
    msg2 = '2. Now you can input texts, or open a file (must be UTF-8).'
    Label(frame1, font = ft2, bg = 'lightblue', text = msg1 + msg2).pack(side = LEFT)
    
    # Create the 'Open' button.
    button1 = Button(frame1, font = ft3, text = 'Open', width = 6, command = OpenFile)
    button1.pack(side = LEFT)
    
    # Create the text for inputting and the corresponding scrollbar.
    text = Text(frame2)
    scrollbar = Scrollbar(frame2)
    scrollbar.pack(side = RIGHT, fill = Y)
    text['yscrollcommand'] = scrollbar.set
    text.pack(side = LEFT)
    scrollbar['command'] = text.yview
    
    # Create the 'OK' button.
    Label(framey, font = ft2, bg = 'lightblue', text = '3. If you are ready to segment, click ').pack(side = LEFT)
    button2 = Button(framey, font = ft3, text = 'OK', width = 6, command = SegSentence)
    button2.pack(pady = 5)
    framex.pack()
    
    # Create frames.
    frame.pack(side = LEFT, pady = 5, padx = 10)
    frame0.pack(side = TOP, pady = 5)
    frame1.pack(side = TOP, pady = 5)
    frame2.pack()
    framey.pack(side = BOTTOM)
    
    # Create frames to put contents in them afterwards.
    frame3 = Frame(framex, height = 700, width = 400)
    frame4 = Frame(frame3, height = 400, width = 400, bg = 'lightblue')
    frame5 = Frame(frame3, height = 250, width = 400, bg = 'lightblue')
    frame6 = Frame(frame4, height = 40, width = 400, bg = 'lightblue')
    frame7 = Frame(frame4, height = 200, width = 400, bg = 'lightblue')
    frame78 = Frame(frame5, height = 20, width = 400, bg = 'lightblue')
    frame8 = Frame(frame5, height = 20, width = 400)
    frame9 = Frame(frame5, height = 300, width = 400)
    Label(frame6, font = ft2, bg = 'lightblue', text = 'Here is the result of sentences segmentation:').pack(side = LEFT)
    
    # Create texts and corresponding scrollbars.
    text2 = Text(frame7)
    scrollbar2 = Scrollbar(frame7)
    scrollbar2.pack(side = RIGHT, fill = Y)
    text2['yscrollcommand'] = scrollbar2.set
    text2.pack(side = LEFT)
    scrollbar2['command'] = text2.yview
    Label(frame8, font = ft2, bg = 'lightblue', text = 'Here is the result of words segmentation:').pack(side = LEFT)
    text3 = Text(frame9)
    scrollbar3 = Scrollbar(frame9)
    scrollbar3.pack(side = RIGHT, fill = Y)
    text3['yscrollcommand'] = scrollbar3.set
    text3.pack(side = LEFT)
    scrollbar3['command'] = text3.yview
    Label(frame78, font = ft2, bg = 'lightblue', text = '4. Select one sentence to segment:').pack(side = LEFT)
    
    # Create the button that can select which sentence to be segmented.
    button3 = Button(frame78, font = ft3, text = 'Select', width = 6, command = SelectSent)
    button3.pack(side = LEFT, pady = 3)
    frame3.pack(side = LEFT, padx = 10)
    frame4.pack(side = TOP)
    frame5.pack()
    frame6.pack(side = TOP, pady = 3)
    frame7.pack()
    frame78.pack()
    frame8.pack(side = TOP, pady = 3)
    frame9.pack(pady = 3)

    mainloop()

main()
