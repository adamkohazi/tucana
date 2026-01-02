from kivy.app import App
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.clock import Clock

from components.tilemap.tilemap import Hex, Terrain, Sight, Tile, Path, Tilemap

class MainApp(App):
    def build(self):
        self._entities = set()

        # Set window size
        Window.size = (800, 800)

        # Draw UI
        self.root = Builder.load_file("main.kv")
        
        # Update UI based on mouse movement
        self.mouse_pos = (0, 0)
        Window.bind(mouse_pos=self.update_mouse_pos)

         # Draw initial elements
        Clock.schedule_once(self.initialize)
        return self.root
    
    def update_mouse_pos(self, *args):
        self.mouse_pos = args[-1]
        self.root.ids.tilemap.set_active(self.mouse_pos)

    def initialize(self, dt):
        # Set tilemap
        self.root.ids.tilemap.load_from_file("assets/maps/isla_petit.json")

        # Testing paths
        self.root.ids.tilemap.add_path(Path(Hex(4,4), Hex(6,4)))
        self.root.ids.tilemap.add_path(Path(Hex(6,4), Hex(7,5)))

        # Setup framerate (60)
        self.register_event_type("on_frame")
        Clock.schedule_interval(self._on_frame, 1/60)
    
    def _on_frame(self, dt):
        self.dispatch("on_frame", dt)

    def on_frame(self, dt):
        pass

    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            self.canvas.remove(entity._instruction)

if __name__ == "__main__":
    MainApp().run()