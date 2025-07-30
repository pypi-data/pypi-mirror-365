# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Qt,
    QRect,
    QSize,
)
from PySide6.QtGui import (
    QCursor,
)
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QSizeGrip,
    QHBoxLayout,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# TYPE HINTS IMPROVEMENTS
from typing import Any

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class CustomGrip(QWidget):
    """
    Custom resize widget for windows.

    This class provides custom resize handles
    for different window edges (top, bottom, left, right).
    Each handle allows resizing the parent window.
    """

    def __init__(
        self, parent: QWidget, position: Qt.Edge, disable_color: bool = False
    ) -> None:
        """
        Initialize the resize handle.

        Parameters
        ----------
        parent : QWidget
            The parent widget to resize.
        position : Qt.Edge
            The position of the handle (Qt.TopEdge, Qt.BottomEdge, etc.).
        disable_color : bool, optional
            Disable handle colors (default: False).
        """
        # ////// SETUP UI
        super().__init__()
        self.parent = parent
        self.setParent(parent)
        self.wi = Widgets()

        # ////// SHOW TOP GRIP
        if position == Qt.TopEdge:
            self.wi.top(self)
            self.setGeometry(0, 0, self.parent.width(), 10)
            self.setMaximumHeight(10)

            # ////// SETUP GRIPS
            top_left = QSizeGrip(self.wi.top_left)
            top_right = QSizeGrip(self.wi.top_right)

            # ////// RESIZE TOP FUNCTION
            def resize_top(event: Any) -> None:
                delta = event.pos()
                height = max(
                    self.parent.minimumHeight(), self.parent.height() - delta.y()
                )
                geo = self.parent.geometry()
                geo.setTop(geo.bottom() - height)
                self.parent.setGeometry(geo)
                event.accept()

            self.wi.top.mouseMoveEvent = resize_top

            # ////// ENABLE COLOR
            if disable_color:
                self.wi.top_left.setStyleSheet("background: transparent")
                self.wi.top_right.setStyleSheet("background: transparent")
                self.wi.top.setStyleSheet("background: transparent")

        # ////// SHOW BOTTOM GRIP
        elif position == Qt.BottomEdge:
            self.wi.bottom(self)
            self.setGeometry(0, self.parent.height() - 10, self.parent.width(), 10)
            self.setMaximumHeight(10)

            # GRIPS
            self.bottom_left = QSizeGrip(self.wi.bottom_left)
            self.bottom_right = QSizeGrip(self.wi.bottom_right)

            # RESIZE BOTTOM
            def resize_bottom(event) -> None:
                delta = event.pos()
                height = max(
                    self.parent.minimumHeight(), self.parent.height() + delta.y()
                )
                self.parent.resize(self.parent.width(), height)
                event.accept()

            self.wi.bottom.mouseMoveEvent = resize_bottom

            # ENABLE COLOR
            # //////
            if disable_color:
                self.wi.bottom_left.setStyleSheet("background: transparent")
                self.wi.bottom_right.setStyleSheet("background: transparent")
                self.wi.bottom.setStyleSheet("background: transparent")

        # ////// SHOW LEFT GRIP
        elif position == Qt.LeftEdge:
            self.wi.left(self)
            self.setGeometry(0, 10, 10, self.parent.height() - 20)
            self.setMaximumWidth(10)

            # RESIZE LEFT
            def resize_left(event: Any) -> None:
                delta = event.pos()
                width = max(self.parent.minimumWidth(), self.parent.width() - delta.x())
                geo = self.parent.geometry()
                geo.setLeft(geo.right() - width)
                self.parent.setGeometry(geo)
                event.accept()

            self.wi.leftgrip.mouseMoveEvent = resize_left

            # ENABLE COLOR
            # //////
            if disable_color:
                self.wi.leftgrip.setStyleSheet("background: transparent")

        # RESIZE RIGHT
        # ///////////////////////////////////////////////////////////////
        elif position == Qt.RightEdge:
            self.wi.right(self)
            self.setGeometry(
                self.parent.width() - 10, 10, 10, self.parent.height() - 20
            )
            self.setMaximumWidth(10)

            def resize_right(event: Any) -> None:
                delta = event.pos()
                width = max(self.parent.minimumWidth(), delta.x())
                geo = self.parent.geometry()
                geo.setWidth(width)
                self.parent.setGeometry(geo)
                event.accept()

            self.wi.rightgrip.mouseMoveEvent = resize_right

            # ENABLE COLOR
            # //////
            if disable_color:
                self.wi.rightgrip.setStyleSheet("background: transparent")

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mouseReleaseEvent(self, event: Any) -> None:
        """Handle mouse release event."""
        self.mousePos = None

    # ///////////////////////////////////////////////////////////////

    def resizeEvent(self, event: Any) -> None:
        """Handle resize event."""
        if hasattr(self.wi, "container_top"):
            self.wi.container_top.setGeometry(0, 0, self.width(), 10)

        elif hasattr(self.wi, "container_bottom"):
            self.wi.container_bottom.setGeometry(0, 0, self.width(), 10)

        elif hasattr(self.wi, "leftgrip"):
            self.wi.leftgrip.setGeometry(0, 0, 10, self.height() - 20)

        elif hasattr(self.wi, "rightgrip"):
            self.wi.rightgrip.setGeometry(0, 0, 10, self.height() - 20)


