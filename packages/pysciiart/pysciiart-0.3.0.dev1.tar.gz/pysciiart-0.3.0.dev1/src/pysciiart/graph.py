from typing import List, Tuple, Mapping

from pysciiart.coordinates import Rectangle, Path, PathStep
from pysciiart.graph_layer import LayerModel
from pysciiart.graph_solver import compute_positions, link_hotspots
from pysciiart.raster import Raster
from pysciiart.widget import Widget, Size, Hints

STEP_CHARS: Mapping[PathStep, str] = {PathStep.HORIZONTAL: "-", PathStep.VERTICAL: "|", PathStep.TURN: "+"}


class Graph(Widget):
    def __init__(self,
                 widgets: List[Widget],
                 links: List[Tuple[Widget, Widget]],
                 layer_spacing: int = 5):
        super().__init__()
        self._layers = LayerModel()
        self._links = links
        self._layer_spacing = layer_spacing

        # Initial flat single layer

        for w in widgets:
            self._layers.add(w)

        # Iteratively shift items to deeper layers in order to ensure links
        # go from left to right

        updated = True

        while updated:
            updated = False

            for link_src, link_dst in links:
                ix1 = self._layers.find_item_position(link_src)
                ix2 = self._layers.find_item_position(link_dst)

                if ix1[0] >= ix2[0]:
                    self._layers.shift(link_dst)
                    updated = True
                    break

        # Sort items in layers based on link source order to avoid crossings

        for layer_index, layer in enumerate(self._layers.get_layers()):
            layer.sort(key=lambda wid: self._widget_sort_key(wid))

    def _widget_sort_key(self, widget: Widget) -> int:
        result = 0

        # Iterate on link sources
        for src in [link[0] for link in self._links if link[1] == widget]:
            source_position = self._layers.find_item_position(src)
            result += source_position[1]

        return result

    def preferred_size(self) -> Size:
        raise Exception('Not implemented')

    def render(self, hints: Hints = None) -> Raster:
        r = Raster()

        positions: Mapping[Widget, Rectangle] = compute_positions(self._layers,
                                                                  self._links,
                                                                  self._layer_spacing)

        # Render all components

        for widget, position in positions.items():
            hints = Hints(position)
            content_raster = widget.render(hints)
            r.write(position.x, position.y, content_raster)

        # Draw links

        for l_from, l_to in self._links:
            rect_from = positions[l_from.get_ancestor()]
            rect_to = positions[l_to.get_ancestor()]

            pos1 = link_hotspots(rect_from)[1]
            pos2 = link_hotspots(rect_to)[0]

            path = Path(pos1, pos2)

            for step, pos in path:
                r.write(pos.x, pos.y, STEP_CHARS[step])

            r.write(path[-1][1].x, path[-1][1].y, '>')

        return r
