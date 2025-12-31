from kivy.app import App
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.clock import Clock

from components.tilemap.tilemap import Hex, Terrain, Sight, Tile, Path, Tilemap

class MainApp(App):
    def build(self):
        # Set window size
        Window.size = (800, 800)

        # Draw UI
        self.root = Builder.load_file("main.kv")
        
        # Update UI based on mouse movement
        Window.bind(mouse_pos=self.update)

         # Draw initial elements
        Clock.schedule_once(self.initialize)
        return self.root
    
    def update(self, *args):
        self.root.ids.tilemap.set_active(args[-1])

    def initialize(self, dt):
        # Set tilemap
        self.root.ids.tilemap.set_size(10,10)
        
        # Isla Petit
        self.root.ids.tilemap.set(Tile(Hex(4,0), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(6,0), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(8,0), Terrain.MOUNTAIN, Sight.C_TOWN))
        self.root.ids.tilemap.set(Tile(Hex(10,0), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(12,0), Terrain.FOREST))

        self.root.ids.tilemap.set(Tile(Hex(3,1), Terrain.MOUNTAIN, Sight.D_TOWN))
        self.root.ids.tilemap.set(Tile(Hex(5,1), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(7,1), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(9,1), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(11,1), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(13,1), Terrain.FOREST, Sight.A_TOWN))

        self.root.ids.tilemap.set(Tile(Hex(2,2), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(4,2), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(6,2), Terrain.FOREST, Sight.TOUCAN))
        self.root.ids.tilemap.set(Tile(Hex(8,2), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(10,2), Terrain.DESERT, Sight.OBELISK))
        self.root.ids.tilemap.set(Tile(Hex(12,2), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(14,2), Terrain.DESERT))

        self.root.ids.tilemap.set(Tile(Hex(1,3), Terrain.DESERT, Sight.E_TOWN))
        self.root.ids.tilemap.set(Tile(Hex(3,3), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(5,3), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(7,3), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(9,3), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(11,3), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(13,3), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(15,3), Terrain.DESERT, Sight.B_TOWN))

        self.root.ids.tilemap.set(Tile(Hex(0,4), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(2,4), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(4,4), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(6,4), Terrain.MOUNTAIN, Sight.YETI))
        self.root.ids.tilemap.set(Tile(Hex(8,4), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(10,4), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(12,4), Terrain.FOREST, Sight.BOOK))
        self.root.ids.tilemap.set(Tile(Hex(14,4), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(16,4), Terrain.DESERT))

        self.root.ids.tilemap.set(Tile(Hex(1,5), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(3,5), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(5,5), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(7,5), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(9,5), Terrain.WATER, Sight.SERPENT))
        self.root.ids.tilemap.set(Tile(Hex(11,5), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(13,5), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(15,5), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(17,5), Terrain.FOREST))

        self.root.ids.tilemap.set(Tile(Hex(2,6), Terrain.DESERT, Sight.B_TOWN))
        self.root.ids.tilemap.set(Tile(Hex(4,6), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(6,6), Terrain.FOREST, Sight.BOOK))
        self.root.ids.tilemap.set(Tile(Hex(8,6), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(10,6), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(12,6), Terrain.FOREST, Sight.TOUCAN))
        self.root.ids.tilemap.set(Tile(Hex(14,6), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(16,6), Terrain.DESERT, Sight.D_TOWN))

        self.root.ids.tilemap.set(Tile(Hex(1,7), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(3,7), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(5,7), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(7,7), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(9,7), Terrain.DESERT, Sight.OBELISK))
        self.root.ids.tilemap.set(Tile(Hex(11,7), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(13,7), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(15,7), Terrain.DESERT))

        self.root.ids.tilemap.set(Tile(Hex(0,8), Terrain.MOUNTAIN, Sight.YETI))
        self.root.ids.tilemap.set(Tile(Hex(2,8), Terrain.MOUNTAIN))
        self.root.ids.tilemap.set(Tile(Hex(4,8), Terrain.FOREST, Sight.E_TOWN))
        self.root.ids.tilemap.set(Tile(Hex(6,8), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(8,8), Terrain.FOREST))
        self.root.ids.tilemap.set(Tile(Hex(10,8), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(12,8), Terrain.MOUNTAIN, Sight.C_TOWN))
        self.root.ids.tilemap.set(Tile(Hex(14,8), Terrain.MOUNTAIN))

        self.root.ids.tilemap.set(Tile(Hex(5,9), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(7,9), Terrain.DESERT))
        self.root.ids.tilemap.set(Tile(Hex(9,9), Terrain.FOREST, Sight.A_TOWN))
        self.root.ids.tilemap.set(Tile(Hex(13,9), Terrain.WATER))
        self.root.ids.tilemap.set(Tile(Hex(15,9), Terrain.WATER, Sight.SERPENT))

        # Testing paths
        self.root.ids.tilemap.add_path(Path(Hex(4,4), Hex(6,4)))
        self.root.ids.tilemap.add_path(Path(Hex(6,4), Hex(7,5)))

if __name__ == "__main__":
    MainApp().run()