
import sys
import pandas as pd
import os
from pathlib import Path

from event_correlation_engine import EventCorrelationEngine
from constraints.existence_constraints import *
from constraints.relation_constraints import *
from constraints.mutual_relation_constraints import *
from constraints.negative_relation_constraints import *

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QFormLayout,
    QFileDialog,
    QLineEdit,
    QLabel,
    QTextEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 550
DISPLAY_HEIGHT = 35


# class PyCalcWindow(QMainWindow):
#     """PyCalc's main window (GUI or view)."""
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Event Correlation Engine")
#         self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
#         self.generalLayout = QVBoxLayout()
#
#         central_widget = QWidget(self)
#         central_widget.setLayout(self.generalLayout)
#         self.setCentralWidget(central_widget)
#
#         self._create_display()
#         # self._create_buttons()
#
#     def _create_display(self):
#         self.display = QLineEdit()
#         self.display.setFixedHeight(DISPLAY_HEIGHT)
#         self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
#         self.display.setReadOnly(True)
#         self.generalLayout.addWidget(self.display)

class Window(QWidget):

    def open_file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Import CSV",
            "",
            "CSV data files (*.csv)"
        )
        if filename:
            path = Path(filename)
            self.filename_edit.setText(str(path))

    def set_generate_button(self):
        start_event = {'attr': 'Activity', 'value': 'A'}
        case_name = "CaseID"
        timestamp_name = "Start Timestamp"

        # data_file = 'event_logs/check/data21.csv'
        data_file = self.filename_edit.text()

        constraints = [
            {'constraint': Existence,
             'e': {'attr': 'Activity', 'value': 'A'}},
            {'constraint': Existence,
             'e': {'attr': 'Activity', 'value': 'L'}},
            {'constraint': Existence,
             'e': {'attr': 'Activity', 'value': 'B'}},
            {'constraint': Existence,
             'e': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': Existence,
             'e': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': Existence,
             'e': {'attr': 'Activity', 'value': 'I'}},
            {'constraint': Existence,
             'e': {'attr': 'Activity', 'value': 'D'}},
            {'constraint': Absence,
             'e': {'attr': 'Activity', 'value': 'K'}},
            {'constraint': AlternateResponse,
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'D'}},
            {'constraint': AlternateResponse,
             'e': {'attr': 'Activity', 'value': 'C'},
             'e2': {'attr': 'Activity', 'value': 'D'}},
            {'constraint': Precedence,
             'e': {'attr': 'Activity', 'value': 'A'},
             'e2': {'attr': 'Activity', 'value': 'B'}},
            {'constraint': Precedence,
             'e': {'attr': 'Activity', 'value': 'A'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': Coexistence,
             'e': {'attr': 'Activity', 'value': 'B'},
             'e2': {'attr': 'Activity', 'value': 'C'}},
            {'constraint': ChainResponse,
             'e': {'attr': 'Activity', 'value': 'F'},
             'e2': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': ChainResponse,
             'e': {'attr': 'Activity', 'value': 'E'},
             'e2': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': ChainPrecedence,
             'e': {'attr': 'Activity', 'value': 'G'},
             'e2': {'attr': 'Activity', 'value': 'H'}},
            {'constraint': ChainPrecedence,
             'e': {'attr': 'Activity', 'value': 'I'},
             'e2': {'attr': 'Activity', 'value': 'J'}},
            {'constraint': NotChainSuccession,
             'e': {'attr': 'Activity', 'value': 'D'},
             'e2': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': NotSuccession,
             'e': {'attr': 'Activity', 'value': 'J'},
             'e2': {'attr': 'Activity', 'value': 'I'}},  # redundant?
            {'constraint': ChainPrecedence,
             'e': {'attr': 'Activity', 'value': 'J'},
             'e2': {'attr': 'Activity', 'value': 'K'}},
            {'constraint': RespondedExistence,
             'e': {'attr': 'Activity', 'value': 'F'},
             'e2': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': RespondedExistence,
             'e': {'attr': 'Activity', 'value': 'E'},
             'e2': {'attr': 'Activity', 'value': 'G'}},
            {'constraint': RespondedExistence,
             'e': {'attr': 'Activity', 'value': 'K'},
             'e2': {'attr': 'Activity', 'value': 'L'}},
            {'constraint': AlternatePrecedence,
             'e': {'attr': 'Activity', 'value': 'H'},
             'e2': {'attr': 'Activity', 'value': 'I'}},
            {'constraint': AlternatePrecedence,
             'e': {'attr': 'Activity', 'value': 'G'},
             'e2': {'attr': 'Activity', 'value': 'H'}}
        ]

        result, measures = EventCorrelationEngine(start_event, data_file, constraints).generate()

        self.text_edit.setText(str(result))
        self.text_edit2.setText(str(measures))

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Correlation Engine")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        grid_layout = QGridLayout()

        grid_layout2 = QGridLayout()

        # file selection
        file_button = QPushButton('Browse')
        file_button.clicked.connect(self.open_file_dialog)
        self.filename_edit = QLineEdit()

        grid_layout.addWidget(QLabel('Event log in csv:'), 0, 0)
        grid_layout.addWidget(self.filename_edit, 0, 1)
        grid_layout.addWidget(file_button, 0, 2)

        generate_button = QPushButton('Generate')

        grid_layout2.addWidget(generate_button, 0, 2)

        main_layout = QVBoxLayout()
        # text box
        self.text_edit = QTextEdit()
        self.text_edit2 = QTextEdit()

        grid_layout3 = QGridLayout()

        text_edit_label = QLabel("Assigned cases:")
        text_edit_label2 = QLabel("Measures:")
        grid_layout3.addWidget(text_edit_label, 0, 1)
        grid_layout3.addWidget(text_edit_label2, 0, 2)
        grid_layout3.addWidget(self.text_edit, 1, 1)
        grid_layout3.addWidget(self.text_edit2, 1, 2)

        generate_button.clicked.connect(self.set_generate_button)

        main_layout.addLayout(grid_layout)
        main_layout.addLayout(grid_layout2)
        main_layout.addLayout(grid_layout3)
        # main_layout.addWidget(self.text_edit)
        # main_layout.addWidget(self.text_edit2)

        # Set the layout on the application's window
        self.setLayout(main_layout)

        # layout.addRow("Job:", QLineEdit())
        # emailLabel = QLabel("Email:")
        # layout.addRow(emailLabel, QLineEdit())



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())




