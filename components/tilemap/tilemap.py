# widget class
from kivy.uix.relativelayout import RelativeLayout

# for compact data types
from enum import Enum
from dataclasses import dataclass

# ...for math...duh
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
@dataclass(frozen=True, slots=True)
class Hex:
    x: int
    y: int

    @staticmethod
    def from_cartesian(x: float, y: float, size:float) -> 'Hex':
        return Hex(
            round(x / (math.sqrt(3)/2) / (size/2)),  # x
            round(y * 2/3 / (size/2))  # y
        )
    
    def distance(self, other: 'Hex') -> int:
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        return dy + max(0, (dx-dy)/2)
    
    def neighbors(self) -> list['Hex']:
        x, y = self.x, self.y
        return [
            Hex(x+2, y  ),
            Hex(x+1, y-1),
            Hex(x-1, y-1),
            Hex(x-2, y  ),
            Hex(x-1, y+1),
            Hex(x+1, y+1),
        ]
    
    def cartesian(self, size: float = 1.0) -> tuple[float, float]:
        return (
            self.x * math.sqrt(3)/2 * (size/2), # x
            self.y * 3/2 * (size/2) # y
        )

class Tile():
    def __init__(self, coords: Hex, terrain: Terrain, sight: Sight = None):
        self.coords = coords
        self.terrain = terrain
        self.sight = sight
        self.active = False
    
    def __repr__(self):
        return f"Tile({self.coords}, {self.terrain}, {self.sight})"

class TileView():
    ICON_FILES = {
        Sight.OBELISK: 'assets/graphics/obelisk.png',
        Sight.BOOK: 'assets/graphics/book.png',
        Sight.TOUCAN: 'assets/graphics/toucan.png',
        Sight.YETI: 'assets/graphics/yeti.png',
        Sight.SERPENT: 'assets/graphics/serpent.png'
    }

    TERRAIN_COLORS = {
        Terrain.DESERT: (1, 1, 0.8, 1),
        Terrain.FOREST: (0.8, 1, 0.8, 1),
        Terrain.MOUNTAIN: (0.8, 0.8, 0.8, 1),
        Terrain.WATER: (0.6, 0.8, 1.0, 1)
    }

    BORDER_INACTIVE = (0.5, 0.5, 0.5, 1)
    BORDER_ACTIVE = (1, 0, 0, 1)

    def __init__(self, tile: Tile):
        self.tile = tile
        self.instructions = InstructionGroup()

        # Offset based on coordinates
        x, y = self.tile.coords.cartesian()
        self.instructions.add(PushMatrix())
        self.instructions.add(Translate(x, y, 0))

        # Border
        self._border_color = Color(*self.BORDER_INACTIVE)
        self.instructions.add(self._border_color)

        self.instructions.add(Ellipse(
            segments = 6,
            pos = (0, 0),
            size = (1, 1))
        )

        # Main fill
        self._fill_color = Color(*self.TERRAIN_COLORS[self.tile.terrain])
        self.instructions.add(self._fill_color)

        self.instructions.add(Ellipse(
            segments = 6,
            pos = (0.02, 0.02),
            size = (0.96, 0.96))
        )

        # Icon for sights
        if self.tile.sight in self.ICON_FILES:
            self.instructions.add(Color(1,1,1,1))
            self.instructions.add(Rectangle(
                pos = (0.25, 0.25),
                size = (0.5, 0.5),
                source = self.ICON_FILES[self.tile.sight])
            )
        
        # Cancel offset
        self.instructions.add(PopMatrix())
    
    def update(self):
        if self.tile.active:
            self._border_color.rgba = self.BORDER_ACTIVE
        else:
            self._border_color.rgba = self.BORDER_INACTIVE

