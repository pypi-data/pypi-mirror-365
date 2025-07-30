from typing import Any, List, Optional, Tuple

from pysciiart.widget import Container, Widget


class LayerModel:
    __layers: List[List[Any]]

    def __init__(self) -> None:
        self.__layers = [[]]

    def add(self, item: Widget) -> None:
        self.__layers[0].append(item)

    def find_item_position(self, needle: Widget) -> Optional[Tuple[int, int]]:
        for layer_index, layer in enumerate(self.__layers):
            for item_index, item in enumerate(layer):
                if item == needle or isinstance(item, Container) and item.contains(needle):
                    return layer_index, item_index

        return None

    def shift(self, item: Widget) -> None:
        position = self.find_item_position(item)
        if position is None:
            return
        item_layer_index, item_index = position

        if item_layer_index == len(self.__layers) - 1:
            self.__layers.append([])

        dropped = self.__layers[item_layer_index].pop(item_index)
        self.__layers[item_layer_index + 1].append(dropped)

    def get_layers(self) -> List[List[Any]]:
        return self.__layers
