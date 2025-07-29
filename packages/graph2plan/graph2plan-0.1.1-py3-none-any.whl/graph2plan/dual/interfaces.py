from pathlib import Path
import json
from dataclasses import dataclass
from typing import Generic, Literal, NamedTuple

import matplotlib.pyplot as plt
import shapely

from graph2plan.constants import OUTPUTS_PATH

from ..helpers.geometry_interfaces import ShapelyBounds, T
from ..helpers.graph_interfaces import Face, get_exterior_names


MarkedNb = NamedTuple("MarkedNb", [("name", str), ("mark", Literal["IN", "OUT"])])


class FacePair(Generic[T], NamedTuple):
    left: Face[T]
    right: Face[T]


EdgeFaceDict = dict[tuple[T, T], FacePair[T]]


@dataclass
class DualVertex(Generic[T]):
    face: Face
    edge: tuple[T, T]
    side: Literal["LEFT", "RIGHT"]

    def name(self, ix):
        return f"v_f{ix}"


class VertexDomain(NamedTuple):
    min: int
    max: int

    def check_is_valid(self):
        assert self.min < self.max, f"min {self.min} !< max {self.max}"


class Domain(NamedTuple):
    name: str
    bounds: ShapelyBounds


@dataclass
class Domains:
    domains: list[Domain]

    def get_domains_lim(self, PAD_BASE=1.4):
        # TODO clean up..
        PAD = PAD_BASE * 1.1
        min_x = min([i.bounds.min_x for i in self.domains]) - PAD
        max_x = max([i.bounds.max_x for i in self.domains]) + PAD
        min_y = min([i.bounds.min_y for i in self.domains]) - PAD
        max_y = max([i.bounds.max_y for i in self.domains]) + PAD
        return (min_x, max_x), (min_y, max_y)

    def draw(self):
        fig = plt.figure()
        ax = fig.add_subplot()
        xlim, ylim = self.get_domains_lim()
        for d in self.domains:
            patch = d.bounds.get_mpl_patch()
            ax.add_artist(patch)
            ax.annotate(d.name, (0.5, 0.5), xycoords=patch, ha="center", va="bottom")
        ax.set(xlim=xlim, ylim=ylim)

    def to_shapely_rectangles(self):
        shapes = [i.bounds.to_shapely_rectangle() for i in self.domains]
        union = shapely.unary_union(shapes)
        return union
    
    def to_floorplan(self):
        return [[dom.bounds.to_room_type(ix, dom.name).to_json() for ix, dom in enumerate(self.domains) if dom.name not in get_exterior_names()]]
    
    def write_floorplan(self, output_path:Path=OUTPUTS_PATH, filename="plan.json"):
        with open(output_path / filename, "w+") as file:
            json.dump(self.to_floorplan(), default=str, fp=file)
            print(f"Saved floorplan to {output_path.parent / output_path.name}") # TODO potentially rich print?
            


    
    # jsonify should exist here.. 
