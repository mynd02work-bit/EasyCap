from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
from PyQt6.QtCore import Qt, QPoint, QRect
import math

from model import CaptureModel, RectangleShape, OvalShape, ArrowShape, TextShape

class CaptureView(QWidget):
    def __init__(self, model: CaptureModel, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        
        # Frameless window, stays on top, tool window (doesn't show in taskbar)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setMouseTracking(True)

    def set_screenshot(self, pixmap):
        self.model.original_pixmap = pixmap
        self.update()

    def mousePressEvent(self, event):
        self.controller.handle_mouse_press(event)

    def mouseMoveEvent(self, event):
        self.controller.handle_mouse_move(event)

    def mouseReleaseEvent(self, event):
        self.controller.handle_mouse_release(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.controller.cancel_capture()

    def paintEvent(self, event):
        if self.model.original_pixmap.isNull():
            return
            
        painter = QPainter(self)
        
        # Draw the background screenshot
        painter.drawPixmap(self.rect(), self.model.original_pixmap)

        # Draw semi-transparent dark overlay
        overlay_color = QColor(0, 0, 0, 120)
        
        s = self.model.selection_rect.normalized()
        r = self.rect()

        if s.width() > 0 and s.height() > 0:
            # Draw 4 rectangles around the selection to maintain the dark overlay while
            # keeping the selected region completely clear (bright)
            painter.fillRect(0, 0, r.width(), s.top(), overlay_color)
            painter.fillRect(0, s.bottom() + 1, r.width(), r.bottom() - s.bottom(), overlay_color)
            painter.fillRect(0, s.top(), s.left(), s.height(), overlay_color)
            painter.fillRect(s.right() + 1, s.top(), r.right() - s.right(), s.height(), overlay_color)
            
            # Draw a colored border around the active selection area
            painter.setPen(QPen(QColor(0, 150, 255), 2))
            painter.drawRect(s)
        else:
            # Full overlay if no selection has been made yet
            painter.fillRect(r, overlay_color)

        # Render all shapes stored in the model's shapes list
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for shape in self.model.shapes:
            if isinstance(shape, TextShape):
                pen = QPen(shape.color)
                painter.setPen(pen)
                # Drawing text within the defined rectangle
                painter.drawText(shape.rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, shape.text)
                continue
                
            pen = QPen(shape.color, getattr(shape, 'thickness', 2))
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            if isinstance(shape, RectangleShape):
                painter.drawRect(shape.rect)
            elif isinstance(shape, OvalShape):
                painter.drawEllipse(shape.rect)
            elif isinstance(shape, ArrowShape):
                self._draw_arrow(painter, shape)

    def _draw_arrow(self, painter: QPainter, arrow: ArrowShape):
        """Helper method to draw an arrow with a proper head."""
        painter.drawLine(arrow.start_point, arrow.end_point)
        
        # Calculate arrowhead coordinates
        dx = arrow.end_point.x() - arrow.start_point.x()
        dy = arrow.end_point.y() - arrow.start_point.y()
        angle = math.atan2(dy, dx)
        
        # Scale arrowhead based on line thickness
        arrow_len = max(12, int(arrow.thickness * 4.5))
        arrow_rad = math.pi / 6  # 30 degrees
        
        p1 = QPoint(
            int(arrow.end_point.x() - arrow_len * math.cos(angle - arrow_rad)),
            int(arrow.end_point.y() - arrow_len * math.sin(angle - arrow_rad))
        )
        p2 = QPoint(
            int(arrow.end_point.x() - arrow_len * math.cos(angle + arrow_rad)),
            int(arrow.end_point.y() - arrow_len * math.sin(angle + arrow_rad))
        )
        
        painter.setBrush(QBrush(arrow.color))
        # Draw the head as a solid polygon
        painter.setPen(QPen(arrow.color, 1))
        poly = QPolygon([arrow.end_point, p1, p2])
        painter.drawPolygon(poly)
