# Python 生成器（Generator）教程

# ========== 1. 什么是生成器 ==========
# 生成器是一种特殊的迭代器，用 yield 关键字定义
# 特点：惰性求值，用一次生成一个值，内存占用小

# ========== 2. 生成器函数（yield）==========
def count_up_to(n):
    """数到 n - 普通函数 vs 生成器"""
    num = 1
    while num <= n:
        yield num      # yield = 暂停并返回值，下次从这里继续
        num += 1

# 使用生成器
counter = count_up_to(5)
print(type(counter))       # <class 'generator'>
print(list(counter))       # [1, 2, 3, 4, 5]

# 手动逐个取
counter2 = count_up_to(3)
print(next(counter2))      # 1
print(next(counter2))      # 2
print(next(counter2))      # 3
# print(next(counter2))    # ❌ StopIteration，生成器耗尽了


# ========== 3. yield 的工作方式 ==========
def demo_yield():
    print("开始")
    yield 1
    print("继续1")
    yield 2
    print("继续2")
    yield 3
    print("结束")

g = demo_yield()
print(next(g))   # 开始 + 1
print(next(g))   # 继续1 + 2
print(next(g))   # 继续2 + 3
# next(g)        # 结束 + StopIteration


# ========== 4. 生成器表达式（类似列表推导式）==========
# 列表推导式 - 一次性生成所有数据，占内存
squares_list = [x**2 for x in range(1000000)]   # 内存里存了100万个数

# 生成器表达式 - 惰性生成，几乎不占内存
squares_gen = (x**2 for x in range(1000000))    # 只是一个生成器对象

print(type(squares_gen))   # <class 'generator'>

# 取前5个
for i, val in enumerate(squares_gen):
    if i >= 5:
        break
    print(val)             # 0, 1, 4, 9, 16


# ========== 5. 实际应用场景 ==========

# 场景1：读取大文件（一行一行读，不一次性载入内存）
def read_large_file(filepath):
    """逐行读取大文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

# 场景2：无限序列
def fibonacci():
    """斐波那契无限序列"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
for _ in range(10):
    print(next(fib), end=' ')   # 0 1 1 2 3 5 8 13 21 34
print()


# 场景3：数据管道（处理流水线的每一环节都是生成器）
def read_numbers():
    """模拟数据源"""
    for i in range(1, 11):
        yield i

def filter_even(numbers):
    """过滤偶数"""
    for n in numbers:
        if n % 2 == 0:
            yield n

def multiply_by_ten(numbers):
    """乘以10"""
    for n in numbers:
        yield n * 10

# 组装管道
pipeline = multiply_by_ten(filter_even(read_numbers()))
print(list(pipeline))   # [20, 40, 60, 80, 100]


# ========== 6. 生成器与迭代器的关系 ==========
# 生成器是迭代器的一种，自动实现了 __iter__ 和 __next__

gen = (x for x in range(3))
print(hasattr(gen, '__iter__'))    # True
print(hasattr(gen, '__next__'))    # True

# for 循环本质就是不断调用 next()
for item in count_up_to(3):
    print(item)


# ========== 7. yield from（委托子生成器）==========
def sub_generator():
    yield 1
    yield 2

def main_generator():
    yield '开始'
    yield from sub_generator()   # 把子生成器的值直接 yield 出来
    yield '结束'

print(list(main_generator()))   # ['开始', 1, 2, '结束']


# ========== 8. 进阶：send 方法（双向通信）==========
def accumulator():
    """累加器 - 可以接收外部传入的值"""
    total = 0
    while True:
        value = yield total   # yield 返回 total，同时可以接收 send() 的值
        if value is None:
            break
        total += value

acc = accumulator()
print(next(acc))       # 0，启动生成器
print(acc.send(10))    # 10
print(acc.send(20))    # 30
print(acc.send(5))     # 35
acc.close()            # 关闭生成器


# ========== 9. 实际练习：简化版日志处理器 ==========
def log_filter(log_lines, keyword):
    """过滤包含关键字的日志行"""
    for line in log_lines:
        if keyword in line:
            yield line

# 模拟日志
logs = [
    "2024-01-01 INFO 系统启动",
    "2024-01-01 ERROR 数据库连接失败",
    "2024-01-01 INFO 用户登录",
    "2024-01-01 ERROR 内存不足",
]

errors = log_filter(logs, "ERROR")
for err in errors:
    print(err)


# ========== 总结 ==========
print("\n=== 生成器 vs 列表 ===")
print("列表推导式: [x**2 for x in range(5)] =", [x**2 for x in range(5)])
print("生成器表达式: (x**2 for x in range(5)) =", list(x**2 for x in range(5)))
print("\n生成器优点:")
print("1. 省内存 - 惰性求值，用多少生成多少")
print("2. 可以表示无限序列")
print("3. 代码简洁，状态自动保存")
