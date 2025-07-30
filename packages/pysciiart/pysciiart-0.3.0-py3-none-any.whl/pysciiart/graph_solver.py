from typing import List, Mapping, Tuple

from pysciiart.coordinates import Path, Position, Rectangle
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
    """Check if a line segment collides with any widget."""
    for widget_position in positions.values():
        if _line_intersects_rectangle(segment[0], segment[1], widget_position):
            return True
    return False


def _line_intersects_rectangle(p1: Position, p2: Position, rect: Rectangle) -> bool:
    """Check if a line segment from p1 to p2 intersects with a rectangle."""
    # Check if line passes through the rectangle
    # First check if either endpoint is inside the rectangle
    if (_point_in_rectangle(p1, rect) or _point_in_rectangle(p2, rect)):
        return True

    # Check if line intersects any of the rectangle edges
    rect_corners = [
        Position(rect.x, rect.y),  # top-left
        Position(rect.x + rect.width, rect.y),  # top-right
        Position(rect.x + rect.width, rect.y + rect.height),  # bottom-right
        Position(rect.x, rect.y + rect.height)  # bottom-left
    ]

    # Check intersection with each edge of the rectangle
    edges = [
        (rect_corners[0], rect_corners[1]),  # top edge
        (rect_corners[1], rect_corners[2]),  # right edge
        (rect_corners[2], rect_corners[3]),  # bottom edge
        (rect_corners[3], rect_corners[0])  # left edge
    ]

    for edge_start, edge_end in edges:
        if _line_segments_intersect(p1, p2, edge_start, edge_end):
            return True

    return False


def _point_in_rectangle(point: Position, rect: Rectangle) -> bool:
    """Check if a point is inside a rectangle."""
    return (rect.x <= point.x <= rect.x + rect.width and
            rect.y <= point.y <= rect.y + rect.height)


def _line_segments_intersect(p1: Position, p2: Position, p3: Position, p4: Position) -> bool:
    """Check if two line segments intersect."""

    def orientation(p: Position, q: Position, r: Position) -> int:
        """Find orientation of ordered triplet (p, q, r).
        Returns 0 if collinear, 1 if clockwise, 2 if counterclockwise"""
        val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
        if val == 0:
            return 0  # collinear
        return 1 if val > 0 else 2  # clockwise or counterclockwise

    def on_segment(p: Position, q: Position, r: Position) -> bool:
        """Check if point q lies on segment pr"""
        return (q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and
                q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y))

    o1 = orientation(p1, p2, p3)
    o2 = orientation(p1, p2, p4)
    o3 = orientation(p3, p4, p1)
    o4 = orientation(p3, p4, p2)

    # General case
    if o1 != o2 and o3 != o4:
        return True

    # Special cases for collinear points
    if (o1 == 0 and on_segment(p1, p3, p2)) or \
        (o2 == 0 and on_segment(p1, p4, p2)) or \
        (o3 == 0 and on_segment(p3, p1, p4)) or \
        (o4 == 0 and on_segment(p3, p2, p4)):
        return True

    return False


def path_collides_with_widgets(path: Path, positions: Mapping[Widget, Rectangle],
                               source_widget: Widget, dest_widget: Widget) -> bool:
    """Check if a path collides with any widgets (excluding source and destination)."""
    if len(path) < 2:
        return False

    # Get source and destination rectangles to exclude from collision checking
    source_rect = positions.get(source_widget)
    dest_rect = positions.get(dest_widget)

    # Check each segment of the path
    for i in range(len(path) - 1):
        segment_start = path[i][1]
        segment_end = path[i + 1][1]

        for widget, widget_rect in positions.items():
            # Skip collision check with source and destination widgets
            if widget == source_widget or widget == dest_widget:
                continue
            if widget_rect == source_rect or widget_rect == dest_rect:
                continue

            if _line_intersects_rectangle(segment_start, segment_end, widget_rect):
                return True

    return False


def link_hotspots(rect: Rectangle) -> Tuple[Position, Position]:
    """Get the default input and output connection points for a widget."""
    y = rect.y + (rect.height - 1) // 2
    port_out = Position(rect.x + rect.width, y)
    port_in = Position(rect.x - 1, y)
    return port_in, port_out


def get_connection_ports(rect: Rectangle, port_type: str = 'both') -> List[Position]:
    """Get all available connection ports for a widget.

    Args:
        rect: Widget rectangle
        port_type: 'input', 'output', or 'both'

    Returns:
        List of available connection positions
    """
    ports = []

    # Calculate center and quarter positions
    center_y = rect.y + (rect.height - 1) // 2
    quarter_y = rect.y + rect.height // 4
    three_quarter_y = rect.y + (3 * rect.height) // 4

    # Input ports (left side)
    if port_type in ['input', 'both']:
        if rect.height == 1:
            ports.append(Position(rect.x - 1, center_y))
        elif rect.height >= 3:
            ports.extend([
                Position(rect.x - 1, quarter_y),
                Position(rect.x - 1, center_y),
                Position(rect.x - 1, three_quarter_y)
            ])
        else:  # height == 2
            ports.extend([
                Position(rect.x - 1, rect.y),
                Position(rect.x - 1, rect.y + 1)
            ])

    # Output ports (right side)
    if port_type in ['output', 'both']:
        if rect.height == 1:
            ports.append(Position(rect.x + rect.width, center_y))
        elif rect.height >= 3:
            ports.extend([
                Position(rect.x + rect.width, quarter_y),
                Position(rect.x + rect.width, center_y),
                Position(rect.x + rect.width, three_quarter_y)
            ])
        else:  # height == 2
            ports.extend([
                Position(rect.x + rect.width, rect.y),
                Position(rect.x + rect.width, rect.y + 1)
            ])

    return ports


