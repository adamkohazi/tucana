# widget class
from kivy.uix.relativelayout import RelativeLayout

from enum import Enum
from typing import NamedTuple
import math

# for loading data from files
import json

# for shuffling cards
import random

# for updating the ui
from kivy.clock import Clock

# for displaying tiles
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import Translate, Scale, PushMatrix, PopMatrix
from kivy.graphics import InstructionGroup

class Entity(object):
    def __init__(self):
        # Drawing group
        self._instructions = InstructionGroup()
        self._instructions.add(PushMatrix())

        # Translation
        self._pos = (0, 0)
        self._translate = Translate(self._pos)
        self._instructions.add(self._translate)

        # Scaling
        self._size = (0, 0)
        self._scale = Scale(self._size, self._size, self._size)
        self._instructions.add(self._scale)
        
        # Other drawing instructions should go here
        self._instructions.add(PopMatrix())
        
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        self._pos = value
        self._translate.x = self._pos[0]
        self._translate.y = self._pos[1]
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = value
        self._scale.x = self._size[0]
        self._scale.y = self._size[1]

    def add_instruction(self, instruction):
        # Start by removing the closing "pop"
        self._instructions.remove(self._instructions.children[-1]) # remove last
        # Add new instruction
        self._instructions.add(instruction)
        # Re-add the closing "pop"
        self._instructions.add(PopMatrix())

class Terrain(Enum):
    DESERT = 0
    FOREST = 1
    MOUNTAIN = 2
    WATER = 3
    ANY = 4

class Sight(Enum):
    OBELISK = 0
    BOOK = 1
    TOUCAN = 2
    YETI = 3
    SERPENT = 4
    A_TOWN = 5
    B_TOWN = 6
    C_TOWN = 7
    D_TOWN = 8
    E_TOWN = 9

class Deck():
    def __init__(self):
        # Reset deck
        self.cards = [
            [Terrain.DESERT] * 8,
            [Terrain.FOREST] * 7,
            [Terrain.MOUNTAIN] * 6,
            [Terrain.WATER] * 4,
            [Terrain.ANY] * 2
        ]
        # Shuffle
        random.shuffle(self.cards)
    
    def draw(self) -> Terrain:
        return self.cards.pop()


# Double-width horizontal layout: doubles horizontal coordinate
class Hex(NamedTuple):
    x: int
    y: int

    @staticmethod
    def from_cartesian(x, y, size) -> 'Hex':
        return Hex(
            round(x / math.sqrt(3) / (size/2)),  # x
            round(y * 2/3 / (size/2))  # y
        )

    def __str__(self):
        return f'({self.x}, {self.y})'
    
    def distance(self, other: 'Hex') -> int:
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        return dy + max(0, (dx-dy)/2)
    
    def neighbors(self) -> list['Hex']:
        return [
            Hex(self.x + 2, self.y + 0),
            Hex(self.x + 1, self.y - 1),
            Hex(self.x - 1, self.y - 1),
            Hex(self.x - 2, self.y + 0),
            Hex(self.x - 1, self.y + 1),
            Hex(self.x + 1, self.y + 1)
        ]
    
    def cartesian(self, size: float = 1.0):
        return (
            self.x * math.sqrt(3)/2 * (size/2), # x
            self.y * 3/2 * (size/2) # y
        )

class Path():
    def __init__(self, start: Hex, end: Hex):
        self.start = start
        self.end = end
    
    def draw(self, canvas, size, tile_size):
        (x0, y0) = self.start.cartesian(tile_size)
        (x1, y1) = self.end.cartesian(tile_size)

        y0 += 0.5*tile_size
        y1 += 0.5*tile_size

        x0 += 0.5*math.sqrt(3)/2*tile_size
        x1 += 0.5*math.sqrt(3)/2*tile_size

        with canvas:
            Color(0, 0, 0, 1)
            self.line = Line(points=[x0, size[1] - y0, x1, size[1] - y1], width=tile_size/30)
    
    def update(self, size, tile_size):
        (x0, y0) = self.start.cartesian(tile_size)
        (x1, y1) = self.end.cartesian(tile_size)

        y0 += 0.5*tile_size
        y1 += 0.5*tile_size

        x0 += 0.5*math.sqrt(3)/2*tile_size
        x1 += 0.5*math.sqrt(3)/2*tile_size

        self.line.points = [x0, size[1] - y0, x1, size[1] - y1]
        self.line.width = tile_size/30