class TileGrid:
    def __init__(self):
        self.width = 0
        self.height = 0
        self._tiles: dict[Hex, Tile] = {}
    
    def get(self, index: Hex):
        return self._tiles.get(index)

    def set(self, tile: Tile):
        self._tiles[tile.coords] = tile
        if tile.coords.x >= self.width:
            self.width = tile.coords.x + 1
        
        if tile.coords.y >= self.height:
            self.height = tile.coords.y + 1
    
    def __iter__(self):
        return iter(self._tiles.values())

@dataclass(frozen=True)
class Path():
    start: Hex
    end: Hex

class PathView():
    LINE_COLOR = (0, 0, 0.2, 1)

    def __init__(self, path: Path):
        self.path = path

        self.instructions = InstructionGroup()

        # Border
        self.instructions.add(Color(*self.LINE_COLOR))

        (x0, y0) = self.path.start.cartesian()
        x0 += 0.5*math.sqrt(3)/2
        y0 += 0.5

        (x1, y1) = self.path.end.cartesian()
        x1 += 0.5*math.sqrt(3)/2
        y1 += 0.5

        self.instructions.add(Line(
            points =[x0, y0, x1, y1],
            width = 0.03)
        )

def load_from_file(filename: str) -> TileGrid:
        grid = TileGrid()

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data["tiles"]:
            tile = Tile(
                coords = Hex(entry["x"], entry["y"]),
                terrain = Terrain[entry["terrain"]],
                sight = Sight[entry["sight"]] if "sight" in entry else None
            )

            grid.set(tile)
        
        return grid

class Tilemap(RelativeLayout):
    def __init__(self, grid: TileGrid, **kwargs):
        # Keyword arguments are passed to initialize kivy widget
        super().__init__(**kwargs)

        # Tiles
        self.grid = grid
        self.tile_views: dict[Tile, TileView] = {}
        # Populate views
        for tile in self.grid:
            view = TileView(tile)
            self.tile_views[tile] = view
        
        # Paths
        self.paths = []
        self.path_views: dict[Path, PathView] = {}

        # Background
        self._background = Rectangle(pos=(0, 0), size=self.size)
        
        # Tile scale
        self.tile_size = 0
        self._tile_scale = Scale(self.tile_size, self.tile_size, self.tile_size)

        # Redraw widget if size changes
        self.bind(pos=self.update_positions, size=self.update_positions)

        # Draw tilemap
        Clock.schedule_once(self.draw)

    def add_path(self, path: Path):
        self.paths.append(path)
        self.path_views[path] = PathView(path)
    
    def set_active(self, mouse_pos):
        coords = Hex.from_cartesian(
            mouse_pos[0]-self.tile_size/2, # x
            mouse_pos[1]-self.tile_size/2, # y
            self.tile_size
        )

        # Activate the one tile at coords, deactivate all other
        for tile in self.grid:
            tile.active = (tile.coords.x == coords.x and tile.coords.y == coords.y)
            self.tile_views[tile].update()
    
    def draw(self, *args):
        # Background
        self.canvas.before.add(Color(0.5, 0.5, 0.5, 1))
        self.canvas.before.add(self._background)

        # Update position and size
        self.update_positions()

        # Set size
        self.canvas.add(PushMatrix())
        self.canvas.add(self._tile_scale)
        
        # Draw tiles
        for tile in self.grid:
            self.canvas.add(self.tile_views[tile].instructions)

        # Draw paths
        for path in self.paths:
            self.canvas.add(self.path_views[path].instructions)
        
        # Restore size
        self.canvas.add(PopMatrix())

    def update_positions(self, *args):
        # Calculate tile size:
        # Keep aspect and fit whole grid
        max_tile_width = self.width / (((self.grid.width + 0.5) / 2) * math.sqrt(3)/2)
        max_tile_height = self.height / (self.grid.height * 0.75 + 0.25)
        self.tile_size = min(max_tile_width, max_tile_height)
        
        # Update size
        self._tile_scale.x = self.tile_size
        self._tile_scale.y = self.tile_size

        # Update background
        self._background.size = self.size
    