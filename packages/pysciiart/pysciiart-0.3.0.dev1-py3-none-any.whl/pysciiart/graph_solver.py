import itertools
import math
from typing import Mapping, Tuple, List

from pysciiart.coordinates import Rectangle, Position
from pysciiart.graph_layer import LayerModel
from pysciiart.widget import Widget

LARGE_VALUE = 99999999


def compute_widget_positions(layers: LayerModel,
                             offsets: Mapping[Widget, int],
                             layer_spacing: int) -> Mapping[Widget, Rectangle]:
    result = {}

    x = 0

    for layer in layers.get_layers():
        y = 0
        layer_width = 0

        for w in layer:
            y += offsets[w]

            size = w.preferred_size()

            result[w] = Rectangle(x=x, y=y, width=size.width, height=size.height)

            layer_width = max(layer_width, size.width)
            y += size.height

        x += layer_width + layer_spacing

    return result


def is_colliding(positions: Mapping[Widget, Rectangle], segment: Tuple[Position, Position]) -> bool:
    for widget_position in positions.values():
        seg_x1 = min(segment[0].x, segment[1].x)
        seg_x2 = max(segment[0].x, segment[1].x)
        if (seg_x1 < widget_position.x and widget_position.x + widget_position.width < seg_x2
            and (widget_position.y <= segment[0].y <= widget_position.y + widget_position.height
                 or widget_position.y <= segment[1].y <= widget_position.y + widget_position.height)
        ):
            return True

    return False


def link_hotspots(rect: Rectangle) -> Tuple[Position, Position]:
    y = rect.y + math.floor((rect.height - 1) / 2)
    port_out = Position(rect.x + rect.width, y)
    port_in = Position(rect.x - 1, y)
    return port_in, port_out


def compute_positions(layers: LayerModel,
                      links: List[Tuple[Widget, Widget]],
                      layer_spacing=5) -> Mapping[Widget, Rectangle]:
    # Calculate the minimum height of all layers

    layer_min_heights = []
    widgets = []

    for layer in layers.get_layers():
        height = 0

        for widget in layer:
            height += widget.preferred_size().height
            widgets.append(widget)

        layer_min_heights.append(height)

    layer_gaps = [max(layer_min_heights) - h for h in layer_min_heights]

    # Reserve space to avoid crossing widgets

    for w1, w2 in links:
        layer_1 = layers.find_item_position(w1)[0]
        layer_2 = layers.find_item_position(w2)[0]

        if layer_1 + 1 < layer_2:
            for mid_layer in range(layer_1 + 1, layer_2):
                layer_gaps[mid_layer] += math.ceil(w1.preferred_size().height / 2)

    # Calculate free space in each layer aka. offset ranges

    widget_offset_ranges = []

    for layer_index, layer in enumerate(layers.get_layers()):
        for _ in layer:
            widget_offset_ranges.append(range(layer_gaps[layer_index] + 1))

    # Optimise offsets to limit vertical gaps

    best_deviation = LARGE_VALUE
    best_positions = None

    for offsets in itertools.product(*widget_offset_ranges):
        widget_offsets = {widgets[i]: offsets[i] for i in range(len(widgets))}

        total_deviation = 0
        positions = compute_widget_positions(layers, widget_offsets, layer_spacing)

        for w1, w2 in links:
            a1 = w1.get_ancestor()
            a2 = w2.get_ancestor()
            p1 = positions[a1]
            p2 = positions[a2]
            h1 = link_hotspots(p1)[1]
            h2 = link_hotspots(p2)[0]

            if is_colliding(positions, (h1, h2)):
                total_deviation += LARGE_VALUE
            else:
                total_deviation += pow(abs(h2.y - h1.y), 2)

        if total_deviation < best_deviation:
            best_deviation = total_deviation
            best_positions = positions

    return best_positions
