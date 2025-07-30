from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from pysciiart.coordinates import Position, Size
from pysciiart.raster import Raster


@dataclass(frozen=True)
class Hints:
    size: Size


class Widget:
    def __init__(self) -> None:
        self._parent: Optional[Widget] = None

    def get_parent(self) -> Optional['Widget']:
        return self._parent

    def get_ancestor(self) -> 'Widget':
        if self._parent is None:
            return self
        else:
            return self._parent.get_ancestor()

    def set_parent(self, parent: 'Widget') -> None:
        if self._parent is not None:
            raise Exception('Parent already defined')
        self._parent = parent

    def render(self, hints: Hints = None) -> Raster:
        pass

    def preferred_size(self) -> Size:
        pass


class Container(Widget):
    def __init__(self, content: List[Widget]) -> None:
        super().__init__()
        self._content = content

        for c in content:
            c.set_parent(self)

    def contains(self, needle: Widget) -> bool:
        for content in self._content:
            if needle == content or isinstance(content, Container) and content.contains(needle):
                return True

        return False

    def get_offset(self, child: Widget) -> Position:
        raise Exception('Not implemented')


class Wrapper(Container):
    def __init__(self, component: Widget) -> None:
        super().__init__([component])


class Padding(Wrapper):
    def __init__(self, component: Widget, amount_tl: Size, amount_br: Size = None) -> None:
        super().__init__(component)
        self._component = component
        self._amount_tl = amount_tl
        self._amount_br = amount_br if amount_br is not None else amount_tl

    def preferred_size(self) -> Size:
        nested = self._component.preferred_size()
        return Size(nested.width + self._amount_tl.width + self._amount_br.width,
                    nested.height + self._amount_tl.height + self._amount_br.height)

    def render(self, hints: Hints = None) -> Raster:
        r = Raster()
        wrapper_size = self.preferred_size()

        for y in range(wrapper_size.height):
            for x in range(wrapper_size.width):
                r.write(x, y, ' ', self)

        cmp_raster = self._component.render()
        r.write(self._amount_tl.width, self._amount_tl.height, cmp_raster)

        return r


class Border(Wrapper):
    def __init__(self, component: Widget, title: str = '') -> None:
        self._component = Padding(component, Size(1, 0))
        super().__init__(self._component)
        self._title = title

    def preferred_size(self) -> Size:
        nested = self._component.preferred_size()
        return Size(nested.width + 2, nested.height + 2)

    def render(self, hints: Hints = None) -> Raster:
        cmp_raster = self._component.render()
        cmp_size = self._component.preferred_size()
        cmp_w, cmp_h = cmp_size.width, cmp_size.height

        if hints is not None:
            cmp_w, cmp_h = hints.size.width - 2, hints.size.height - 2

        min_width = 2 + len(self._title)
        width = max(min_width, cmp_w)

        r = Raster()

        for y in range(cmp_h + 2):
            r.write(0, y, '|', origin=self, color='white', attrs=['dark'])
            r.write(width + 1, y, '|', origin=self, color='white', attrs=['dark'])

        for x in range(width + 2):
            r.write(x, 0, '-', origin=self, color='white', attrs=['dark'])
            r.write(x, cmp_h + 1, '-', origin=self, color='white', attrs=['dark'])

        r.write(0, 0, '+', origin=self, color='white', attrs=['dark'])
        r.write(width + 1, 0, '+', origin=self, color='white', attrs=['dark'])
        r.write(0, cmp_h + 1, '+', origin=self, color='white', attrs=['dark'])
        r.write(width + 1, cmp_h + 1, '+', origin=self, color='white', attrs=['dark'])

        if len(self._title) > 0:
            r.write(2, 0, ' ' + self._title + ' ', origin=self, color='white')

        r.write(1, 1, cmp_raster)

        return r


class VBox(Container):
    def __init__(self, content: List[Widget]) -> None:
        super().__init__(content)

    def preferred_size(self) -> Size:
        w, h = 0, 0

        for content in self._content:
            ps = content.preferred_size()
            w = max(ps.width, w)
            h += ps.height

        return Size(w, h)

    def render(self, hints: Hints = None) -> Raster:
        r = Raster()
        max_width = self.preferred_size().width

        for content in self._content:
            hints = Hints(Size(max_width, content.preferred_size().height))
            contentraster = content.render(hints)
            r.write(0, r.size()[1], contentraster)

        return r


