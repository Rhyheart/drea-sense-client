import platform
import keyboard
import mouse
from app.models.action import Action
import concurrent.futures
import threading
from app.cores.config import config
if platform.system().lower() == 'windows':
    import win32api
    import win32con
import time

class PlayService:

    def __init__(self):
        self.input_lock = threading.Lock()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, 
                                                           thread_name_prefix='key_processor')
        self.future = None
        self.last_action:Action = None
        self.last_action_count = 0
        self.system = platform.system().lower()  # 获取操作系统类型
        self.sleep_event = threading.Event()  # 添加事件对象
        self.is_shutdown = False
        self.MOUSE_SENSITIVITY = 20  # 鼠标灵敏度
        self.is_countinue = False

    def processKeys(self, action: Action):
        """处理按键输入"""
        if not action.keys:
            return
        
        self.is_countinue = True
        self.last_action = action
        self.last_action.count = self.last_action_count

        print("触发动作：", action.model_dump_json(), '\n')

        if not config.input['is_enable']:
            return

        for actionKey in action.keys:
            try:
                if not actionKey.key:
                    continue
                
                for _ in range(actionKey.count):

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
                        keyboard.press(actionKey.key)
                        self.wait(actionKey.duration)
                        keyboard.release(actionKey.key)
                    
            except Exception as e:
                print(f"按键操作失败: {e}")

    def _handle_arrow_key(self, key: str, duration: float):
        """处理方向键"""
        keyboard.press(key)
        self.wait(duration)
        keyboard.release(key)
        
    def _handle_mouse_action(self, key: str, duration: float):
        """处理鼠标相关操作"""
        if key == "mouse_left":
            mouse.press(button='left')
            self.wait(duration)
            mouse.release(button='left')
        elif key == "mouse_right":
            mouse.press(button='right')
            self.wait(duration)
            mouse.release(button='right')
        elif key == "mouse_middle":
            mouse.press(button='middle')
            self.wait(duration)
            mouse.release(button='middle')
        elif key == "mouse_double_left":
            mouse.double_click(button='left')
        elif key == "mouse_double_right":
            mouse.double_click(button='right')
        elif key == "mouse_scroll_up":
            mouse.wheel(delta=1)
        elif key == "mouse_scroll_down":
            mouse.wheel(delta=-1)
        elif key.startswith("mouse_move_") or key.startswith("mouse_drag_"):
            if platform.system().lower() != 'windows':#TODO: 其他系统需要另外支持
                return

            is_drag = key.startswith("mouse_drag_")
            direction = key.split("_")[-1]
            
            if is_drag:
                mouse.press(button='left')
            
            start_time = time.time()
            while time.time() - start_time < duration:
                if self.sleep_event.is_set():
                    break
                if direction == "up":
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -self.MOUSE_SENSITIVITY*2, 0, 0)
                elif direction == "down":
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, self.MOUSE_SENSITIVITY*2, 0, 0)
                elif direction == "left":
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -self.MOUSE_SENSITIVITY, 0, 0, 0)
                elif direction == "right":
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, self.MOUSE_SENSITIVITY, 0, 0, 0)
                time.sleep(0.01)
            
            if is_drag:
                mouse.release(button='left')

    def _handle_combo_key(self, key: str, duration: float):
        """处理组合键"""
        keys = key.split("+")
        # 按下所有修饰键
        for k in keys:
            keyboard.press(k)
        self.wait(duration)
        # 释放所有按键
        for k in reversed(keys):
            keyboard.release(k)

    def _handle_numpad_key(self, key: str, duration: float):
        """处理小键盘按键"""
        if key == "numlock":
            keyboard.press('num lock')
            self.wait(duration)
            keyboard.release('num lock')
        else:
            num_key = key.replace("num", "")
            keyboard.press(num_key)
            self.wait(duration)
            keyboard.release(num_key)

    def _handle_special_key(self, key: str, duration: float):
        """处理特殊功能键"""
        if self.system == 'darwin':  # macOS
            key_mapping = {
                'win': 'command',
                'cmd': 'command',
                'menu': 'apps',
                'printscreen': 'command+shift+3',
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
        else:
            key_mapping = {
                'win': 'super',
                'cmd': 'super',
                'menu': 'menu',
                'printscreen': 'print_screen',
                'scrolllock': 'scroll_lock',
                'pause': 'pause'
            }

        mapped_key = key_mapping.get(key, key)

        if '+' in mapped_key:
            self._handle_combo_key(mapped_key, duration)
        else:
            keyboard.press(mapped_key)
            self.wait(duration)
            keyboard.release(mapped_key)

    def wait(self, duration: float):
        while self.is_countinue:
            self.is_countinue = False
            self.sleep_event.wait(duration)
    
    def processAction(self, action: Action) -> None:
        """处理单个动作"""
        with self.input_lock:
            self.processKeys(action)

    def processActionSync(self, action: Action) -> concurrent.futures.Future:
        """异步处理动作"""

        if self.is_shutdown:
            return

        # 如果上一个动作和当前动作相同，则增加计数
        if (self.last_action):
            if(self.last_action.name == action.name):
                self.last_action_count += 1
                if(self.future and not self.future.done()):
                    self.is_countinue = True
                    return self.future
            else:
                self.last_action_count = 0
        
        # 如果上一个动作和当前动作不同，则取消上一个动作
        if self.future and not self.future.done():
            self.is_countinue = False
            self.sleep_event.set()
            self.future.cancel()
        
        self.sleep_event.clear()
        self.future = self.executor.submit(self.processAction, action)
        
        return self.future

    def shutdown(self):
        self.is_shutdown = True
        if self.future and not self.future.done():
            self.sleep_event.set()
            self.future.cancel()
        self.executor.shutdown(wait=True)

play_service = PlayService()