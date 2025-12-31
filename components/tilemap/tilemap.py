# widget class
from kivy.uix.relativelayout import RelativeLayout

from enum import Enum
from typing import NamedTuple
import math

# for shuffling cards
import random

# for updating the ui
from kivy.clock import Clock

# for displaying tiles
from kivy.graphics import Color, Ellipse, Line, Rectangle

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

class Tile():
    files = {
        Sight.OBELISK: 'assets/obelisk.png',
        Sight.BOOK: 'assets/book.png',
        Sight.TOUCAN: 'assets/toucan.png',
        Sight.YETI: 'assets/yeti.png',
        Sight.SERPENT: 'assets/serpent.png'
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
        self.active = False

    def draw(self, canvas, size, tile_size):
        with canvas:
            # Calculate position on canvas
            (x, y) = self.coords.cartesian(tile_size)
            y += tile_size
            y = size[1] - y

            # Border
            if self.active:
                Color(1, 0, 0, 1)
            else:
                Color(0.5, 0.5, 0.5, 1)
            self.outline = Ellipse(
                segments = 6,
                pos = (x, y),
                size = (tile_size, tile_size)
            )

            # Set background
            Color(*self.terrain_color[self.terrain])

            # Main fill
            self.fill = Ellipse(
                segments = 6,
                pos = (x+2, y+2),
                size = (tile_size-4, tile_size-4)
            )

            # Icon for sights
            if self.sight in self.files:
                Color(1,1,1,1)
                self.icon = Rectangle(
                    size = (tile_size/2, tile_size/2),
                    pos = (x+0.25*tile_size, y+0.25*tile_size),
                    source = self.files[self.sight]
                )
            else:
                self.icon = None
    
    def update(self, size, tile_size):
        # Calculate position on canvas
        (x, y) = self.coords.cartesian(tile_size)
        y += tile_size
        y = size[1] - y

        self.outline.pos = (x, y)
        self.outline.size = (tile_size, tile_size)

        self.fill.pos = (x+1, y+1)
        self.fill.size = (tile_size-2, tile_size-2)

        if self.sight in self.files:
            self.icon.size = (tile_size/2, tile_size/2)
            self.icon.pos = (x+0.25*tile_size, y+0.25*tile_size)

    def __str__(self):
        return f'({self.terrain}, {self.sight if self.sight is not None else " "})'


class Tilemap(RelativeLayout):
    @staticmethod
    def storage_index(coords: Hex):
        x = int((coords.x - (coords.y%2 == 1)) / 2)
        return NamedTuple('Index', [('x', int), ('y', int)])(x, coords.y)
    
    def __init__(self, width: int = None, height: int = None, **kwargs):
        # Keyword arguments are passed to initialize kivy widget
        super().__init__(**kwargs)

        self.paths = []
        self.tiles = []
        self.max_height = 0
        self.max_width = 0

        self.background = None

        # If size was provided
        if (width is not None) and (height is not None):
            self.set_size(width, height)
        
        # Redraw widget if size changes
        self.bind(pos=self.update, size=self.update)
    
    def set_size(self, width: int, height: int):
        self.max_width = width
        self.max_height = height

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
        coords = Hex.from_cartesian(mouse_pos[0]-self.tile_size/2, self.height-mouse_pos[1]-self.tile_size/2, self.tile_size)

        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    if tile.active:
                        tile.active = False
                        tile.draw(self.canvas, self.size, self.tile_size)
                    
        try:
            self.tiles[coords.y][coords.x].active = True
            self.tiles[coords.y][coords.x].draw(self.canvas, self.size, self.tile_size)
        except:
            print("Can't activate tile.")


    
    def draw(self, *args):
        self.canvas.clear()

        if (self.max_height is not None and self.max_width is not None):
            tile_max_width = self.width / (((self.max_width + 1) / 2) * math.sqrt(3)/2)
            tile_max_height = self.height / (self.max_height * 0.75 + 0.25)
            self.tile_size = min(tile_max_width, tile_max_height)

        with self.canvas:
            # Background
            Color(0.5, 0.5, 0.5, 1)
            self.background = Rectangle(
                pos = (0, 0),
                size = self.size
            )

            for row in self.tiles:
                for tile in row:
                    if tile is not None:
                        tile.draw(self.canvas, self.size, self.tile_size)
                        
            for path in self.paths:
                path.draw(self.canvas.after, self.size, self.tile_size)

    def update(self, *args):
        if (self.max_height is not None and self.max_width is not None):
            tile_max_width = self.width / (((self.max_width + 1) / 2) * math.sqrt(3)/2)
            tile_max_height = self.height / (self.max_height * 0.75 + 0.25)
            self.tile_size = min(tile_max_width, tile_max_height)
        
        if self.background is not None:
            self.background.pos = (0, 0)
            self.background.size = self.size

        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    tile.update(self.size, self.tile_size)
        
        for path in self.paths:
            path.update(self.size, self.tile_size)
    