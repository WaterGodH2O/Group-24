
global flag
flag = True  # 全局变量




def some_function():
    global flag  # 但后面又声明 global，导致错误
    flag = False  # 这里 Python 认为 flag 是局部变量


some_function()