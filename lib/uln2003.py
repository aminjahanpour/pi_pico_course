from machine import Pin
from time import sleep_ms

# 定义高低电平
LOW = 0
HIGH = 1

# 全步步序表（4步）
FULL_STEPS = [
    [ LOW,  LOW, HIGH, HIGH],  # Step 1
    [ LOW, HIGH, HIGH,  LOW],  # Step 2
    [HIGH, HIGH,  LOW,  LOW],  # Step 3
    [HIGH,  LOW,  LOW, HIGH],  # Step 4
]

# 半步步序表（8步）
HALF_STEPS = [
    [ LOW,  LOW,  LOW, HIGH],  # Step 1
    [ LOW,  LOW, HIGH, HIGH],  # Step 2
    [ LOW,  LOW, HIGH,  LOW],  # Step 3
    [ LOW, HIGH, HIGH,  LOW],  # Step 4
    [ LOW, HIGH,  LOW,  LOW],  # Step 5
    [HIGH, HIGH,  LOW,  LOW],  # Step 6
    [HIGH,  LOW,  LOW,  LOW],  # Step 7
    [HIGH,  LOW,  LOW, HIGH],  # Step 8
]

class Stepper:
    """
    控制28BYJ-48步进电机的类。
    支持半步模式和全步模式，并提供多种旋转方式。
    """
    
    def __init__(self, pin1, pin2, pin3, pin4, mode='HALF', delay=None):
        """
        初始化步进电机控制器。
        
        :param pin1, pin2, pin3, pin4: 连接到ULN2003驱动板的GPIO引脚。
        :param mode: 步进模式，可以是 'HALF' 或 'FULL'。
                     - 'HALF': 半步模式，每圈4096步。
                     - 'FULL': 全步模式，每圈2048步。
        :param delay: 每步之间的延迟时间（毫秒）。
                     - 默认为2ms（半步模式）或4ms（全步模式）。
        """
        self.pin1 = pin1
        self.pin2 = pin2
        self.pin3 = pin3
        self.pin4 = pin4
        
        # 将模式转换为大写以避免大小写问题
        mode = mode.upper()
        if mode == 'FULL':
            self.steps = FULL_STEPS  # 使用全步步序表
            self.delay = 4 if not delay else delay  # 默认延迟4ms
        elif mode == 'HALF':
            self.steps = HALF_STEPS  # 使用半步步序表
            self.delay = 2 if not delay else delay  # 默认延迟2ms
        else:
            raise ValueError('Invalid Mode Value! The value can only be "HALF" or "FULL"!')
        
        # 计算每圈的步数和每步的角度
        self.mode = mode
        self.steps_per_circle = 2048 if self.mode == 'FULL' else 4096  # 每圈的步数
        self.angle_per_step = 360 / self.steps_per_circle  # 每步对应的角度
        
        self.step_count = 0  # 当前步数计数器，用于记录电机的当前位置
    
    def step(self):
        """
        执行一步前进操作。
        根据当前步数计数器的值，从步序表中获取对应的信号状态，并驱动电机向前移动一步。
        """
        # 获取当前步的信号状态
        value1, value2, value3, value4 = self.steps[self.step_count % len(self.steps)]
        self.pin1.value(value1)
        self.pin2.value(value2)
        self.pin3.value(value3)
        self.pin4.value(value4)
        self.step_count += 1  # 更新步数计数器
        sleep_ms(self.delay)  # 延迟以控制速度
    
    def back_step(self):
        """
        执行一步后退操作。
        根据当前步数计数器的值，从步序表中获取对应的信号状态，并驱动电机向后移动一步。
        """
        # 获取当前步的信号状态
        value1, value2, value3, value4 = self.steps[self.step_count % len(self.steps)]
        self.pin1.value(value1)
        self.pin2.value(value2)
        self.pin3.value(value3)
        self.pin4.value(value4)
        self.step_count -= 1  # 更新步数计数器
        sleep_ms(self.delay)  # 延迟以控制速度
    
    def rotate_by_steps(self, steps):
        """
        按指定步数旋转电机。
        
        :param steps: 正值表示前进，负值表示后退。
        根据步数的正负性选择调用 `step` 或 `back_step` 方法。
        """
        step_func = self.step if steps > 0 else self.back_step
        for _ in range(abs(steps)):
            step_func()
    
    def rotate_by_angle(self, angle):
        """
        按指定角度旋转电机。
        
        :param angle: 正值表示顺时针，负值表示逆时针。支持浮点数。
        将角度转换为步数后调用 `rotate_by_steps` 方法。
        """
        steps = int(angle / self.angle_per_step)  # 将角度转换为步数
        self.rotate_by_steps(steps)
    
    def rotate_by_circles(self, circles):
        """
        按指定圈数旋转电机。
        
        :param circles: 正值表示顺时针，负值表示逆时针。支持浮点数。
        将圈数转换为步数后调用 `rotate_by_steps` 方法。
        """
        steps = int(circles * self.steps_per_circle)  # 将圈数转换为步数
        self.rotate_by_steps(steps)

    def set_current_as_home(self):
        """
        将当前位置设置为零位。
        将当前步数计数器的值重置为0，表示当前位置为零位。
        """
        self.step_count = 0
    
    def go_home(self):
        """
        回归到之前设置的零位。
        根据当前步数计数器与零位的差值计算需要移动的步数，并调用 `rotate_by_steps` 方法。
        """
        self.rotate_by_steps(-self.step_count)
        
if __name__ == '__main__':
    # 初始化GPIO引脚
    pin1 = Pin(5, Pin.OUT)
    pin2 = Pin(6, Pin.OUT)
    pin3 = Pin(7, Pin.OUT)
    pin4 = Pin(8, Pin.OUT)
    
    # 创建步进电机实例（默认半步模式）
    stepper = Stepper(pin1, pin2, pin3, pin4)
    
    # 示例：按角度旋转
    stepper.rotate_by_angle(-180)  # 逆时针旋转180度
    
    # 设置当前位置为零位
    stepper.set_current_as_home()
    
    # 再次旋转
    stepper.rotate_by_angle(90)  # 顺时针旋转90度
    
    # 回归零位
    stepper.go_home()
