import math
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtGui import QPainter, QGuiApplication, QPixmap, QPen, QBrush, QPolygon
from PyQt6.QtCore import Qt, QPoint, QRect

from model import CaptureModel, RectangleShape, OvalShape, ArrowShape, TextShape
import view

class CaptureController:
    def __init__(self, model: CaptureModel):
        self.model = model
        self.view = None
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False

    def start_capture(self):
        """Capture the screen and show the View."""
        if getattr(self.model, 'is_capturing', False):
            return
            
        self.model.is_capturing = True
        
        # Grab the entire screen
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        
        # Reset the selection and shapes for a fresh capture
        self.model.selection_rect = QRect()
        self.model.shapes.clear()
        
        # Initialize and show the full-screen frameless view
        self.view = view.CaptureView(self.model, self)
        # Pass this screenshot (QPixmap) to the CaptureView before showing it
        self.view.set_screenshot(screenshot)
        self.view.showFullScreen()

    def cancel_capture(self):
        """Cancel capture mode, close the view, and reset state."""
        self.model.is_capturing = False
        if self.view:
            self.view.close()
            self.view = None

    def handle_mouse_press(self, event):
        """Update model.selection_rect start position."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = True
            self.start_pos = event.pos()
            # Initialize an empty rect at the click position
            self.model.selection_rect = QRect(self.start_pos, self.start_pos)
            self.view.update()

    def handle_mouse_move(self, event):
        """Update model.selection_rect during dragging."""
        if self.is_selecting:
            self.end_pos = event.pos()
            # Use normalized() so dragging up/left still forms a valid rectangle
            self.model.selection_rect = QRect(self.start_pos, self.end_pos).normalized()
            self.view.update()

    def handle_mouse_release(self, event):
        """Finish the selection rect."""
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.end_pos = event.pos()
            self.model.selection_rect = QRect(self.start_pos, self.end_pos).normalized()
            self.view.update()

    def _get_annotated_cropped_image(self) -> QPixmap:
        """Helper method to crop the selected area and apply annotations."""
        if self.model.selection_rect.isEmpty():
            return QPixmap()

        # Crop the selected area from the original background image
        cropped = self.model.original_pixmap.copy(self.model.selection_rect)
        
        # Apply annotations using QPainter onto the cropped image
        painter = QPainter(cropped)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Because annotations are stored in absolute screen coordinates,
        # we must translate the painter offset to match the cropped bounding box.
        painter.translate(-self.model.selection_rect.topLeft())
        
        for shape in self.model.shapes:
            if isinstance(shape, TextShape):
                pen = QPen(shape.color)
                painter.setPen(pen)
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
                painter.drawLine(shape.start_point, shape.end_point)
                
                dx = shape.end_point.x() - shape.start_point.x()
                dy = shape.end_point.y() - shape.start_point.y()
                angle = math.atan2(dy, dx)
                
                arrow_len = max(12, int(shape.thickness * 4.5))
                arrow_rad = math.pi / 6  
                
                p1 = QPoint(
                    int(shape.end_point.x() - arrow_len * math.cos(angle - arrow_rad)),
                    int(shape.end_point.y() - arrow_len * math.sin(angle - arrow_rad))
                )
                p2 = QPoint(
                    int(shape.end_point.x() - arrow_len * math.cos(angle + arrow_rad)),
                    int(shape.end_point.y() - arrow_len * math.sin(angle + arrow_rad))
                )
                painter.setBrush(QBrush(shape.color))
                painter.setPen(QPen(shape.color, 1))
                painter.drawPolygon(QPolygon([shape.end_point, p1, p2]))
                
        painter.end()
        return cropped

    def save_image(self):
        """Crop the selected area, apply annotations, and save as PNG."""
        annotated_image = self._get_annotated_cropped_image()
        
        if not annotated_image.isNull():
            # Prompt user for destination file path
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
                "Save Screenshot",
                "screenshot.png",
                "Images (*.png)"
            )
            
            if file_path:
                annotated_image.save(file_path, "PNG")
                self.cancel_capture()

    def copy_to_clipboard(self):
        """Copy the final annotated image to the system clipboard."""
        annotated_image = self._get_annotated_cropped_image()
        
        if not annotated_image.isNull():
            clipboard = QGuiApplication.clipboard()
            clipboard.setPixmap(annotated_image)
            
            self.cancel_capture()
