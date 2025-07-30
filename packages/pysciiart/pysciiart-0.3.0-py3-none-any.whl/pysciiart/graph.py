from typing import Dict, List, Mapping, Tuple

from pysciiart.coordinates import Path, PathStep, Position, Rectangle
from pysciiart.graph_layer import LayerModel
from pysciiart.graph_solver import compute_positions, link_hotspots, select_best_ports
from pysciiart.raster import Raster
from pysciiart.widget import Container, Hints, Size, Widget

STEP_CHARS: Mapping[PathStep, str] = {PathStep.HORIZONTAL: "─", PathStep.VERTICAL: "│", PathStep.TURN: "┌"}

# Alternative character sets for different styles
STEP_CHARS_ASCII: Mapping[PathStep, str] = {PathStep.HORIZONTAL: "-", PathStep.VERTICAL: "|",
                                            PathStep.TURN: "+"}
STEP_CHARS_UNICODE: Mapping[PathStep, str] = {PathStep.HORIZONTAL: "─", PathStep.VERTICAL: "│",
                                              PathStep.TURN: "┌"}
STEP_CHARS_HEAVY: Mapping[PathStep, str] = {PathStep.HORIZONTAL: "━", PathStep.VERTICAL: "┃",
                                            PathStep.TURN: "┏"}

# Arrow styles
ARROW_STYLES = {
    'ascii': '>',
    'unicode': '→',
    'heavy': '▶',
    'double': '⇒',
}


