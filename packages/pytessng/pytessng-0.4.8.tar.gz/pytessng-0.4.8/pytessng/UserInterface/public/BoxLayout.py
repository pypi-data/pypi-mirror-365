from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox, QWidget, QLayout, QLayoutItem


class HBoxLayout(QHBoxLayout):
    """水平布局"""
    def __init__(self, elements: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_elements(elements)

    def add_elements(self, elements: list):
        for element in elements:
            if isinstance(element, QWidget):
                self.addWidget(element)
            elif isinstance(element, QLayout):
                self.addLayout(element)
            elif isinstance(element, QLayoutItem):
                self.addItem(element)
            elif isinstance(element, int):
                self.addStretch(element)
            else:
                raise TypeError(f"Unsupported type: {type(element)}. Expected QWidget or QLayout.")


class VBoxLayout(QVBoxLayout):
    """垂直布局"""
    def __init__(self, elements: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_elements(elements)

    def add_elements(self, elements: list):
        for element in elements:
            if isinstance(element, QWidget):
                self.addWidget(element)
            elif isinstance(element, QLayout):
                self.addLayout(element)
            elif isinstance(element, QLayoutItem):
                self.addItem(element)
            elif isinstance(element, int):
                self.addStretch(element)
            else:
                raise TypeError(f"Unsupported type: {type(element)}. Expected QWidget or QLayout.")


class GBoxLayout(QGroupBox):
    """分组布局"""
    def __init__(self, layout: QLayout, title: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(layout)
        if title:
            self.setTitle(title)
