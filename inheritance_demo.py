# Python 继承教程 - 动物世界

# ========== 1. 基础继承 ==========
class Animal:
    """动物基类"""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def speak(self):
        # 基类提供默认实现，但期望子类覆盖
        return "..."

    def introduce(self):
        return f"我是{self.name}，今年{self.age}岁"


class Dog(Animal):
    """狗：继承自 Animal"""

    def speak(self):
        # 覆盖父类方法
        return "汪汪！"

    def fetch(self):
        # 子类独有的方法
        return f"{self.name}去捡球了"


class Cat(Animal):
    """猫：继承自 Animal"""

    def speak(self):
        return "喵喵~"

    def climb(self):
        return f"{self.name}爬上树了"


# ========== 2. super() 用法 ==========
class Bird(Animal):
    """鸟：演示 super()"""

    def __init__(self, name, age, can_fly=True):
        # 先调用父类的 __init__
        super().__init__(name, age)
        # 再添加自己的属性
        self.can_fly = can_fly

    def speak(self):
        return "叽叽喳喳"

    def introduce(self):
        # 扩展父类方法
        base = super().introduce()
        fly_status = "会飞" if self.can_fly else "不会飞"
        return f"{base}，{fly_status}"


# ========== 3. 类方法和静态方法 ==========
class Vehicle:
    """交通工具基类"""
    total_count = 0  # 类属性

    def __init__(self, brand):
        self.brand = brand
        Vehicle.total_count += 1

    @classmethod
    def get_total(cls):
        # 类方法：可以访问类属性
        return f"总共有 {cls.total_count} 辆车"

    @staticmethod
    def is_valid_brand(brand):
        # 静态方法：不依赖类实例
        return len(brand) > 0


class ElectricCar(Vehicle):
    """电动车"""

    def __init__(self, brand, battery_capacity):
        super().__init__(brand)
        self.battery_capacity = battery_capacity

    def charge(self):
        return f"{self.brand} 正在充电，电池容量 {self.battery_capacity}kWh"


# ========== 4. 属性装饰器 ==========
class Person:
    def __init__(self, name):
        self._name = name  # 约定：单下划线表示"内部使用"
        self._age = 0

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError("年龄不能为负数")
        self._age = value


# ========== 5. 多继承 (MRO - 方法解析顺序) ==========
class Flyable:
    def fly(self):
        return "我在飞"

class Swimmable:
    def swim(self):
        return "我在游泳"

class Duck(Animal, Flyable, Swimmable):
    """鸭子：会叫、会飞、会游泳"""

    def speak(self):
        return "嘎嘎嘎"


# ========== 演示 ==========
if __name__ == "__main__":
    print("=== 基础继承 ===")
    dog = Dog("旺财", 3)
    cat = Cat("咪咪", 2)

    print(dog.introduce())  # 继承自 Animal
    print(dog.speak())      # Dog 自己的实现
    print(dog.fetch())      # Dog 独有的方法

    print(cat.introduce())
    print(cat.speak())
    print(cat.climb())

    print("\n=== super() ===")
    bird = Bird("小黄", 1, can_fly=True)
    print(bird.introduce())  # 扩展了父类方法

    penguin = Bird("企鹅", 2, can_fly=False)
    print(penguin.introduce())

    tank = Bird("坦克", 999, can_fly=False)
    print(tank.introduce())




    print("\n=== 类方法 / 静态方法 ===")
    car1 = ElectricCar("特斯拉", 75)
    car2 = ElectricCar("比亚迪", 82)
    car3 = ElectricCar("小米", 99)
    print(car3.charge())
    print(Vehicle.get_total())
    print(ElectricCar.get_total())
    print(Vehicle.is_valid_brand(""))

    print(car1.charge())
    print(Vehicle.get_total())  # 通过类调用
    print(ElectricCar.get_total())  # 通过子类调用
    print(Vehicle.is_valid_brand(""))  # False

    print("\n=== 属性装饰器 ===")
    person = Person("小明")
    person.age = 18  # 使用 setter
    print(f"{person.name}, {person.age}岁")
    # person.age = -1  # 会抛出 ValueError

    print("\n=== 多继承 ===")
    duck = Duck("唐老鸭", 5)
    print(duck.speak())   # Animal
    print(duck.fly())     # Flyable
    print(duck.swim())    # Swimmable

    print("\n=== MRO 方法解析顺序 ===")
    print(Duck.__mro__)  # 查看继承链

    print("\n=== isinstance 和 issubclass ===")
    print(f"duck 是 Animal 吗？{isinstance(duck, Animal)}")
    print(f"duck 是 Flyable 吗？{isinstance(duck, Flyable)}")
    print(f"Dog 是 Animal 的子类吗？{issubclass(Dog, Animal)}")