def select_best_ports(src_rect: Rectangle, dst_rect: Rectangle,
                      existing_connections: List[Tuple[Position, Position]] = None) -> Tuple[
    Position, Position]:
    """Select the best input/output port pair to minimize conflicts and distance.

    Args:
        src_rect: Source widget rectangle
        dst_rect: Destination widget rectangle
        existing_connections: List of existing connection lines to avoid

    Returns:
        Tuple of (output_port_from_src, input_port_to_dst)
    """
    if existing_connections is None:
        existing_connections = []

    output_ports = get_connection_ports(src_rect, 'output')
    input_ports = get_connection_ports(dst_rect, 'input')

    best_score = float('inf')
    best_pair = None

    # Calculate center positions for alignment bonus
    src_center_y = src_rect.y + (src_rect.height - 1) // 2
    dst_center_y = dst_rect.y + (dst_rect.height - 1) // 2

    for out_port in output_ports:
        for in_port in input_ports:
            # Calculate basic distance
            distance = abs(out_port.y - in_port.y) + abs(out_port.x - in_port.x)

            # Bonus for center alignment - but only if there are no collision risks
            alignment_bonus = 0
            if abs(src_center_y - dst_center_y) <= 2:  # Widgets are roughly aligned
                # We'll apply alignment bonus only if we're not in a high-collision scenario
                # (i.e., if the basic distance is reasonable)
                if distance <= 50:  # Only apply alignment bonus for reasonably close widgets
                    if out_port.y == src_center_y and in_port.y == dst_center_y:
                        alignment_bonus = -30  # Moderate bonus for perfect center alignment
                    elif out_port.y == src_center_y or in_port.y == dst_center_y:
                        alignment_bonus = -15  # Smaller bonus for partial center alignment

            # Penalty for conflicts with existing connections
            conflict_penalty = 0
            for existing_out, existing_in in existing_connections:
                # Only penalize if ports are at exactly the same position (actual collision)
                if (out_port.y == existing_out.y and in_port.y == existing_in.y):
                    conflict_penalty += 50  # Heavy penalty for exact collisions
                # Light penalty for very close connections (within 1 unit)
                elif (abs(out_port.y - existing_out.y) <= 1 and
                      abs(in_port.y - existing_in.y) <= 1):
                    conflict_penalty += 5  # Light penalty for nearby connections

            score = distance + conflict_penalty + alignment_bonus

            if score < best_score:
                best_score = score
                best_pair = (out_port, in_port)

    # Fallback to default hotspots if no ports found
    if best_pair is None:
        src_in, src_out = link_hotspots(src_rect)
        dst_in, dst_out = link_hotspots(dst_rect)
        best_pair = (src_out, dst_in)

    return best_pair


def compute_positions(layers: LayerModel,
                      links: List[Tuple[Widget, Widget]],
                      layer_spacing: int = 5,
                      max_optimization_iterations: int = 50) -> Mapping[Widget, Rectangle]:
    """Efficiently compute widget positions using greedy algorithm with iterative improvement."""

    # Calculate the minimum height of all layers
    layer_min_heights = []
    widgets = []

    for layer in layers.get_layers():
        height = 0
        for widget in layer:
            height += widget.preferred_size().height
            widgets.append(widget)
        layer_min_heights.append(height)

    if not widgets:
        return {}

    layer_gaps = [max(layer_min_heights) - h for h in layer_min_heights]

    # Reserve space to avoid crossing widgets
    # For links that span multiple layers, we need to ensure enough vertical space
    # for the link to go above or below intermediate widgets
    for w1, w2 in links:
        pos1 = layers.find_item_position(w1)
        pos2 = layers.find_item_position(w2)

        if pos1 is None or pos2 is None:
            continue

        layer_1, layer_2 = pos1[0], pos2[0]

        if layer_1 + 1 < layer_2:
            # For multi-layer links, we need significant vertical separation
            # The amount depends on how many layers the link spans
            layers_spanned = layer_2 - layer_1 - 1

            # Base space needed for the link itself (minimum 2 lines: one for routing, one for spacing)
            base_link_space = 3

            # Additional space for complex routing scenarios
            additional_space = layers_spanned * 2

            link_spacing_needed = base_link_space + additional_space

            # Apply this spacing to ALL intermediate layers
            for mid_layer in range(layer_1 + 1, layer_2):
                layer_gaps[mid_layer] += link_spacing_needed

    # Use greedy algorithm instead of brute force
    return _compute_positions_greedy(layers, links, widgets, layer_gaps, layer_spacing,
                                     max_optimization_iterations)


