# Python 多态与抽象类教程

# ========== 1. 多态（Polymorphism）==========
# 多态 = "多种形态"，同一个接口，不同实现

class Animal:
    """动物基类"""
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "汪汪！"

class Cat(Animal):
    def speak(self):
        return "喵喵~"

class Duck(Animal):
    def speak(self):
        return "嘎嘎嘎"

# 多态的体现：同一个函数，处理不同类型的对象
def animal_concert(animals):
    """动物演唱会 - 接收任何 Animal 子类的列表"""
    for animal in animals:
        print(f"{type(animal).__name__}: {animal.speak()}")


# ========== 2. 鸭子类型（Duck Typing）==========
# Python 特色：不关注对象类型，只关注有没有某个方法

class Car:
    """汽车不是动物，但也能 '叫'"""
    def speak(self):
        return "滴滴！"

# 只要对象有 speak() 方法，就能传入 animal_concert
def make_it_speak(obj):
    """不关心对象是什么类型，只要有 speak() 方法就行"""
    print(obj.speak())


# ========== 3. 抽象类（Abstract Base Class）==========
# 强制子类必须实现某些方法，否则不能实例化

from abc import ABC, abstractmethod

class Shape(ABC):
    """形状抽象类 - 不能直接创建实例"""

    @abstractmethod
    def area(self):
        """计算面积 - 子类必须实现"""
        pass

    @abstractmethod
    def perimeter(self):
        """计算周长 - 子类必须实现"""
        pass

    def describe(self):
        """普通方法 - 子类可以直接继承使用"""
        return f"面积: {self.area()}, 周长: {self.perimeter()}"


class Rectangle(Shape):
    """矩形"""
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Circle(Shape):
    """圆形"""

    def __init__(self, radius):
        self.radius = radius

    def area(self):
        import math
        return math.pi * self.radius ** 2

    def perimeter(self):
        import math
        return 2 * math.pi * self.radius


# ========== 4. 结合之前的游戏角色 ==========
from abc import ABC, abstractmethod

class GameCharacter(ABC):
    """游戏角色抽象基类"""

    def __init__(self, name, level=1, hp=100):
        self.name = name
        self._level = level
        self._hp = hp

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = max(0, value)

    @property
    def is_alive(self):
        return self.hp > 0

    @abstractmethod
    def attack(self):
        """攻击 - 每个子类必须实现自己的攻击方式"""
        pass

    def introduce(self):
        return f"我是{self.name},等级{self.level},生命值{self.hp}"


class Warrior(GameCharacter):
    """战士"""
    def __init__(self, name, level=1, hp=200, weapon=""):
        super().__init__(name, level, hp)
        self.weapon = weapon

    def attack(self):
        return f"{self.name}挥舞{self.weapon}猛击!"


class Mage(GameCharacter):
    """法师"""
    def __init__(self, name, level=1, hp=80, mana=100):
        super().__init__(name, level, hp)
        self.mana = mana

    def attack(self):
        if self.mana >= 10:
            self.mana -= 10
            return f"{self.name}释放魔法弹！"
        else:
            return f"{self.name}法力不足！"


def battle(characters):
    """战斗场景 - 多态的体现"""
    print("=== 战斗开始 ===")
    for char in characters:
        print(char.attack())


# ========== 演示 ==========
if __name__ == "__main__":
    print("=== 多态演示 ===")
    zoo = [Dog(), Cat(), Duck()]
    animal_concert(zoo)

    print("\n=== 鸭子类型 ===")
    make_it_speak(Dog())
    make_it_speak(Car())   # 汽车不是动物，也能"叫"

    print("\n=== 抽象类 ===")
    rect = Rectangle(3, 4)
    circle = Circle(5)
    print(f"矩形: {rect.describe()}")
    print(f"圆形: {circle.describe()}")

    # shape = Shape()  # ❌ 报错！抽象类不能实例化

    print("\n=== 游戏角色多态 ===")
    team = [Warrior("战士", weapon="大剑"), Mage("法师")]
    battle(team)

