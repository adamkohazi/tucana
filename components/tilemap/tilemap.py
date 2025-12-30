# widget class
from kivy.uix.relativelayout import RelativeLayout

from enum import Enum
from typing import NamedTuple
import math

# for updating the ui
from kivy.clock import Clock

# for displaying tiles
from kivy.graphics import Color, Ellipse, Line, Rectangle

# For displaying sights and tows
from kivy.uix.label import Label

class Terrain(Enum):
    DESERT = 0
    FOREST = 1
    MOUNTAIN = 2
    WATER = 3

    def __str__(self):
        return self.name[0]

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

    def __str__(self):
        emojis = {
            Sight.OBELISK: "🗿",
            Sight.BOOK: "📕",
            Sight.TOUCAN: "🦜",
            Sight.YETI: "🐅",
            Sight.SERPENT: "🐍",
            Sight.A_TOWN: "A",
            Sight.B_TOWN: "B",
            Sight.C_TOWN: "C",
            Sight.D_TOWN: "D",
            Sight.E_TOWN: "E",
        }
        return emojis[self]

# Double-width horizontal layout: doubles horizontal coordinate
class Hex(NamedTuple):
    x: int
    y: int

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
            math.sqrt(3)/2 * self.x * size/2, # x
            3/2 * self.y * size/2 # y
        )

class Path(NamedTuple):
    start: Hex
    end: Hex

class Tile(NamedTuple):
    coords: Hex
    terrain: Terrain
    sight: Sight = None

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

        # If size was provided
        if (width is not None) and (height is not None):
            self.set_size(width, height)
        
        # Redraw widget if size changes
        self.bind(pos=self.draw, size=self.draw)
    
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
    
    def draw(self, *args):
        self.clear_widgets()
        self.canvas.clear()

        if (self.max_height is not None and self.max_width is not None):
            tile_max_width = self.width / (((self.max_width + 1) / 2) * math.sqrt(3)/2)
            tile_max_height = self.height / (self.max_height * 0.75 + 0.25)
            tile_size = min(tile_max_width, tile_max_height)

        with self.canvas:
            # Background
            Color(0, 0, 0.5, 1)
            Rectangle(
                pos = (0, 0),
                size = self.size
            )

            for row in self.tiles:
                for tile in row:
                    if tile is not None:
                        (x, y) = tile.coords.cartesian(tile_size)
                        y += tile_size
                        y = self.height - y

                        # Border
                        Color(0, 0, 0, 0.5)
                        Ellipse(
                            segments = 6,
                            pos = (x-2, y-2),
                            size = (tile_size, tile_size)
                        )

                        Ellipse(
                            segments = 6,
                            pos = (x-2, y+2),
                            size = (tile_size, tile_size)
                        )

                        # Set background
                        if tile.terrain == Terrain.DESERT:
                            Color(1, 1, 0.8, 1)
                        elif tile.terrain == Terrain.FOREST:
                            Color(0.8, 1, 0.8, 1)
                        elif tile.terrain == Terrain.MOUNTAIN:
                            Color(0.8, 0.8, 0.8, 1)
                        elif tile.terrain == Terrain.WATER:
                            Color(0.6, 0.8, 1.0, 1)
                        else:
                            Color(1, 1, 1, 1)

                        Ellipse(
                            segments = 6,
                            pos = (x, y),
                            size = (tile_size, tile_size)
                        )

                        self.add_widget(Label(
                            text = f'{tile.sight if tile.sight is not None else ""}',
                            color = (0,0,0,1),
                            font_size = 0.4*tile_size,
                            font_name="SEGUIEMJ.ttf",
                            size_hint = (None, None),
                            size = (tile_size, tile_size),
                            center = (x+0.5*tile_size, y+0.5*tile_size)
                        ))
                        
            for path in self.paths:
                (x0, y0) = path.start.cartesian(tile_size)
                (x1, y1) = path.end.cartesian(tile_size)

                y0 += 0.5*tile_size
                y1 += 0.5*tile_size

                x0 += 0.5*math.sqrt(3)/2*tile_size
                x1 += 0.5*math.sqrt(3)/2*tile_size

                Color(0, 0, 0, 1)

                Line(points=[x0, self.height - y0, x1, self.height - y1], width=tile_size/30)

    