def _compute_positions_greedy(layers: LayerModel,
                              links: List[Tuple[Widget, Widget]],
                              widgets: List[Widget],
                              layer_gaps: List[int],
                              layer_spacing: int,
                              max_optimization_iterations: int = 50) -> Mapping[Widget, Rectangle]:
    """Greedy algorithm for position optimization with iterative improvement."""

    # Initialize with strategic positioning to avoid long-distance link collisions
    widget_offsets = {}

    # Identify long-distance links that span multiple layers
    long_distance_links = []
    for w1, w2 in links:
        pos1 = layers.find_item_position(w1)
        pos2 = layers.find_item_position(w2)
        if pos1 and pos2 and pos1[0] + 1 < pos2[0]:
            long_distance_links.append((w1, w2, pos1[0], pos2[0]))

    for layer_index, layer in enumerate(layers.get_layers()):
        available_gap = layer_gaps[layer_index]
        widgets_in_layer = len(layer)

        if widgets_in_layer == 0:
            continue

        # Check if this layer has widgets that are sources/destinations of long-distance links
        has_long_distance_source = any(w1 for w1, w2, l1, l2 in long_distance_links if l1 == layer_index)
        has_long_distance_dest = any(w2 for w1, w2, l1, l2 in long_distance_links if l2 == layer_index)
        is_intermediate_layer = any(l1 < layer_index < l2 for w1, w2, l1, l2 in long_distance_links)

        if is_intermediate_layer:
            # For intermediate layers, position widgets lower to make room for long-distance links above
            base_offset = available_gap // 2  # Start from middle of available space
            gap_per_widget = (available_gap - base_offset) // widgets_in_layer if widgets_in_layer > 0 else 0

            for i, widget in enumerate(layer):
                widget_offsets[widget] = base_offset + i * gap_per_widget

        elif has_long_distance_source or has_long_distance_dest:
            # For source/destination layers of long-distance links, keep widgets near the top
            gap_per_widget = min(available_gap // 4,
                                 available_gap // widgets_in_layer) if widgets_in_layer > 0 else 0

            for i, widget in enumerate(layer):
                widget_offsets[widget] = i * gap_per_widget

        else:
            # Default: distribute gap evenly among widgets
            gap_per_widget = available_gap // widgets_in_layer if widgets_in_layer > 0 else 0

            for i, widget in enumerate(layer):
                widget_offsets[widget] = i * gap_per_widget

    # Compute initial positions
    best_positions = compute_widget_positions(layers, widget_offsets, layer_spacing)
    best_score = _evaluate_positions(best_positions, links)

    # Iterative improvement: try to improve positions by adjusting offsets
    max_iterations = min(max_optimization_iterations, len(widgets) * 5)  # Limit iterations for performance
    improved = True
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        # Try adjusting each widget's offset
        for widget in widgets:
            current_offset = widget_offsets[widget]
            widget_layer = layers.find_item_position(widget)[0]
            max_offset = layer_gaps[widget_layer]

            # Try adjustments - start with small ones, then try larger ones if there are collisions
            deltas = [-2, -1, 1, 2, -4, -3, 3, 4, -6, -5, 5, 6] if best_score >= LARGE_VALUE / 2 else [-2, -1,
                                                                                                       1, 2]

            for delta in deltas:
                new_offset = current_offset + delta
                if 0 <= new_offset <= max_offset:
                    # Test this adjustment
                    widget_offsets[widget] = new_offset
                    new_positions = compute_widget_positions(layers, widget_offsets, layer_spacing)
                    new_score = _evaluate_positions(new_positions, links)

                    if new_score < best_score:
                        best_score = new_score
                        best_positions = new_positions
                        improved = True
                        break  # Accept first improvement for this widget
                    else:
                        # Revert the change
                        widget_offsets[widget] = current_offset

    return best_positions


def _evaluate_positions(positions: Mapping[Widget, Rectangle],
                        links: List[Tuple[Widget, Widget]]) -> float:
    """Evaluate the quality of a position assignment."""
    total_score = 0.0

    for w1, w2 in links:
        a1 = w1.get_ancestor()
        a2 = w2.get_ancestor()

        if a1 not in positions or a2 not in positions:
            continue

        p1 = positions[a1]
        p2 = positions[a2]
        h1 = link_hotspots(p1)[1]
        h2 = link_hotspots(p2)[0]

        # Create the actual path that would be drawn
        path = Path(h1, h2)

        # Heavy penalty for path collisions with intermediate widgets
        if path_collides_with_widgets(path, positions, a1, a2):
            total_score += LARGE_VALUE
        else:
            # Quadratic penalty for vertical distance (encourages straight lines)
            vertical_distance = abs(h2.y - h1.y)
            total_score += vertical_distance ** 2

    return total_score