# ///////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////


class Widgets:
    """
    Utility class for creating resize handle widgets.

    This class provides methods to create different types
    of handles (top, bottom, left, right) with their layouts and styles.
    """

    def top(self, Form: QWidget) -> None:
        """
        Create a resize handle for the top edge.

        Parameters
        ----------
        Form : QWidget
            The parent widget for the handle.
        """
        if not Form.objectName():
            Form.setObjectName("Form")

        # ////// SETUP CONTAINER
        self.container_top = QFrame(Form)
        self.container_top.setObjectName("container_top")
        self.container_top.setGeometry(QRect(0, 0, 500, 10))
        self.container_top.setMinimumSize(QSize(0, 10))
        self.container_top.setMaximumSize(QSize(16777215, 10))
        self.container_top.setFrameShape(QFrame.NoFrame)
        self.container_top.setFrameShadow(QFrame.Raised)

        # ////// SETUP LAYOUT
        self.top_layout = QHBoxLayout(self.container_top)
        self.top_layout.setSpacing(0)
        self.top_layout.setObjectName("top_layout")
        self.top_layout.setContentsMargins(0, 0, 0, 0)

        # ////// SETUP TOP LEFT GRIP
        self.top_left = QFrame(self.container_top)
        self.top_left.setObjectName("top_left")
        self.top_left.setMinimumSize(QSize(10, 10))
        self.top_left.setMaximumSize(QSize(10, 10))
        self.top_left.setCursor(QCursor(Qt.SizeFDiagCursor))
        self.top_left.setStyleSheet("background-color: rgb(33, 37, 43);")
        self.top_left.setFrameShape(QFrame.NoFrame)
        self.top_left.setFrameShadow(QFrame.Raised)
        self.top_layout.addWidget(self.top_left)

        # ////// SETUP TOP CENTER GRIP
        self.top = QFrame(self.container_top)
        self.top.setObjectName("top")
        self.top.setCursor(QCursor(Qt.SizeVerCursor))
        self.top.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.top.setFrameShape(QFrame.NoFrame)
        self.top.setFrameShadow(QFrame.Raised)
        self.top_layout.addWidget(self.top)

        # ////// SETUP TOP RIGHT GRIP
        self.top_right = QFrame(self.container_top)
        self.top_right.setObjectName("top_right")
        self.top_right.setMinimumSize(QSize(10, 10))
        self.top_right.setMaximumSize(QSize(10, 10))
        self.top_right.setCursor(QCursor(Qt.SizeBDiagCursor))
        self.top_right.setStyleSheet("background-color: rgb(33, 37, 43);")
        self.top_right.setFrameShape(QFrame.NoFrame)
        self.top_right.setFrameShadow(QFrame.Raised)
        self.top_layout.addWidget(self.top_right)

    # ///////////////////////////////////////////////////////////////

    def bottom(self, Form: QWidget) -> None:
        """
        Create a resize handle for the bottom edge.

        Parameters
        ----------
        Form : QWidget
            The parent widget for the handle.
        """
        if not Form.objectName():
            Form.setObjectName("Form")

        # ////// SETUP CONTAINER
        self.container_bottom = QFrame(Form)
        self.container_bottom.setObjectName("container_bottom")
        self.container_bottom.setGeometry(QRect(0, 0, 500, 10))
        self.container_bottom.setMinimumSize(QSize(0, 10))
        self.container_bottom.setMaximumSize(QSize(16777215, 10))
        self.container_bottom.setFrameShape(QFrame.NoFrame)
        self.container_bottom.setFrameShadow(QFrame.Raised)

        # ////// SETUP LAYOUT
        self.bottom_layout = QHBoxLayout(self.container_bottom)
        self.bottom_layout.setSpacing(0)
        self.bottom_layout.setObjectName("bottom_layout")
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)

        # ////// SETUP BOTTOM LEFT GRIP
        self.bottom_left = QFrame(self.container_bottom)
        self.bottom_left.setObjectName("bottom_left")
        self.bottom_left.setMinimumSize(QSize(10, 10))
        self.bottom_left.setMaximumSize(QSize(10, 10))
        self.bottom_left.setCursor(QCursor(Qt.SizeBDiagCursor))
        self.bottom_left.setStyleSheet("background-color: rgb(33, 37, 43);")
        self.bottom_left.setFrameShape(QFrame.NoFrame)
        self.bottom_left.setFrameShadow(QFrame.Raised)
        self.bottom_layout.addWidget(self.bottom_left)

        # ////// SETUP BOTTOM CENTER GRIP
        self.bottom = QFrame(self.container_bottom)
        self.bottom.setObjectName("bottom")
        self.bottom.setCursor(QCursor(Qt.SizeVerCursor))
        self.bottom.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.bottom.setFrameShape(QFrame.NoFrame)
        self.bottom.setFrameShadow(QFrame.Raised)
        self.bottom_layout.addWidget(self.bottom)

        # ////// SETUP BOTTOM RIGHT GRIP
        self.bottom_right = QFrame(self.container_bottom)
        self.bottom_right.setObjectName("bottom_right")
        self.bottom_right.setMinimumSize(QSize(10, 10))
        self.bottom_right.setMaximumSize(QSize(10, 10))
        self.bottom_right.setCursor(QCursor(Qt.SizeFDiagCursor))
        self.bottom_right.setStyleSheet("background-color: rgb(33, 37, 43);")
        self.bottom_right.setFrameShape(QFrame.NoFrame)
        self.bottom_right.setFrameShadow(QFrame.Raised)
        self.bottom_layout.addWidget(self.bottom_right)

    # ///////////////////////////////////////////////////////////////

    def left(self, Form: QWidget) -> None:
        """
        Create a resize handle for the left edge.

        Parameters
        ----------
        Form : QWidget
            The parent widget for the handle.
        """
        if not Form.objectName():
            Form.setObjectName("Form")

        # ////// SETUP LEFT GRIP
        self.leftgrip = QFrame(Form)
        self.leftgrip.setObjectName("left")
        self.leftgrip.setGeometry(QRect(0, 10, 10, 480))
        self.leftgrip.setMinimumSize(QSize(10, 0))
        self.leftgrip.setCursor(QCursor(Qt.SizeHorCursor))
        self.leftgrip.setStyleSheet("background-color: rgb(255, 121, 198);")
        self.leftgrip.setFrameShape(QFrame.NoFrame)
        self.leftgrip.setFrameShadow(QFrame.Raised)

    # ///////////////////////////////////////////////////////////////

    def right(self, Form: QWidget) -> None:
        """
        Create a resize handle for the right edge.

        Parameters
        ----------
        Form : QWidget
            The parent widget for the handle.
        """
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(500, 500)

        # ////// SETUP RIGHT GRIP
        self.rightgrip = QFrame(Form)
        self.rightgrip.setObjectName("right")
        self.rightgrip.setGeometry(QRect(0, 0, 10, 500))
        self.rightgrip.setMinimumSize(QSize(10, 0))
        self.rightgrip.setCursor(QCursor(Qt.SizeHorCursor))
        self.rightgrip.setStyleSheet("background-color: rgb(255, 0, 127);")
        self.rightgrip.setFrameShape(QFrame.NoFrame)
        self.rightgrip.setFrameShadow(QFrame.Raised)
