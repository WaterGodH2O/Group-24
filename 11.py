def star_decorator(func):
    def wrapper():
        return "*** " + func() + " ***"
    return wrapper

@star_decorator  # 直接使用装饰器
def basic_text():
    return "Hello, World!"

print(basic_text())  # 输出: *** Hello, World! ***