from PySide6.QtWidgets import QApplication, QMessageBox, QGraphicsScene, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt, QTimer, QDateTime, QRect
import rc_res
import random
import sys

class Stats:
    def __init__(self):
        # 从文件中加载UI定义
        self.ui = QUiLoader().load('form.ui')

        # 初始化锁定状态
        self.locked = True  # 初始为锁定状态

        # 初始化错误状态
        self.error_occurred = False  # 初始无错误

        # 新增：硬件错误锁定状态
        self.hardware_error_locked = False  # 硬件错误导致的锁定

        # 初始化mode状态（True表示mode1，False表示mode2）
        self.current_mode = True  # 初始为mode1

        # 初始化Benchmark状态
        self.benchmark_mode = True  # 初始为Benchmark1（前基准）

        # 初始化声音状态
        self.listen_mode = True  # 初始为有声音

        # 初始化电源状态
        self.battery_mode = True  # 初始为有声音

        # 初始化数据队列相关变量
        self.data_queue = [None] * 100  # 存储100个数据的循环队列
        self.queue_start = 0  # 队列起始位置
        self.queue_size = 0   # 队列当前大小
        self.queue_next = 0   # 下一个要写入的位置
        self.current_display_index = -1  # 当前显示的数据索引
        self.last_measurement_index = -1  # 上一次测量数据的索引

        # 连续测量相关变量
        self.is_continuous_measuring = False  # 是否处于连续测量中
        self.continuous_timer = QTimer()  # 连续测量定时器
        self.continuous_timer.timeout.connect(self.continuous_measurement)  # 连接定时器信号
        self.continuous_measurement_interval = 500  # 连续测量间隔（毫秒）
        self.temp_measurement_data = None  # 临时测量数据（用于连续测量）
        self.temp_sequence_number = None  # 临时序列号（用于连续测量）

        # 休眠相关变量
        self.sleep_mode = False  # 是否处于休眠状态
        self.sleep_timer = QTimer()  # 休眠检测定时器
        self.sleep_timer.timeout.connect(self.check_sleep_condition)  # 连接定时器信号
        self.sleep_timeout = 300000  # 5分钟（300秒 = 300000毫秒）
        self.last_activity_time = QDateTime.currentMSecsSinceEpoch()  # 正确的初始化

        # 清除确认相关变量
        self.clear_confirmation_active = False  # 是否处于清除确认状态
        self.clear_confirmation_timer = QTimer()  # 清除确认定时器
        self.clear_confirmation_timer.setSingleShot(True)  # 单次触发
        self.clear_confirmation_timer.timeout.connect(self.clear_confirmation_timeout)  # 连接定时器信号
        self.clear_confirmation_timeout_duration = 3000  # 3秒确认超时
        self.pending_clear_index = -1  # 待清除的数据索引

        # 初始化QGraphicsView的场景
        self.scene = QGraphicsScene()
        self.ui.graphicsView_mode.setScene(self.scene)

        self.scene2 = QGraphicsScene()
        self.ui.graphicsView_benchmark.setScene(self.scene2)

        self.scene3 = QGraphicsScene()
        self.ui.graphicsView_listen.setScene(self.scene3)

        self.scene4 = QGraphicsScene()
        self.ui.graphicsView_battery.setScene(self.scene4)

        # 初始化警告图标的场景
        self.warning_scene = QGraphicsScene()
        self.ui.graphicsView_warning.setScene(self.warning_scene)

        # 加载图片
        self.pixmap_mode1 = QPixmap(":/image/mode1.png")
        self.pixmap_mode2 = QPixmap(":/image/mode2.png")
        self.pixmap_benchmark1 = QPixmap(":/image/Benchmark1.png")
        self.pixmap_benchmark2 = QPixmap(":/image/Benchmark2.png")
        self.pixmap_listen1 = QPixmap(":/image/listen1.png")
        self.pixmap_listen2 = QPixmap(":/image/listen2.png")
        self.pixmap_battery1 = QPixmap(":/image/battery1.png")
        self.pixmap_battery2 = QPixmap(":/image/battery2.png")
        self.pixmap_warning = QPixmap(":/image/warning.png")  # 警告图标

        # 初始状态：隐藏所有图片并清空场景
        self.clear_all_graphics_views()

        # 隐藏警告图标（初始状态）
        self.hide_warning()

        # 创建序号标签（左上角，字体较小）
        self.seq_label = QLabel(self.ui)
        self.seq_label.setGeometry(QRect(35, 65, 50, 60))  # 在左上角显示
        self.seq_label.setStyleSheet("font: 10pt \"Microsoft YaHei UI\"; color: black;")  # 减小到10pt
        self.seq_label.setText("")
        self.seq_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 创建清除确认提示标签（在屏幕中间，使用红色字体）
        self.clear_warning_label = QLabel(self.ui)
        self.clear_warning_label.setGeometry(QRect(10, 110, 220, 60))  # 在数据区域下方
        self.clear_warning_label.setStyleSheet("font: 8pt \"Microsoft YaHei UI\"; color: red; qproperty-alignment: AlignCenter;")
        self.clear_warning_label.setText("")
        self.clear_warning_label.setVisible(False)  # 初始隐藏
        self.clear_warning_label.setAlignment(Qt.AlignCenter)

        # 创建硬件错误提示标签（在屏幕中间，使用红色字体）
        self.hardware_error_label = QLabel(self.ui)
        self.hardware_error_label.setGeometry(QRect(10, 110, 220, 60))  # 在数据区域下方
        self.hardware_error_label.setStyleSheet("font: 10pt \"Microsoft YaHei UI\"; color: red; qproperty-alignment: AlignCenter; font-weight: bold;")
        self.hardware_error_label.setText("硬件错误，请按电源键重启")
        self.hardware_error_label.setVisible(False)  # 初始隐藏
        self.hardware_error_label.setAlignment(Qt.AlignCenter)

        # 修改数据标签的样式，使其居中显示，设置HTML内容居中
        self.ui.data.setStyleSheet("qproperty-alignment: AlignCenter;")  # 移除字体大小设置，使用HTML控制
        self.ui.label.setStyleSheet("")  # screen标签初始无边框

        # 连接信号和槽
        self.ui.Benchmark.clicked.connect(self.Benchmark)
        self.ui.clear.clicked.connect(self.clear)
        self.ui.listen.clicked.connect(self.listen)
        self.ui.mode.clicked.connect(self.mode)
        self.ui.open.clicked.connect(self.open)
        self.ui.plus.clicked.connect(self.plus)
        self.ui.start.clicked.connect(self.start)
        self.ui.subtract.clicked.connect(self.subtract)

        # 启动休眠检测定时器
        self.sleep_timer.start(1000)  # 每秒检查一次

    def clear_all_graphics_views(self):
        """清空所有graphicsView并隐藏"""
        self.scene.clear()
        self.scene2.clear()
        self.scene3.clear()
        self.scene4.clear()
        self.warning_scene.clear()

    def show_warning(self):
        """显示警告图标，并使其自适应放缩"""
        # 只在程序出错且不处于休眠状态且不处于锁定状态时显示警告
        if self.error_occurred and not self.sleep_mode and not self.locked:
            self.warning_scene.clear()
            if not self.pixmap_warning.isNull():
                # 将图片添加到场景
                self.warning_scene.addPixmap(self.pixmap_warning)

                # 设置graphicsView的缩放和滚动策略
                self.ui.graphicsView_warning.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.ui.graphicsView_warning.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

                # 使视图适应场景内容
                self.ui.graphicsView_warning.fitInView(self.warning_scene.itemsBoundingRect(), Qt.KeepAspectRatio)

                # 设置缩放变换锚点为中心
                self.ui.graphicsView_warning.setTransformationAnchor(self.ui.graphicsView_warning.ViewportAnchor.AnchorViewCenter)

                # 设置调整大小时的策略
                self.ui.graphicsView_warning.setResizeAnchor(self.ui.graphicsView_warning.ViewportAnchor.AnchorViewCenter)

                # 启用抗锯齿
                self.ui.graphicsView_warning.setRenderHints(QPainter.RenderHint.Antialiasing)

                self.ui.graphicsView_warning.setVisible(True)
                print("显示警告图标")
                # 如果扬声器开启，打印对应的sendAndReceive命令
                if self.listen_mode and not self.hardware_error_locked:
                    print("sendAndReceive(CMD_WARNING_SONG, sizeof(CMD_WARNING_SONG)); //扬声器播放")
        else:
            self.hide_warning()

    def hide_warning(self):
        """隐藏警告图标"""
        self.warning_scene.clear()
        self.ui.graphicsView_warning.setVisible(False)

    def show_hardware_error_message(self, show=True):
        """显示或隐藏硬件错误消息"""
        if show:
            self.hardware_error_label.setVisible(True)
            self.ui.data.setVisible(False)  # 隐藏正常数据
            self.seq_label.setVisible(False)  # 隐藏序号
            print("显示硬件错误消息：请按电源键重启")
        else:
            self.hardware_error_label.setVisible(False)
            self.ui.data.setVisible(True)  # 显示正常数据
            self.seq_label.setVisible(True)  # 显示序号

    def show_clear_warning(self, show=True):
        """显示或隐藏清除确认警告文字"""
        if show and not self.locked and not self.sleep_mode and not self.hardware_error_locked:
            print("drawChinese16x16(0, 110, charData, red)")
            self.clear_warning_label.setText("再次按下clear键确认删除")
            self.clear_warning_label.setVisible(True)
            print("显示清除确认提示")
        else:
            self.clear_warning_label.setText("")
            self.clear_warning_label.setVisible(False)
          # print("隐藏清除确认提示")

    def set_error(self, error_state=True):
        """设置错误状态并更新警告显示"""
        if error_state != self.error_occurred:  # 只有在状态改变时才更新
            self.error_occurred = error_state
            print(f"错误状态已{'设置' if error_state else '清除'}")

        # 更新警告显示
        self.show_warning()

    def clear_error(self):
        """清除错误状态"""
        self.set_error(False)

    def set_hardware_error_lock(self, lock_state=True):
        """设置硬件错误锁定状态"""
        if lock_state != self.hardware_error_locked:  # 只有在状态改变时才更新
            self.hardware_error_locked = lock_state
            print(f"硬件错误锁定状态已{'设置' if lock_state else '清除'}")

            if lock_state:
                # 进入硬件错误锁定状态
                self.enter_hardware_error_lock()
            else:
                # 退出硬件错误锁定状态
                self.exit_hardware_error_lock()

    def enter_hardware_error_lock(self):
        """进入硬件错误锁定状态"""
        print("进入硬件错误锁定状态，所有操作被禁用，请按电源键重启")

        # 停止所有正在进行的测量
        if self.is_continuous_measuring:
            self.stop_continuous_measurement()

        # 停止休眠检测
        self.sleep_timer.stop()

        # 显示硬件错误消息
        self.show_hardware_error_message(True)

        # 隐藏正常数据显示
        self.ui.data.setText("")
        self.seq_label.setText("")

        # 确保警告图标显示
        self.set_error(True)

        # 清空其他所有提示
        self.show_clear_warning(False)

        # 打印硬件错误信息
        print("硬件测量设备错误！系统已锁定，请按电源键重启")

    def exit_hardware_error_lock(self):
        """退出硬件错误锁定状态"""
        print("退出硬件错误锁定状态")

        # 隐藏硬件错误消息
        self.show_hardware_error_message(False)

        # 重新启动休眠检测
        self.sleep_timer.start(1000)

        # 清除错误状态
        self.clear_error()

    def show_current_image(self):
        """显示当前模式的图片到QGraphicsView"""
        if self.locked or self.sleep_mode or self.hardware_error_locked:
            return

        self.scene.clear()

        if self.current_mode:  # mode1
            pixmap = self.pixmap_mode1
        else:  # mode2
            pixmap = self.pixmap_mode2

        if not pixmap.isNull():
            self.scene.addPixmap(pixmap)
            self.ui.graphicsView_mode.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            mode_text = "当前模式: Mode1" if self.current_mode else "当前模式: Mode2"
            self.ui.graphicsView_mode.setToolTip(mode_text)

    def show_current_benchmark(self):
        """显示当前Benchmark模式的图片到graphicsView_benchmark"""
        if self.locked or self.sleep_mode or self.hardware_error_locked:
            return

        self.scene2.clear()

        if self.benchmark_mode:  # Benchmark1（前基准）
            pixmap = self.pixmap_benchmark1
        else:  # Benchmark2（后基准）
            pixmap = self.pixmap_benchmark2

        if not pixmap.isNull():
            self.scene2.addPixmap(pixmap)
            self.ui.graphicsView_benchmark.fitInView(self.scene2.itemsBoundingRect(), Qt.KeepAspectRatio)

    def show_current_listen(self):
        """显示当前listen模式的图片到graphicsView_listen"""
        if self.locked or self.sleep_mode or self.hardware_error_locked:
            return

        self.scene3.clear()

        if self.listen_mode:  # listen1
            pixmap = self.pixmap_listen1
        else:  # listen2
            pixmap = self.pixmap_listen2

        if not pixmap.isNull():
            self.scene3.addPixmap(pixmap)
            self.ui.graphicsView_listen.fitInView(self.scene3.itemsBoundingRect(), Qt.KeepAspectRatio)

    def show_current_battery(self):
        """显示当前battery模式的图片到graphicsView_battery"""
        if self.locked or self.sleep_mode or self.hardware_error_locked:
            return

        self.scene4.clear()

        if self.battery_mode:  # battery1
            pixmap = self.pixmap_battery1
        else:
            pixmap = self.pixmap_battery2

        if not pixmap.isNull():
            self.scene4.addPixmap(pixmap)
            self.ui.graphicsView_battery.fitInView(self.scene4.itemsBoundingRect(), Qt.KeepAspectRatio)

    def generate_measurement_data(self, apply_benchmark_adjustment=True):
        """生成测量数据，模拟可能的硬件错误，现在生成三个角度"""
        try:
            # 模拟随机硬件错误（1%的概率出错）
            if random.random() < 0.5:  # 1%概率出错
                raise Exception("硬件测量设备错误")

            # 生成随机数据
            length = round(random.uniform(5, 500), 1)
            angle1 = random.randint(0, 359)  # 第一个角度
            angle2 = random.randint(0, 359)  # 第二个角度
            angle3 = random.randint(0, 359)  # 第三个角度

            print(f"length = parseDistanceFromResponse(response, 13);//获取长度数据")
            print(f"Angle_computation(gyro_x_dps,gyro_y_dps,gyro_z_dps);// angle1(俯仰角)//angle2(横滚角)//angle3(偏航角)")
            print(f"displayMeasurementData(int seq_num, float length, int angle1, int angle2, int angle3)//屏幕显示数据")
            # 如果应用基准调整且当前为后基准模式，则长度增加15cm
            if apply_benchmark_adjustment and not self.benchmark_mode:
                length += 15.0

            return length, angle1, angle2, angle3  # 返回三个角度
        except Exception as e:
            # 设置硬件错误锁定状态
            self.set_hardware_error_lock(True)
            print(f"硬件测量错误: {e}")
            # 返回默认值
            return 0.0, 0, 0, 0  # 返回三个角度的默认值

    def update_display(self, temp_data=None):
        """更新数据显示：序号在左上角，其他数据居中，显示三个角度，长度使用大字体，角度使用小字体"""
        try:
            # 如果处于硬件错误锁定状态，不更新显示
            if self.hardware_error_locked:
                return

            if temp_data is not None:
                # temp_data 现在包含 (seq_num, length, angle1, angle2, angle3)
                seq_num, length, angle1, angle2, angle3 = temp_data
                # 左上角显示序号（字体较小）
                self.seq_label.setText(f"{seq_num:3d}")
                # 使用HTML格式显示，长度使用大字体(16pt)，角度使用小字体(12pt)
                display_text = f"""
                <div style="text-align: center;">
                    <span style="font-size: 16pt; font-weight: bold;">{length:6.1f}cm</span><br>
                    <span style="font-size: 12pt;">{angle1:3d}° {angle2:3d}° {angle3:3d}°</span>
                </div>
                """
                self.ui.data.setText(display_text)
            elif self.current_display_index == -1:
                self.seq_label.setText("")
                self.ui.data.setText("data")
            else:
                data_item = self.data_queue[self.current_display_index]
                if data_item:
                    # data_item 现在包含 (seq_num, length, angle1, angle2, angle3)
                    seq_num, length, angle1, angle2, angle3 = data_item
                    # 左上角显示序号（字体较小）
                    self.seq_label.setText(f"{seq_num:3d}")
                    # 使用HTML格式显示，长度使用大字体(16pt)，角度使用小字体(12pt)
                    display_text = f"""
                    <div style="text-align: center;">
                        <span style="font-size: 16pt; font-weight: bold;">{length:6.1f}cm</span><br>
                        <span style="font-size: 12pt;">{angle1:3d}° {angle2:3d}° {angle3:3d}°</span>
                    </div>
                    """
                    self.ui.data.setText(display_text)
                else:
                    self.seq_label.setText("")
                    self.ui.data.setText("")
        except Exception as e:
            # 软件显示错误，不设置错误状态，只打印信息
            print(f"显示更新出错: {e}")

    def get_next_sequence_number(self):
        """获取下一个序列号"""
        try:
            if self.queue_size == 0:
                return 1
            elif self.queue_size < 100:
                last_seq = self.data_queue[(self.queue_next - 1) % 100][0] if self.queue_next > 0 else 0
                return last_seq + 1
            else:
                return self.data_queue[self.queue_next][0]
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"获取序列号出错: {e}")
            return 1

    def update_activity_time(self):
        """更新活动时间"""
        self.last_activity_time = QDateTime.currentMSecsSinceEpoch()

    def check_sleep_condition(self):
        """检查是否需要进入休眠状态"""
        if self.locked or self.sleep_mode or self.hardware_error_locked:
            return

        current_time = QDateTime.currentMSecsSinceEpoch()
        time_since_last_activity = current_time - self.last_activity_time

        if time_since_last_activity >= self.sleep_timeout:
            print("5分钟内无按键操作，进入休眠状态")
            self.enter_sleep_mode()

    def enter_sleep_mode(self):
        """进入休眠状态"""
        if self.sleep_mode or self.hardware_error_locked:
            return

        self.sleep_mode = True

        # 隐藏非按键控件
        self.ui.graphicsView_mode.setVisible(False)
        self.ui.graphicsView_benchmark.setVisible(False)
        self.ui.graphicsView_battery.setVisible(False)
        self.ui.graphicsView_listen.setVisible(False)
        self.ui.graphicsView_warning.setVisible(False)  # 休眠时隐藏警告
        self.ui.data.setVisible(False)
        self.ui.label.setVisible(False)
        self.seq_label.setVisible(False)  # 隐藏序号标签
        self.clear_warning_label.setVisible(False)  # 休眠时隐藏清除警告
        self.hardware_error_label.setVisible(False)  # 休眠时隐藏硬件错误消息

        print("已进入休眠状态，只显示按键")

    def exit_sleep_mode(self):
        """退出休眠状态"""
        if not self.sleep_mode or self.hardware_error_locked:
            return

        self.sleep_mode = False

        # 显示所有控件
        self.ui.graphicsView_mode.setVisible(True)
        self.ui.graphicsView_benchmark.setVisible(True)
        self.ui.graphicsView_battery.setVisible(True)
        self.ui.graphicsView_listen.setVisible(True)
        self.ui.graphicsView_warning.setVisible(True)  # 警告控件的可见性由show_warning控制
        self.ui.data.setVisible(True)
        self.ui.label.setVisible(True)
        self.seq_label.setVisible(True)  # 显示序号标签
        # 清除警告标签的可见性由show_clear_warning控制
        # 硬件错误标签的可见性由show_hardware_error_message控制

        # 更新显示
        self.show_current_image()
        self.show_current_benchmark()
        self.show_current_listen()
        self.show_current_battery()
        self.update_display()
        self.show_warning()  # 退出休眠时显示警告（如果有错误）

        # 打印电池检查
        print("Check_battery()")
        print("drawpicture(170,5,graphicsView_battery,ILI9341_BLACK)//电池状态显示")

        print("已退出休眠状态")

    def handle_activity(self):
        """处理用户活动"""
        # 如果处于硬件错误锁定状态，只允许电源键操作
        if self.hardware_error_locked:
            print("硬件错误锁定状态，只有电源键可以操作")
            return False

        if self.sleep_mode:
            print("检测到活动，退出休眠状态")
            self.exit_sleep_mode()
            self.update_activity_time()
            return True

        self.update_activity_time()
        return False

    def mode(self):
        """切换图片模式"""
        # 如果处于硬件错误锁定状态，不执行任何操作
        if self.hardware_error_locked:
            print("硬件错误锁定状态，无法切换模式，请按电源键重启")
            return

        if self.locked:
            print("锁定状态，无法切换模式")
            return

        # 尝试执行操作，但软件错误不触发警告
        try:
            if self.handle_activity() and self.sleep_mode:
                return

            if self.is_continuous_measuring:
                self.stop_continuous_measurement()

            self.current_mode = not self.current_mode
            self.show_current_image()

            current_mode = "单次测量" if self.current_mode else "连续测量"
            print(f"toggle_measurement_mode();模式已切换到: {current_mode}")

            # 如果扬声器开启，打印对应的sendAndReceive命令
            if self.listen_mode:
                if self.current_mode:  # mode1
                    print("sendAndReceive(CMD_MODE1_SONG, sizeof(CMD_MODE1_SONG)); //扬声器播放")
                else:  # mode2
                    print("sendAndReceive(CMD_MODE2_SONG, sizeof(CMD_MODE2_SONG)); //扬声器播放")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"切换模式出错: {e}")

    def Benchmark(self):
        """切换Benchmark图片模式"""
        # 如果处于硬件错误锁定状态，不执行任何操作
        if self.hardware_error_locked:
            print("硬件错误锁定状态，无法切换基准，请按电源键重启")
            return

        if self.locked:
            print("锁定状态，无法切换基准")
            return

        # 尝试执行操作，但软件错误不触发警告
        try:
            if self.handle_activity() and self.sleep_mode:
                return

            self.benchmark_mode = not self.benchmark_mode
            self.show_current_benchmark()

            current_mode = "前基准" if self.benchmark_mode else "后基准"
            print(f"toggle_Benchmark();")
            print(f"测量基准已切换到: {current_mode}")

            # 如果扬声器开启，打印对应的sendAndReceive命令
            if self.listen_mode:
                if self.benchmark_mode:  # Benchmark1
                    print("sendAndReceive(CMD_BENCHMARK1_SONG, sizeof(CMD_BENCHMARK1_SONG)); //扬声器播放")
                else:  # Benchmark2
                    print("sendAndReceive(CMD_BENCHMARK2_SONG, sizeof(CMD_BENCHMARK2_SONG)); //扬声器播放")

            if self.is_continuous_measuring and self.temp_measurement_data:
                seq_num = self.temp_sequence_number
                length, angle1, angle2, angle3 = self.generate_measurement_data(apply_benchmark_adjustment=True)
                # 更新临时数据 - 现在包含三个角度
                self.temp_measurement_data = (seq_num, length, angle1, angle2, angle3)
                self.update_display(self.temp_measurement_data)
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"切换基准出错: {e}")

    def clear(self):
        """删除当前显示的数据，采用两次确认机制"""
        # 如果处于硬件错误锁定状态，不执行任何操作
        if self.hardware_error_locked:
            print("错误，请按电源键重启")
            return

        if self.locked:
            print("锁定状态，无法清除")
            return

        # 尝试执行操作，但软件错误不触发警告
        try:
            if self.handle_activity() and self.sleep_mode:
                return

            if self.is_continuous_measuring:
                self.stop_continuous_measurement()

            if self.queue_size == 0:
                print("队列为空，无法删除数据")
                return

            if self.current_display_index == -1:
                print("没有显示任何数据，无法删除")
                return

            # 检查是否已经处于清除确认状态
            if self.clear_confirmation_active:
                # 第二次按下clear，执行删除操作
                self.clear_confirmation_timer.stop()
                self.clear_confirmation_active = False

                # 如果扬声器开启，打印对应的sendAndReceive命令
                if self.listen_mode:
                    print("sendAndReceive(CMD_CLEAR_SONG, sizeof(CMD_CLEAR_SONG)); //扬声器播放")

                # 隐藏清除确认提示
                self.show_clear_warning(False)

                # 实际执行删除操作
                self.execute_clear()
            else:
                # 第一次按下clear，显示确认提示并启动定时器
                self.pending_clear_index = self.current_display_index
                self.clear_confirmation_active = True

                # 在屏幕上显示确认提示文字
                self.show_clear_warning(True)

                # 启动确认超时定时器
                self.clear_confirmation_timer.start(self.clear_confirmation_timeout_duration)

                print("第一次按下clear，显示确认提示，请再次按下clear确认删除")

        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"清除数据出错: {e}")
            # 确保重置清除确认状态
            self.clear_confirmation_active = False
            self.pending_clear_index = -1
            if hasattr(self, 'clear_confirmation_timer') and self.clear_confirmation_timer.isActive():
                self.clear_confirmation_timer.stop()
            # 隐藏清除确认提示
            self.show_clear_warning(False)

    def clear_confirmation_timeout(self):
        """清除确认超时处理"""
        if self.clear_confirmation_active:
            print("清除确认超时，取消删除操作")
            self.clear_confirmation_active = False
            self.pending_clear_index = -1

            # 隐藏清除确认提示
            self.show_clear_warning(False)

    def execute_clear(self):
        """实际执行删除操作"""
        try:
            print("clear()")
            print(f"删除数据，索引: {self.pending_clear_index}")

            if self.pending_clear_index == -1:
                print("无效的待删除索引")
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                return

            deleted_data = self.data_queue[self.pending_clear_index]
            if deleted_data:
                seq_num, length, angle1, angle2, angle3 = deleted_data
                print(f"删除的数据: 序号={seq_num}, 长度={length}cm, 角度1={angle1}°, 角度2={angle2}°, 角度3={angle3}°")

            self.data_queue[self.pending_clear_index] = None
            self.queue_size -= 1

            if self.queue_size == 0:
                self.current_display_index = -1
                self.last_measurement_index = -1
                self.queue_start = 0
                self.queue_next = 0
                self.update_display()
                print("clear()")
                print("队列已空")
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                return

            prev_index = (self.pending_clear_index - 1) % 100
            count = 0
            while self.data_queue[prev_index] is None and count < 100:
                prev_index = (prev_index - 1) % 100
                count += 1

            if self.data_queue[prev_index] is not None:
                self.current_display_index = prev_index
            else:
                next_index = (self.pending_clear_index + 1) % 100
                count = 0
                while self.data_queue[next_index] is None and count < 100:
                    next_index = (next_index + 1) % 100
                    count += 1

                if self.data_queue[next_index] is not None:
                    self.current_display_index = next_index
                else:
                    for i in range(100):
                        if self.data_queue[i] is not None:
                            self.current_display_index = i
                            break

            self.update_display()
            print(f"显示删除后的数据，索引: {self.current_display_index}")
            self.update_queue_start()
            self.clear_confirmation_active = False
            self.pending_clear_index = -1
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"执行清除数据出错: {e}")
            self.clear_confirmation_active = False
            self.pending_clear_index = -1
            # 隐藏清除确认提示
            self.show_clear_warning(False)

    def update_queue_start(self):
        """更新队列起始位置，确保指向第一个有效数据"""
        try:
            if self.queue_size == 0:
                self.queue_start = 0
                return

            for i in range(100):
                if self.data_queue[i] is not None:
                    self.queue_start = i
                    return
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"更新队列起始位置出错: {e}")

    def listen(self):
        """切换listen图片模式"""
        # 如果处于硬件错误锁定状态，不执行任何操作
        if self.hardware_error_locked:
            print("硬件错误锁定状态，无法切换声音，请按电源键重启")
            return

        if self.locked:
            print("锁定状态，无法切换声音")
            return

        # 尝试执行操作，但软件错误不触发警告
        try:
            if self.handle_activity() and self.sleep_mode:
                return

            self.listen_mode = not self.listen_mode
            self.show_current_listen()

            current_mode = "有声" if self.listen_mode else "无声"
            print(f"toggle_measurement_mode()")
            print(f"目前为: {current_mode}")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"切换声音模式出错: {e}")

    def open(self):
        """打开/关闭锁定状态，也是硬件错误时的重启键"""
        # 尝试执行操作，但软件错误不触发警告
        try:
            self.update_activity_time()

            # 如果处于硬件错误锁定状态，执行重启
            if self.hardware_error_locked:
                print("执行硬件错误重启...")
                # 清除硬件错误锁定状态
                self.set_hardware_error_lock(False)
                # 然后执行正常的解锁操作
                self.locked = False
                # 继续执行下面的解锁代码
                # 注意：这里不直接返回，让代码继续执行下面的解锁逻辑
            elif self.locked:
                # 解锁状态
                self.locked = False
                print("initializeMPU6050()")
                print("initializeJQ8900()")
                print("initialize_tftscreen()")
                print("initialize_PLS-K-100()")
                print("初始化完成")

                if self.is_continuous_measuring:
                    self.stop_continuous_measurement()

                # 重置清除确认状态
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                if hasattr(self, 'clear_confirmation_timer') and self.clear_confirmation_timer.isActive():
                    self.clear_confirmation_timer.stop()
                # 隐藏清除确认提示
                self.show_clear_warning(False)

                # 显示所有图片
                print("tft.fillScreen(ILI9341_WHITE);//背景显示")
                print("drawpicture(75,5,graphicsView_mode,ILI9341_BLACK)//模式显示")
                print("drawpicture(15,0,graphicsView_benchmark,ILI9341_BLACK)//基准显示")

                print("drawpicture(125,5,graphicsView_listen,ILI9341_BLACK)//声音状态显示")
                print("drawpicture(10,40,graphicsView_Border,ILI9341_BLACK)//边框显示")

                self.show_current_image()
                self.show_current_benchmark()
                self.show_current_listen()
                self.show_current_battery()
                self.show_warning()  # 显示警告（如果有错误）

                # 打印电池检查
                print("Check_battery()")
                print("drawpicture(170,5,graphicsView_battery,ILI9341_BLACK)//电池状态显示")
                print("图标显示成功")
                self.ui.data.setText("data")
                self.seq_label.setText("")

                # 添加圆角边框，保持HTML控制字体大小
                self.ui.data.setStyleSheet("qproperty-alignment: AlignCenter; border-style: solid; border-width: 2px; border-color: black; border-radius: 10px;")
                # screen标签也添加圆角边框
                self.ui.label.setStyleSheet("border-style: solid; border-width: 2px; border-color: black; border-radius: 10px;")
                # 序号标签样式，字体为10pt
                self.seq_label.setStyleSheet("font: 10pt \"Microsoft YaHei UI\"; color: black;")
                # 清除警告标签样式
                self.clear_warning_label.setStyleSheet("font: 12pt \"Microsoft YaHei UI\"; color: red; qproperty-alignment: AlignCenter;")
            else:
                # 锁定状态
                self.locked = True
                print("关闭仪器，无法操作")

                if self.is_continuous_measuring:
                    self.stop_continuous_measurement()

                # 重置清除确认状态
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                if hasattr(self, 'clear_confirmation_timer') and self.clear_confirmation_timer.isActive():
                    self.clear_confirmation_timer.stop()
                # 隐藏清除确认提示
                self.show_clear_warning(False)

                self.clear_all_graphics_views()
                self.hide_warning()  # 锁定状态隐藏警告
                self.clear_error()   # 锁定状态清除错误状态
                self.set_hardware_error_lock(False)  # 锁定状态清除硬件错误锁定

                self.current_mode = True
                self.benchmark_mode = True
                self.listen_mode = True

                self.data_queue = [None] * 100
                self.queue_start = 0
                self.queue_size = 0
                self.queue_next = 0
                self.current_display_index = -1
                self.last_measurement_index = -1

                self.is_continuous_measuring = False
                self.temp_measurement_data = None
                self.temp_sequence_number = None

                self.ui.data.setText("")
                self.seq_label.setText("")
                self.clear_warning_label.setText("")
                self.hardware_error_label.setText("")
                self.ui.data.setStyleSheet("qproperty-alignment: AlignCenter;")
                self.ui.label.setStyleSheet("")
                self.seq_label.setStyleSheet("font: 10pt \"Microsoft YaHei UI\"; color: black;")
                self.clear_warning_label.setStyleSheet("font: 12pt \"Microsoft YaHei UI\"; color: red; qproperty-alignment: AlignCenter;")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"切换锁定状态出错: {e}")

    def plus(self):
        """选择上一个数据"""
        # 如果处于硬件错误锁定状态，不执行任何操作
        if self.hardware_error_locked:
            print("硬件错误锁定状态，无法操作，请按电源键重启")
            return

        if self.locked:
            print("锁定状态，无法操作")
            return

        # 尝试执行操作，但软件错误不触发警告
        try:
            if self.handle_activity() and self.sleep_mode:
                return

            # 如果处于清除确认状态，取消确认
            if self.clear_confirmation_active:
                self.clear_confirmation_timer.stop()
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                self.show_clear_warning(False)
                print("清除确认已取消")

            if self.is_continuous_measuring:
                self.stop_continuous_measurement()

            # 如果扬声器开启，打印对应的sendAndReceive命令
            if self.listen_mode:
                print("sendAndReceive(CMD_PLUS_SONG, sizeof(CMD_PLUS_SONG)); //扬声器播放")

            if self.queue_size == 0:
                print("队列为空，无法选择数据")
                return

            if self.current_display_index == -1:
                self.current_display_index = (self.queue_next - 1) % 100
            else:
                prev_index = (self.current_display_index - 1) % 100
                count = 0
                while self.data_queue[prev_index] is None and count < 100:
                    prev_index = (prev_index - 1) % 100
                    count += 1

                if self.data_queue[prev_index] is not None:
                    self.current_display_index = prev_index

            self.update_display()
            print(f"subtract()")
            print(f"显示上一个数据，索引: {self.current_display_index}")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"选择上一个数据出错: {e}")

    def start(self):
        """开始/停止测量"""
        # 如果处于硬件错误锁定状态，不执行任何操作
        if self.hardware_error_locked:
            print("硬件错误锁定状态，无法开始，请按电源键重启")
            return

        if self.locked:
            print("锁定状态，无法开始")
            return

        # 尝试执行操作，但软件错误不触发警告
        try:
            if self.handle_activity() and self.sleep_mode:
                return

            # 如果处于清除确认状态，取消确认
            if self.clear_confirmation_active:
                self.clear_confirmation_timer.stop()
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                self.show_clear_warning(False)
                print("清除确认已取消")

            # 如果扬声器开启，打印对应的sendAndReceive命令
            if self.listen_mode:
                print("sendAndReceive(CMD_START_SONG, sizeof(CMD_START_SONG)); //扬声器播放")

            if self.current_mode:
                self.single_measurement()
            else:
                if self.is_continuous_measuring:
                    self.stop_continuous_measurement()
                else:
                    self.start_continuous_measurement()
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"开始/停止测量出错: {e}")

    def single_measurement(self):
        """单次测量"""
        # 尝试执行操作，但软件错误不触发警告
        try:
            # 如果处于清除确认状态，取消确认
            if self.clear_confirmation_active:
                self.clear_confirmation_timer.stop()
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                self.show_clear_warning(False)
                print("清除确认已取消")

            # 打印单次测量串口命令
            print("send_serial(baudrate=115200, char='r') //单次测量指令")
            print("const uint8_t cmd[] = {0xAA, 0x00, 0x00, 0x20, 0x00, 0x01, 0x00, 0x00, 0x21}; //单次测量指令")
            print("uart2.write(cmd, sizeof(cmd));")
            # 现在获取三个角度
            length, angle1, angle2, angle3 = self.generate_measurement_data(apply_benchmark_adjustment=True)

            # 如果硬件错误锁定状态已设置，直接返回
            if self.hardware_error_locked:
                return

            seq_num = self.get_next_sequence_number()

            # 存储数据 - 现在包含三个角度
            self.data_queue[self.queue_next] = (seq_num, length, angle1, angle2, angle3)

            print(f"单次测量 - 存储数据: 序号={seq_num}, 长度={length}cm, 角度1={angle1}°, 角度2={angle2}°, 角度3={angle3}°")

            if self.queue_size < 100:
                self.queue_size += 1

            self.last_measurement_index = self.queue_next
            self.queue_next = (self.queue_next + 1) % 100

            if self.queue_size == 100:
                self.queue_start = (self.queue_start + 1) % 100

            self.current_display_index = self.last_measurement_index
            self.update_display()

            print(f"队列状态: 大小={self.queue_size}, 下一个位置={self.queue_next}, 起始位置={self.queue_start}")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"单次测量出错: {e}")

    def start_continuous_measurement(self):
        """开始连续测量"""
        # 尝试执行操作，但软件错误不触发警告
        try:
            # 如果处于清除确认状态，取消确认
            if self.clear_confirmation_active:
                self.clear_confirmation_timer.stop()
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                self.show_clear_warning(False)
                print("清除确认已取消")

            print("开始连续测量...")
            # 打印开始连续测量串口命令
            print("send_serial(baudrate=115200, char='c') //连续测量开始指令")
            print("const uint8_t cmd[] = {0xAA, 0x00, 0x00, 0x20, 0x00, 0x01, 0x00, 0x06, 0x27}; //连续测量开始指令")
            print("uart2.write(cmd, sizeof(cmd));")
            self.temp_sequence_number = self.get_next_sequence_number()
            # 生成三个角度
            length, angle1, angle2, angle3 = self.generate_measurement_data(apply_benchmark_adjustment=True)

            # 如果硬件错误锁定状态已设置，直接返回
            if self.hardware_error_locked:
                return

            # 临时数据现在包含三个角度
            self.temp_measurement_data = (self.temp_sequence_number, length, angle1, angle2, angle3)

            self.update_display(self.temp_measurement_data)

            self.is_continuous_measuring = True
            self.continuous_timer.start(self.continuous_measurement_interval)

            print(f"连续测量开始，临时序号: {self.temp_sequence_number}, 角度1={angle1}°, 角度2={angle2}°, 角度3={angle3}°")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"开始连续测量出错: {e}")

    def stop_continuous_measurement(self):
        """停止连续测量并保存数据"""
        # 尝试执行操作，但软件错误不触发警告
        try:
            # 如果处于清除确认状态，取消确认
            if self.clear_confirmation_active:
                self.clear_confirmation_timer.stop()
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                self.show_clear_warning(False)
                print("清除确认已取消")

            print("停止连续测量并保存数据...")
            # 打印停止连续测量串口命令
            print("send_serial(baudrate=115200, char='s') //连续测量停止指令")
            print("uart2.write(0x58); //连续测量停止指令")
            self.continuous_timer.stop()
            self.is_continuous_measuring = False

            if self.temp_measurement_data:
                # 现在获取五个值
                seq_num, length, angle1, angle2, angle3 = self.temp_measurement_data

                # 保存数据 - 包含三个角度
                self.data_queue[self.queue_next] = (seq_num, length, angle1, angle2, angle3)
                print(f"连续测量 - 保存数据: 序号={seq_num}, 长度={length}cm, 角度1={angle1}°, 角度2={angle2}°, 角度3={angle3}°")

                if self.queue_size < 100:
                    self.queue_size += 1

                self.last_measurement_index = self.queue_next
                self.queue_next = (self.queue_next + 1) % 100

                if self.queue_size == 100:
                    self.queue_start = (self.queue_start + 1) % 100

                self.current_display_index = self.last_measurement_index
                self.update_display()

                self.temp_measurement_data = None
                self.temp_sequence_number = None

                print(f"队列状态: 大小={self.queue_size}, 下一个位置={self.queue_next}, 起始位置={self.queue_start}")
            else:
                print("没有测量数据可保存")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"停止连续测量出错: {e}")

    def continuous_measurement(self):
        """连续测量定时器回调函数"""
        # 尝试执行操作，但软件错误不触发警告
        try:
            if not self.is_continuous_measuring:
                return

            # 生成三个角度
            length, angle1, angle2, angle3 = self.generate_measurement_data(apply_benchmark_adjustment=True)

            # 如果硬件错误锁定状态已设置，停止连续测量
            if self.hardware_error_locked:
                self.stop_continuous_measurement()
                return

            # 更新临时数据 - 包含三个角度
            self.temp_measurement_data = (self.temp_sequence_number, length, angle1, angle2, angle3)

            self.update_display(self.temp_measurement_data)

            print(f"连续测量刷新: 序号={self.temp_sequence_number}, 长度={length}cm, 角度1={angle1}°, 角度2={angle2}°, 角度3={angle3}°")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"连续测量过程出错: {e}")

    def subtract(self):
        """选择下一个数据"""
        # 如果处于硬件错误锁定状态，不执行任何操作
        if self.hardware_error_locked:
            print("硬件错误锁定状态，无法操作，请按电源键重启")
            return

        if self.locked:
            print("锁定状态，无法操作")
            return

        # 尝试执行操作，但软件错误不触发警告
        try:
            if self.handle_activity() and self.sleep_mode:
                return

            # 如果处于清除确认状态，取消确认
            if self.clear_confirmation_active:
                self.clear_confirmation_timer.stop()
                self.clear_confirmation_active = False
                self.pending_clear_index = -1
                self.show_clear_warning(False)
                print("清除确认已取消")

            if self.is_continuous_measuring:
                self.stop_continuous_measurement()

            # 如果扬声器开启，打印对应的sendAndReceive命令
            if self.listen_mode:
                print("sendAndReceive(CMD_SUBTRACT_SONG, sizeof(CMD_SUBTRACT_SONG)); //扬声器播放")

            if self.queue_size == 0:
                print("队列为空，无法选择数据")
                return

            if self.current_display_index == -1:
                self.current_display_index = self.queue_start
            else:
                next_index = (self.current_display_index + 1) % 100
                count = 0
                while self.data_queue[next_index] is None and count < 100:
                    next_index = (next_index + 1) % 100
                    count += 1

                if self.data_queue[next_index] is not None:
                    self.current_display_index = next_index

            self.update_display()
            print(f"plus()")
            print(f"显示下一个数据，索引: {self.current_display_index}")
        except Exception as e:
            # 软件错误，不设置错误状态，只打印信息
            print(f"选择下一个数据出错: {e}")

app = QApplication(sys.argv)
stats = Stats()
stats.ui.show()
sys.exit(app.exec())
