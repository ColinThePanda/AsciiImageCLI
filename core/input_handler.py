from pynput import keyboard
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass

# Import for type hints
if TYPE_CHECKING:
    from pdretro import Emulator

# Import for runtime
from pdretro import RetroButton


@dataclass
class ButtonMapping:
    """Maps a keyboard key to a controller button"""
    button: RetroButton


class Keymap:
    """Keyboard to controller button mappings for Player 1"""
    
    def __init__(self):
        self.mappings: dict[keyboard.Key | keyboard.KeyCode, ButtonMapping] = {}
    
    def bind(self, key: str | keyboard.Key, button: RetroButton):
        """Bind a keyboard key to a controller button
        
        Args:
            key: Either a string (e.g., 'z', 'a') or keyboard.Key (e.g., keyboard.Key.up)
            button: RetroButton enum value
        """
        if isinstance(key, str):
            key_obj = keyboard.KeyCode.from_char(key.lower())
        else:
            key_obj = key
        
        self.mappings[key_obj] = ButtonMapping(button)
    
    def get_mapping(self, key: keyboard.Key | keyboard.KeyCode) -> Optional[ButtonMapping]:
        """Get the button mapping for a key"""
        return self.mappings.get(key)
    
    @staticmethod
    def retroarch_default() -> "Keymap":
        """Default RetroArch-style keymap for Player 1
        
        Controls:
            Arrow Keys: D-pad
            Z: B button (bottom)
            X: A button (right)
            A: Y button (left)
            S: X button (top)
            Q: L shoulder
            W: R shoulder
            E: L2 shoulder (trigger)
            R: R2 shoulder (trigger)
            Enter: START
            Right Shift: SELECT
        """
        keymap = Keymap()
        
        # D-pad
        keymap.bind(keyboard.Key.up, RetroButton.UP)
        keymap.bind(keyboard.Key.down, RetroButton.DOWN)
        keymap.bind(keyboard.Key.left, RetroButton.LEFT)
        keymap.bind(keyboard.Key.right, RetroButton.RIGHT)
        
        # Face buttons (SNES layout)
        keymap.bind('z', RetroButton.B)      # Bottom
        keymap.bind('x', RetroButton.A)      # Right
        keymap.bind('a', RetroButton.Y)      # Left
        keymap.bind('s', RetroButton.X)      # Top
        
        # Shoulder buttons
        keymap.bind('q', RetroButton.L)
        keymap.bind('w', RetroButton.R)
        keymap.bind('e', RetroButton.L2)
        keymap.bind('r', RetroButton.R2)
        
        # Start/Select
        keymap.bind(keyboard.Key.enter, RetroButton.START)
        keymap.bind(keyboard.Key.shift_r, RetroButton.SELECT)
        
        return keymap


class InputHandler:
    """Handles keyboard input for emulator control
    
    Uses pynput for cross-platform keyboard listening and applies inputs
    directly to the pdretro Emulator instance.
    """
    
    def __init__(self, emulator: "Emulator", keymap: Optional[Keymap] = None):
        """
        Args:
            emulator: The pdretro Emulator instance to control
            keymap: Keymap to use (defaults to RetroArch layout)
        """
        self.emulator = emulator
        self.keymap = keymap or Keymap.retroarch_default()
        self.pressed_keys: set[keyboard.Key | keyboard.KeyCode] = set()
        self.listener: Optional[keyboard.Listener] = None
        self.port = 0  # Always use port 0 for single player
    
    def start(self):
        """Start listening for keyboard input"""
        if self.listener is not None:
            return
        
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def stop(self):
        """Stop listening for keyboard input"""
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        
        # Clear all pressed inputs
        self._clear_all_inputs()
    
    def _on_press(self, key: keyboard.Key | keyboard.KeyCode | None):
        """Handle key press event"""
        if key is None:
            return  # Unknown key
        
        if key in self.pressed_keys:
            return  # Already pressed (key repeat)
        
        mapping = self.keymap.get_mapping(key)
        if mapping is None:
            return  # Not mapped
        
        self.pressed_keys.add(key)
        
        # Apply input to emulator
        self.emulator.set_button(self.port, int(mapping.button), True)
    
    def _on_release(self, key: keyboard.Key | keyboard.KeyCode | None):
        """Handle key release event"""
        if key is None:
            return  # Unknown key
        
        if key not in self.pressed_keys:
            return  # Not pressed
        
        mapping = self.keymap.get_mapping(key)
        if mapping is None:
            return  # Not mapped
        
        self.pressed_keys.discard(key)
        
        # Release input from emulator
        self.emulator.set_button(self.port, int(mapping.button), False)
    
    def _clear_all_inputs(self):
        """Clear all pressed inputs"""
        self.emulator.clear_input()
        self.pressed_keys.clear()