class Graph(Widget):
    def __init__(self,
                 widgets: List[Widget],
                 links: List[Tuple[Widget, Widget]],
                 layer_spacing: int = 5,
                 link_style: str = 'ascii',
                 arrow_style: str = 'ascii',
                 smart_ports: bool = True,
                 max_optimization_iterations: int = 50):
        super().__init__()
        self._layers = LayerModel()
        self._links = links
        self._layer_spacing = layer_spacing
        self._smart_ports = smart_ports
        self._max_optimization_iterations = max_optimization_iterations

        # Set styling
        self._link_chars = self._get_link_chars(link_style)
        self._arrow_char = ARROW_STYLES.get(arrow_style, ARROW_STYLES['ascii'])

        # Validate that the graph is a DAG (no cycles)
        self._validate_acyclic(widgets, links)

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

        for _, layer in enumerate(self._layers.get_layers()):
            layer.sort(key=lambda wid: self._widget_sort_key(wid))

    def _get_link_chars(self, style: str) -> Mapping[PathStep, str]:
        """Get the character set for the specified link style."""
        style_map = {
            'ascii': STEP_CHARS_ASCII,
            'unicode': STEP_CHARS_UNICODE,
            'heavy': STEP_CHARS_HEAVY,
        }
        return style_map.get(style, STEP_CHARS_ASCII)

    def _get_path_char(self, step: PathStep, path: List[Tuple[PathStep, Position]], index: int) -> str:
        """Get the appropriate character for a path step, with better corner detection."""
        if step != PathStep.TURN:
            return self._link_chars[step]

        # For turns, determine the correct corner character based on direction
        prev_step = path[index - 1][0] if index > 0 else None
        next_step = path[index + 1][0] if index < len(path) - 1 else None

        # Use Unicode box-drawing characters for better corners
        if self._link_chars == STEP_CHARS_UNICODE:
            # Determine corner type based on direction
            if prev_step == PathStep.HORIZONTAL and next_step == PathStep.VERTICAL:
                # Check if going down or up
                if index < len(path) - 1:
                    curr_pos = path[index][1]
                    next_pos = path[index + 1][1]
                    if next_pos.y > curr_pos.y:
                        return "┐"  # Top-right corner (going down)
                    else:
                        return "┘"  # Bottom-right corner (going up)
            elif prev_step == PathStep.VERTICAL and next_step == PathStep.HORIZONTAL:
                # Check if coming from up or down
                if index > 0:
                    prev_pos = path[index - 1][1]
                    curr_pos = path[index][1]
                    if prev_pos.y < curr_pos.y:
                        return "└"  # Bottom-left corner (from up)
                    else:
                        return "┌"  # Top-left corner (from down)

        return self._link_chars[PathStep.TURN]

    def _validate_acyclic(self, widgets: List[Widget], links: List[Tuple[Widget, Widget]]) -> None:
        """Validate that the graph is acyclic using DFS-based cycle detection."""
        if not links:
            return

        def find_widget_in_list(needle: Widget, haystack: List[Widget]) -> bool:
            """Check if widget is in list or contained within a Container widget in the list."""
            for widget in haystack:
                if widget == needle:
                    return True
                if isinstance(widget, Container) and widget.contains(needle):
                    return True
            return False

        # Build adjacency list - include all referenced widgets
        all_widgets = set(widgets)
        for src, dst in links:
            if not find_widget_in_list(src, widgets):
                raise ValueError(f"Link source widget {src} not found in widgets list or containers")
            if not find_widget_in_list(dst, widgets):
                raise ValueError(f"Link destination widget {dst} not found in widgets list or containers")
            all_widgets.add(src)
            all_widgets.add(dst)

        graph: Dict[Widget, List[Widget]] = {widget: [] for widget in all_widgets}
        for src, dst in links:
            graph[src].append(dst)

        # DFS-based cycle detection using three colors:
        # WHITE (0): unvisited, GRAY (1): visiting, BLACK (2): visited
        color = dict.fromkeys(all_widgets,0)

        def dfs(widget: Widget, path: List[Widget]) -> None:
            if color[widget] == 1:  # Gray - back edge found (cycle)
                cycle_start = path.index(widget)
                cycle = path[cycle_start:] + [widget]
                cycle_str = " -> ".join(str(w) for w in cycle)
                raise ValueError(f"Graph contains a cycle: {cycle_str}")

            if color[widget] == 2:  # Black - already processed
                return

            color[widget] = 1  # Gray - mark as being processed
            path.append(widget)

            for neighbor in graph[widget]:
                dfs(neighbor, path)

            path.pop()
            color[widget] = 2  # Black - mark as processed

        # Check all nodes (handles disconnected components)
        for widget in all_widgets:
            if color[widget] == 0:  # WHITE - unvisited
                dfs(widget, [])

    def _widget_sort_key(self, widget: Widget) -> int:
        result = 0

        # Iterate on link sources
        for src in [link[0] for link in self._links if link[1] == widget]:
            source_position = self._layers.find_item_position(src)
            result += source_position[1]

        return result

    def preferred_size(self) -> Size:
        if not self._layers.get_layers() or not any(layer for layer in self._layers.get_layers()):
            return Size(0, 0)

        # Calculate positions to determine actual size needed
        positions = compute_positions(self._layers, self._links, self._layer_spacing,
                                      self._max_optimization_iterations)

        if not positions:
            return Size(0, 0)

        # Find the maximum x and y coordinates
        max_x = 0
        max_y = 0

        for rect in positions.values():
            max_x = max(max_x, rect.x + rect.width)
            max_y = max(max_y, rect.y + rect.height)

        return Size(max_x, max_y)

    def render(self, hints: Hints = None) -> Raster:
        r = Raster()

        positions: Mapping[Widget, Rectangle] = compute_positions(self._layers,
                                                                  self._links,
                                                                  self._layer_spacing,
                                                                  self._max_optimization_iterations)

        # Render all components

        for widget, position in positions.items():
            hints = Hints(position)
            content_raster = widget.render(hints)
            r.write(position.x, position.y, content_raster)

        # Draw links with improved styling and smart port selection

        # Track connections for smart port selection
        existing_connections: List[Tuple[Position, Position]] = []

        for l_from, l_to in self._links:
            rect_from = positions[l_from.get_ancestor()]
            rect_to = positions[l_to.get_ancestor()]

            if self._smart_ports:
                # Use smart port selection to minimize conflicts
                pos1, pos2 = select_best_ports(rect_from, rect_to, existing_connections)
                existing_connections.append((pos1, pos2))
            else:
                # Use default hotspots
                pos1 = link_hotspots(rect_from)[1]
                pos2 = link_hotspots(rect_to)[0]

            path = Path(pos1, pos2)

            # Draw path with better turn handling
            for i, (step, pos) in enumerate(path):
                char = self._get_path_char(step, path, i)
                r.write(pos.x, pos.y, char)

            # Draw arrow at the end
            if path:
                r.write(path[-1][1].x, path[-1][1].y, self._arrow_char)

        return r
