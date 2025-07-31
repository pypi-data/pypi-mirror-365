from typing import Any, List

import napari
import numpy as np
from napari.layers import Shapes
from napari.layers.base._base_constants import ActionType
from napari.layers.shapes._shape_list import ShapeList

from napari_nninteractive.layers.abstract_layer import BaseLayerClass


class CustomShapeList(ShapeList):
    """Custom list of shapes that disallows rotation, ensuring bounding boxes
    are always aligned with the grid.

    Attributes:
        ndisplay (int): The display dimensionality of the shapes.
    """

    # pass

    def rotate(self, index, angle, center=None):
        """Override rotation to prevent bounding boxes from rotating."""

    def shift(self, index, shift):
        pass

    def scale(self, index, scale, center=None):
        pass

    def flip(self, index, axis, center=None):
        pass


class LassoLayer(BaseLayerClass, Shapes):
    """
    A bounding box layer class that extends `BaseLayerClass` and `Shapes` with specific color
    management and interaction handling. This class manages the addition, removal, and color
    updating of bounding boxes and restricts rotation.
    """

    def __init__(self, shape, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_view = CustomShapeList(ndisplay=self._slice_input.ndisplay)
        self._data_view.slice_key = np.array(self._data_slice.point)[
            self._slice_input.not_displayed
        ]
        self._shape = shape

    def replace_color(self, _color: List[float]) -> None:
        """
        Replaces the color of the last added shape in the layer.

        Args:
            _color (List[float]): The RGBA color to apply to the edge and face of the last shape.
        """
        self._data_view.update_edge_color(len(self.data) - 1, _color)
        self._data_view.update_face_color(len(self.data) - 1, _color)

    def remove_last(self) -> None:
        """
        Removes the last shape in the layer along with associated colors and metadata.
        """
        index = [len(self.data) - 1]
        to_remove = sorted(index, reverse=True)
        self.events.data(
            value=self.data,
            action=ActionType.REMOVING,
            data_indices=tuple(
                index,
            ),
            vertex_indices=((),),
        )
        for ind in to_remove:
            self._data_view.remove(ind)

        self._feature_table.remove(index)
        self.text.remove(index)
        self._data_view._edge_color = np.delete(self._data_view._edge_color, index, axis=0)
        self._data_view._face_color = np.delete(self._data_view._face_color, index, axis=0)

    def run(self) -> None:
        """
        Finalizes the current operation, resets selected data, and completes drawing.
        """
        super().run()
        # self.selected_data.clear()
        # self._finish_drawing()

    def _add(self, data: Any, *args, **kwargs) -> None:
        """
        Adds a shape with specified colors, utilizing the current prompt's color settings.

        Args:
            data (Any): The shape data to add.
        """
        Shapes.add(
            self,
            data,
            *args,
            edge_color=self.colors[self.prompt_index],
            face_color=self.colors[self.prompt_index],
            **kwargs,
        )

    def remove_selected(self) -> None:
        super().remove_selected()
        # """Removes selected points if any."""
        # index = list(self.selected_data)
        # if not self._is_free and len(index) == 1 and index[0] == (len(self.data) - 1):
        #     super().remove_selected()
        #     self._is_free = True

    def _rotate_box(self, angle, center=(0, 0)) -> None:
        """Disable rotation by overriding the rotation function."""

    @Shapes.selected_data.setter
    def selected_data(self, selected_data: set) -> None:
        """
        Sets the selected data, restricting selection to the last added shape when the layer is occupied.

        Args:
            selected_data (set): The set of selected shapes' indices.
        """
        index = list(selected_data)
        if len(index) == 1 and index[0] == (len(self.data) - 1) and not self._is_free:
            Shapes.selected_data.fset(self, selected_data)
        else:
            Shapes.selected_data.fset(self, set())

    def get_last(self) -> Any:
        """
        Retrieves the last shape data added to the layer.

        Returns:
            Any: The data of the last added shape.
        """

        labels_shape = self._shape

        ind = self._data_view._z_order[::-1][0]
        polygon = self._data_view.shapes[ind]
        dim_not_displayed = int(polygon.dims_not_displayed[0])
        slice_id = int(self._data_view.slice_key[0])

        # Check if the shape has more than 2 dimensions (3D case)
        if polygon.data.shape[1] > 2:
            polygon_2d = np.delete(polygon.data, dim_not_displayed, axis=1)
        else:
            polygon_2d = polygon.data

        slice_shape = np.delete(labels_shape, dim_not_displayed)

        transformed_shape = napari.layers.shapes._shapes_models.polygon.Polygon(polygon_2d)
        mask_slice = transformed_shape.to_mask(slice_shape, zoom_factor=1, offset=(0, 0)).astype(
            np.uint8
        )
        mask = np.zeros(labels_shape, dtype=np.uint8)

        mask[(slice(None),) * dim_not_displayed + (slice_id,)] = mask_slice

        return mask
