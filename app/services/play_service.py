import platform
import pyautogui
from app.models.action import Action
import concurrent.futures
import threading
from app.cores.config import config

class PlayService:

    def __init__(self):
        self.input_lock = threading.Lock()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, 
                                                           thread_name_prefix='key_processor')
        self.future = None
        self.last_action:Action = None
        self.system = platform.system().lower()  # 获取操作系统类型
        self.sleep_event = threading.Event()  # 添加事件对象
        self.is_shutdown = False
        self.ARROW_KEYS = ('a', 'w', 's', 'd', 'up', 'down', 'left', 'right')

    def processKeys(self, action: Action):
        """处理按键输入"""
        if not action.keys:
            return
        
        for actionKey in action.keys:
            if not actionKey.key:
                continue
            if actionKey.key in self.ARROW_KEYS:
                actionKey.duration = actionKey.duration or 3
            else:
                 actionKey.duration = actionKey.duration or 0.1

        self.last_action = action
        self.last_action.count = 0

        print("触发动作：", action.model_dump_json(), '\n')

        if not config.input['is_enable']:
            return

        for actionKey in action.keys:
            try:
                if not actionKey.key:
                    continue

                # 方向键处理
                if actionKey.key in self.ARROW_KEYS:
                    self._handle_arrow_key(actionKey.key, actionKey.duration)

                # 鼠标点击操作
                if actionKey.key.startswith("mouse_"):
                    self._handle_mouse_action(actionKey.key, actionKey.duration)
                
                # 组合键处理
                elif "+" in actionKey.key:
                    self._handle_combo_key(actionKey.key, actionKey.duration)
                
                # 小键盘处理
                elif actionKey.key.startswith("num"):
                    self._handle_numpad_key(actionKey.key, actionKey.duration)
                
                # 特殊功能键处理
                elif actionKey.key in ("win", "cmd", "menu", "printscreen", "scrolllock", "pause"):
                    self._handle_special_key(actionKey.key, actionKey.duration)
                
                # 普通按键处理(包括方向键、功能键、多媒体键等)
                else:
                    pyautogui.keyDown(actionKey.key)
                    self.sleep_event.wait(actionKey.duration)
                    pyautogui.keyUp(actionKey.key)
                    
            except Exception as e:
                print(f"按键操作失败: {e}")

    def _handle_arrow_key(self, key: str, duration: float):
        """处理方向键"""
        pyautogui.keyDown(key)
        self.sleep_event.wait(duration)
        pyautogui.keyUp(key)
        
    def _handle_mouse_action(self, key: str, duration: float):
        """处理鼠标相关操作"""
        if key == "mouse_left":
            pyautogui.mouseDown(button='left')
            self.sleep_event.wait(duration)
            pyautogui.mouseUp(button='left')
        elif key == "mouse_right":
            pyautogui.mouseDown(button='right')
            self.sleep_event.wait(duration)
            pyautogui.mouseUp(button='right')
        elif key == "mouse_middle":
            pyautogui.mouseDown(button='middle')
            self.sleep_event.wait(duration)
            pyautogui.mouseUp(button='middle')
        elif key == "mouse_double_left":
            pyautogui.doubleClick(button='left', duration=duration)
        elif key == "mouse_double_right":
            pyautogui.doubleClick(button='right', duration=duration)
        elif key == "mouse_scroll_up":
            pyautogui.scroll(10)
        elif key == "mouse_scroll_down":
            pyautogui.scroll(-10)
        elif key.startswith("mouse_move_"):
            direction = key.split("_")[-1]
            move_distance = 50
            if direction == "up":
                pyautogui.moveRel(0, -move_distance, duration=duration)
            elif direction == "down":
                pyautogui.moveRel(0, move_distance, duration=duration)
            elif direction == "left":
                pyautogui.moveRel(-move_distance, 0, duration=duration)
            elif direction == "right":
                pyautogui.moveRel(move_distance, 0, duration=duration)
        elif key.startswith("mouse_drag_"):
            parts = key.split("_")
            if len(parts) >= 4:
                try:
                    button = parts[-2]
                    distance = int(parts[-1])
                    direction = parts[-3] if len(parts) >= 5 else "right"
                    
                    pyautogui.mouseDown(button=button)
                    self.sleep_event.wait(duration/2)  # 分配一半时间给拖拽过程
                    
                    if direction == "up":
                        pyautogui.moveRel(0, -distance, duration=duration/2)
                    elif direction == "down":
                        pyautogui.moveRel(0, distance, duration=duration/2)
                    elif direction == "left":
                        pyautogui.moveRel(-distance, 0, duration=duration/2)
                    else:  # right
                        pyautogui.moveRel(distance, 0, duration=duration/2)
                        
                    pyautogui.mouseUp(button=button)
                except ValueError:
                    print(f"Invalid drag distance: {parts[-1]}")

    def _handle_combo_key(self, key: str, duration: float):
        """处理组合键"""
        keys = key.split("+")
        # 按下所有修饰键
        for k in keys[:-1]:
            pyautogui.keyDown(k)
        # 按下最后一个键并保持指定时长
        pyautogui.keyDown(keys[-1])
        self.sleep_event.wait(duration)
        # 释放最后一个键
        pyautogui.keyUp(keys[-1])
        # 释放所有修饰键
        for k in reversed(keys[:-1]):
            pyautogui.keyUp(k)

    def _handle_numpad_key(self, key: str, duration: float):
        """处理小键盘按键"""
        if key == "numlock":
            pyautogui.keyDown('numlock')
            self.sleep_event.wait(duration)
            pyautogui.keyUp('numlock')
        else:
            num_key = f'numpad{key.replace("num", "")}'
            pyautogui.keyDown(num_key)
            self.sleep_event.wait(duration)
            pyautogui.keyUp(num_key)

    def _handle_special_key(self, key: str, duration: float):
        """处理特殊功能键"""
        # 根据操作系统类型选择映射
        if self.system == 'darwin':  # macOS
            key_mapping = {
                'win': 'command',
                'cmd': 'command',
                'menu': 'apps',
                'printscreen': 'command+shift+3',  # macOS 截图快捷键
                'scrolllock': 'fn+k',
                'pause': 'pause'
            }
        elif self.system == 'windows':  # Windows
            key_mapping = {
                'win': 'winleft',
                'cmd': 'winleft',
                'menu': 'apps',
                'printscreen': 'printscreen',
                'scrolllock': 'scrolllock',
                'pause': 'pause'
            }
        else:  # Linux 或其他系统
            key_mapping = {
                'win': 'super',
                'cmd': 'super',
                'menu': 'menu',
                'printscreen': 'print_screen',
                'scrolllock': 'scroll_lock',
                'pause': 'pause'
            }

        mapped_key = key_mapping.get(key, key)

        # 处理组合键情况(如 macOS 的截图键)
        if '+' in mapped_key:
            self._handle_combo_key(mapped_key, duration)
        else:
            pyautogui.keyDown(mapped_key)
            self.sleep_event.wait(duration)
            pyautogui.keyUp(mapped_key)

    def processAction(self, action: Action) -> None:
        """处理单个动作"""
        with self.input_lock:
            self.processKeys(action)

    def processActionSync(self, action: Action) -> concurrent.futures.Future:
        """异步处理动作"""

        if self.is_shutdown:
            return

        if (self.last_action and 
            self.last_action.name == action.name and 
            self.future and 
            not self.future.done()):
            self.last_action.count += 1
            return self.future
            
        if self.future and not self.future.done():
            self.sleep_event.set()  # 设置事件来唤醒等待中的线程
            self.future.cancel()
        
        self.sleep_event.clear()  # 重置事件状态
        self.future = self.executor.submit(self.processAction, action)
        
        return self.future

    def shutdown(self):
        self.is_shutdown = True
        if self.future and not self.future.done():
            self.sleep_event.set()
            self.future.cancel()
        self.executor.shutdown(wait=True)

play_service = PlayService()