class Tile(object):
    files = {
        Sight.OBELISK: 'assets/graphics/obelisk.png',
        Sight.BOOK: 'assets/graphics/book.png',
        Sight.TOUCAN: 'assets/graphics/toucan.png',
        Sight.YETI: 'assets/graphics/yeti.png',
        Sight.SERPENT: 'assets/graphics/serpent.png'
    }

    terrain_color = {
        Terrain.DESERT: (1, 1, 0.8, 1),
        Terrain.FOREST: (0.8, 1, 0.8, 1),
        Terrain.MOUNTAIN: (0.8, 0.8, 0.8, 1),
        Terrain.WATER: (0.6, 0.8, 1.0, 1)
    }

    def __init__(self, coords: Hex, terrain: Terrain = None, sight: Sight = None):
        self.coords = coords
        self.terrain = terrain
        self.sight = sight
        self._active = False

        self._instructions = InstructionGroup()

        # Offset based on coordinates
        (x, y) = self.coords.cartesian()
        self._instructions.add(PushMatrix())
        self._instructions.add(Translate(x, y, 0))

        # Border
        self._border_color = Color(0.5, 0.5, 0.5, 1)
        self._instructions.add(self._border_color)

        self._instructions.add(
            Ellipse(segments = 6, pos = (0, 0), size = (1, 1))
        )

        # Main fill
        self._fill_color = Color(*self.terrain_color[self.terrain])
        self._instructions.add(self._fill_color)

        self._instructions.add(
            Ellipse(segments = 6, pos = (0.02, 0.02), size = (0.96, 0.96))
        )

        # Icon for sights
        if self.sight in self.files:
            self._instructions.add(
                Color(1,1,1,1)
            )
            self._instructions.add(
                Rectangle(pos = (0.25, 0.25), size = (0.5, 0.5), source = self.files[self.sight])
            )
        
        # Cancel offset
        self._instructions.add(PopMatrix())
    
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, value: bool):
        self._active = value
        if self._active:
            self._border_color.rgba = (1, 0, 0, 1)
        else:
            self._border_color.rgba = (0.5, 0.5, 0.5, 1)
    
    @property
    def instructions(self):
        return self._instructions
    
    def __str__(self):
        return f'({self.terrain}, {self.sight if self.sight is not None else " "})'


class Tilemap(RelativeLayout):
    @staticmethod
    def storage_index(coords: Hex):
        x = int((coords.x - (coords.y%2 == 1)) / 2)
        return NamedTuple('Index', [('x', int), ('y', int)])(x, coords.y)
    
    def __init__(self, **kwargs):
        # Keyword arguments are passed to initialize kivy widget
        super().__init__(**kwargs)

        self.paths = []
        self.tiles = []

        # Background
        self._background = Rectangle(pos=(0, 0), size=self.size)

        # Tile scale
        self._tile_scale = Scale(0,0,0)

        # Redraw widget if size changes
        self.bind(pos=self.update_positions, size=self.update_positions)
    
    def load_from_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Load map size
        self.set_size(data["width"], data["height"])

        # Load tiles
        for tile_data in data["tiles"]:
            x = tile_data["x"]
            y = tile_data["y"]

            terrain = Terrain[tile_data["terrain"]]

            sight = None
            if "sight" in tile_data:
                sight = Sight[tile_data["sight"]]

            tile = Tile(Hex(x, y), terrain, sight)
            self.set(tile)
    
    def set_size(self, width: int, height: int):
        for y in range(height):
            self.tiles.append([])
            for x in range(width):
                tile = None
                self.tiles[y].append(tile)
    
    def set(self, tile: Tile):
        try:
            index = self.storage_index(tile.coords)
            self.tiles[index.y][index.x] = tile

            # Update graphics
            Clock.schedule_once(self.draw, 0)

        except:
            print(f"Can't set tile at ({tile.coords.x}, {tile.coords.y})")

    def add_path(self, path: Path):
        self.paths.append(path)
    
    def set_active(self, mouse_pos):
        coords = Hex.from_cartesian(mouse_pos[0]-self.tile_size, mouse_pos[1]-self.tile_size/2, self.tile_size)

        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    if tile.active:
                        tile.active = False
        try:
            self.tiles[coords.y][coords.x].active = True
        except:
            print("Can't activate tile.")
    
    
    def draw(self, *args):
        self.update_positions()

        # Background
        self.canvas.before.add(Color(0.5, 0.5, 0.5, 1))
        self.canvas.before.add(self._background)
        
        # Set size
        self.canvas.add(PushMatrix())
        self.canvas.add(self._tile_scale)

        # Draw tiles
        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    self.canvas.add(tile._instructions)
        
        self.canvas.add(PopMatrix())

        # Draw paths           
        #for path in self.paths:
        #    path.draw(self.canvas.after, self.size, self.tile_size)

    def update_positions(self, *args):
        try:
            rows = len(self.tiles)
            cols = len(self.tiles[0])
        except:
            print("Can't update positions.")
            return

        max_tile_width = self.width / (((cols + 1) / 2) * math.sqrt(3)/2)
        max_tile_height = self.height / (rows * 0.75 + 0.25)

        self.tile_size = min(max_tile_width, max_tile_height)
        
        self._tile_scale.x = self.tile_size
        self._tile_scale.y = self.tile_size

        # Update background
        self._background.size = self.size
        
        #for path in self.paths:
        #    path.update(self.size, self.tile_size)
    