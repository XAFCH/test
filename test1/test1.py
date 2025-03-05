# 第一个程序
print("hello python")

# 简单操作
# Python可以进行算术运算。 输入算式打印输出。
print(6 + 3)
print(4 + 3 - 2)

# Python执行乘法和除法，用星号 * 表示乘法和正斜杠 / 来表示除法。
# 使用括号确定先执行哪些操作。
print(2 * (3 + 4))
print(10 / 2)  # 使用除法结果会变成浮点数（有小数点），我们将在后面的课程中介绍更多有浮点数的知识。

# 在 Python 中除以零会产生错误。
# print(5 / 0)
# 在 Python 中，错误消息的最后一行表示错误的类型。
# 要仔细阅读错误信息，因为它们经常会告诉你如何修复程序！

# Python 中常见的运算符：+ - * / %
# 整除、幂数和布尔类型：// ** True & False
# 计算商和余数使用的符号分别是 // 和 %。(/在Python中获取的是相除的结果，一般为浮点数)
print(20 // 6)
print(1.25 % 0.5)
print(2 // 2)
print(2 / 2.0)
print(2 // 3)
print(3.0 // 2)
print(3.2 // 1.5)
print(3 ** 2)
print(4.0 ** 3)
print(5 ** 3)
print(9 ** (1 / 2))  # 指数运算。该操作使用两个星号 ** 表示。
print(True + True)  # 1 + 1
print(True * False)  # 1 * 0
# print(True / False) # 1 / 0

# Python 中使用浮点数来表示不是整数的数字。
# 浮点数表示的数字的例子：0.5 和 -7.8237591。
# 浮点数可以通过输入带小数点的数字直接创建，也可以使用整数除法等操作产生。数字结尾的零会被忽略。
print(3 / 4)
print(0.523322)
# 计算机不能完全精确地存储浮点数，就像我们不能写下1/3（0.3333333333333333 ...）的完整小数点一样。

# 两个整数相除将产生一个浮点数。
# 一个浮点数也是通过在两个浮点数或者在一个浮点数和一个整数上运算来产生的。
print(10 / 2)
print(6 * 7.0)
print(5 + 2.32)
# 浮点数可以和整数进行运算，因为运算时Python会默默地将整数转换成浮点数。

# 如果你想在 Python 中使用文本，你必须使用字符串。
# 通过在两个单引号或双引号之间输入文本来创建字符串。
# 当 Python 控制台显示一个字符串时，通常使用单引号。

# 有些字符不能直接包含在字符串中。例如，双引号不能直接包含在双引号字符串中;这会导致字符串过早地结束,产生错误。
# 要在字符串中添加这些字符必须在它们面前添加反斜杠进行转义。
# 其他必须转义的常见字符是换行符和反斜杠。
# 双引号只需要在双引号字符串中转义，单引号字符串也是如此。
print('Loen\'s mother: He\'s not the Messiah. He\'s a very naughty boy!')
# Loen's mother: He's not the Messiah. He's a very naughty boy!
# \n 代表新的一行。
# 反斜杠也可以用于转义制表符，任意的Unicode字符，以及其他各种不能打印的东西。这些字符被称为转义字符。

# Python 提供了一种简单的方法来避免手动编写 \n 来转义字符串中的换行符。用三组引号创建一个字符串，按 Enter 键创建的换行符会自动转义。
print("""Customer: Good morning.
Owner: Good morning, Sir. Welcome to the National Cheese Emporium.""")
# Customer: Good morning.
# Owner: Good morning, Sir. Welcome to the National Cheese Emporium.

# Python 中一切皆对象，每一个对象都有一个唯一的标示符（id()）、类型（type()）以及值。
# 对象根据其值能否修改分为可变对象和不可变对象，其中数字、字符串、元组属于不可变对象，字典以及列表、字节数组属于可变对象。而“菜鸟”常常会试图修改字符串中某个字符。
teststr = "I am a string"
teststr = teststr[:11] + 'h' + teststr[12:]
print(teststr)