class HBox(Container):
    def __init__(self, content: List[Widget]) -> None:
        super().__init__(content)

    def preferred_size(self) -> Size:
        w, h = 0, 0

        for content in self._content:
            ps = content.preferred_size()
            w += ps.width
            h = max(ps.height, h)

        return Size(w, h)

    def render(self, hints: Hints = None) -> Raster:
        r = Raster()

        for content in self._content:
            hints = Hints(content.preferred_size())
            contentraster = content.render(hints)
            r.write(r.size()[0], 0, contentraster)

        return r


class Paragraph(Widget):
    def __init__(self, lines: List[str], color: str = None, attrs: List[str] = None) -> None:
        super().__init__()
        self._lines = lines
        self._color = color
        self._attrs = attrs

    def preferred_size(self) -> Size:
        return Size(max([len(line) for line in self._lines]), len(self._lines))

    def render(self, hints: Hints = None) -> Raster:
        r = Raster()

        for line in self._lines:
            r.write(0, r.size()[1], line, origin=self, color=self._color, attrs=self._attrs)

        return r


class Links(Widget):
    def __init__(self, left: Widget, right: Widget,
                 links: List[Tuple[Widget, Widget]],
                 align: bool = False) -> None:
        super().__init__()
        self._left = left
        self._right = right
        self._links = links
        self._align = align

    def preferred_size(self) -> Size:
        return HBox([self._left, self._right]).preferred_size()

    def render(self, hints: Hints = None) -> Raster:
        dy_values = []
        dy_average = 0
        root = HBox([self._left, self._right])
        raster = root.render(hints)

        for w_src, w_dst in self._links:
            dst_x, dst_y, src_x, src_y = self._compute_link_coords(raster, w_dst, w_src)
            raster.draw_line(src_x, src_y, dst_x, dst_y)
            dy_values.append(dst_y - src_y)

        if self._align and len(dy_values) > 0:
            dy_average = int(sum(dy_values) / len(dy_values))

        if dy_average != 0:
            if dy_average < 0:
                root = HBox([self._left, Padding(self._right, Size(0, -dy_average))])
            else:
                root = HBox([Padding(self._left, Size(0, dy_average)), self._right])

            raster = root.render(hints)

            for w_src, w_dst in self._links:
                dst_x, dst_y, src_x, src_y = self._compute_link_coords(raster, w_dst, w_src)
                raster.draw_line(src_x, src_y, dst_x, dst_y)
                dy_values.append(dst_y - src_y)

        return raster

    @staticmethod
    def _compute_link_coords(raster: Raster, w_dst: Widget, w_src: Widget) -> Tuple[int, int, int, int]:
        bounds_src = raster.origin_bounds(w_src)
        bounds_dst = raster.origin_bounds(w_dst)
        src_x = bounds_src.x + bounds_src.w
        src_y = int(bounds_src.y + bounds_src.h / 2) - 1
        dst_x = bounds_dst.x
        dst_y = int(bounds_dst.y + bounds_dst.h / 2) - 1
        return dst_x, dst_y, src_x, src_y


class Annotations(Widget):
    def __init__(self, content: Widget, annotations: List[Tuple[Widget, str, str, List[str]]]) -> None:
        super().__init__()
        self._content = Padding(content, Size(3, 0), Size(0, 0)) if len(annotations) > 0 else content
        self._annotations = annotations
        self._width = max([0] + [len(a[1]) for a in annotations])

    def preferred_size(self) -> Size:
        content_size = self._content.preferred_size()
        return Size(content_size.width + self._width, content_size.height)

    def render(self, hints: Hints = None) -> Raster:
        raster = Raster()
        raster.write(self._width, 0, self._content.render(hints))

        widget_annotations_map: Dict[Widget, List[Tuple[str, str, List[str]]]] = {}

        used_y = []

        for widget, annotation_text, color, attrs in self._annotations:
            if widget not in widget_annotations_map.keys():
                widget_annotations_map[widget] = []

            widget_annotations_map[widget].append((annotation_text, color, attrs))

        for widget, annotations in widget_annotations_map.items():
            bounds = raster.origin_bounds(widget)
            y = int(bounds.y + (bounds.h - len(annotations)) / 2)

            for annotation_text, color, attrs in annotations:
                while y in used_y:
                    y += 1

                used_y.append(y)

                raster.write(0, y, annotation_text, color=color, attrs=attrs)
                raster.write(self._width, y, ' ]-', color='white')
                raster.draw_line(self._width + 3, y, bounds.x - 1, y, color='white')

        return raster
