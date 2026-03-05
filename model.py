from PyQt6.QtCore import QRect, QPoint
from PyQt6.QtGui import QPixmap, QColor

class AnnotationShape:
    """Base class for all annotation shapes."""
    pass

class RectangleShape(AnnotationShape):
    def __init__(self, rect: QRect, color: QColor, thickness: int):
        self.rect = rect
        self.color = color
        self.thickness = thickness

class OvalShape(AnnotationShape):
    def __init__(self, rect: QRect, color: QColor, thickness: int):
        self.rect = rect
        self.color = color
        self.thickness = thickness

class ArrowShape(AnnotationShape):
    def __init__(self, start_point: QPoint, end_point: QPoint, color: QColor, thickness: int):
        self.start_point = start_point
        self.end_point = end_point
        self.color = color
        self.thickness = thickness

class TextShape(AnnotationShape):
    def __init__(self, rect: QRect, text: str, color: QColor):
        self.rect = rect
        self.text = text
        self.color = color

class CaptureModel:
    """Model class for Easy Cap (MVC pattern)."""
    def __init__(self):
        self.original_pixmap = QPixmap()
        self.selection_rect = QRect()
        self.drawing_color = QColor("red")  # Default drawing color
        self.pen_thickness = 2              # Default pen thickness
        self.is_capturing = False
        
        # List to store annotation objects like Rectangles, Ovals, Arrows, Text
        self.shapes = []
        
    def add_shape(self, shape: AnnotationShape):
        self.shapes.append(shape)
        
    def pop_shape(self):
        if self.shapes:
            return self.shapes.pop()
        return None

    def clear_shapes(self):
        self.shapes.clear()
