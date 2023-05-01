
import sys
import pandas as pd
import os
import json
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
    QFileDialog,
    QLineEdit,
    QLabel,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
DISPLAY_HEIGHT = 35


class Window(QWidget):

    def open_file_dialog(self):
        default_folder = "/Users/arinaulanova/PycharmProjects/pythonProject1/test_logs"
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Import CSV",
            default_folder,
            "CSV data files (*.csv)"
        )
        if filename:
            path = Path(filename)
            self.filename_edit.setText(str(path))

    def format_dict_to_text(self, dict):
        text = ""
        for key, val in dict.items():
            text += f"{key}: { val } \n"
        return text


    def set_generate_button(self):
        start_event = {'attr': 'Activity', 'value': 'A'}
        case_name = "CaseID"
        timestamp_name = "Start Timestamp"

        # data_file = 'event_logs2/check/data21.csv'
        data_file = self.filename_edit.text()

        text = self.text_edit_constr.toPlainText()
        json_constraints = json.loads(text)

        result, measures = EventCorrelationEngine(start_event, json_constraints).generate(data_file)

        self.text_edit_result.setText(self.format_dict_to_text(result))
        self.text_edit_measures.setText(self.format_dict_to_text(measures))

    def __init__(self):
        super().__init__()

        self.constraints = [
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "A"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "L"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "B"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "C"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "J"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "H"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "G"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "I"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "D"}},
            {"constraint": "Absence",
             "e": {"attr": "Activity", "value": "K"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "C"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "H"},
             "e2": {"attr": "Activity", "value": "I"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "L"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "C"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Response",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Response",
             "e": {"attr": "Activity", "value": "C"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Response",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Response",
             "e": {"attr": "Activity", "value": "I"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Coexistence",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "C"}},
            {"constraint": "Coexistence",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "Coexistence",
             "e": {"attr": "Activity", "value": "H"},
             "e2": {"attr": "Activity", "value": "I"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "H"},
             "e2": {"attr": "Activity", "value": "I"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "I"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "NotChainSuccession",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "NotSuccession",
             "e": {"attr": "Activity", "value": "L"},
             "e2": {"attr": "Activity", "value": "A"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "H"},
             "e2": {"attr": "Activity", "value": "I"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "K"},
             "e2": {"attr": "Activity", "value": "L"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "C"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "AlternatePrecedence",  # I no(J) J
             "e": {"attr": "Activity", "value": "I"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "AlternatePrecedence",  # I no(J) J
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "L"}},
            {"constraint": "AlternatePrecedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}}
        ]

        self.constraints = [
            # {"constraint": "Existence",
            #  "e": {"attr": "Activity", "value": "A"}},
            # {"constraint": "Existence",
            #  "e": {"attr": "Activity", "value": "L"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "B"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "C"}},
            # {"constraint": "Existence",
            #  "e": {"attr": "Activity", "value": "G"}},
            # {"constraint": "Existence",
            #  "e": {"attr": "Activity", "value": "I"}},
            {"constraint": "Existence",
             "e": {"attr": "Activity", "value": "D"}},
            {"constraint": "Absence",
             "e": {"attr": "Activity", "value": "K"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "AlternateResponse",
             "e": {"attr": "Activity", "value": "C"},
             "e2": {"attr": "Activity", "value": "D"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Precedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "Response",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Response",
             "e": {"attr": "Activity", "value": "I"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "Coexistence",
             "e": {"attr": "Activity", "value": "B"},
             "e2": {"attr": "Activity", "value": "C"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "ChainResponse",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "I"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "NotChainSuccession",
             "e": {"attr": "Activity", "value": "D"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "NotSuccession",
             "e": {"attr": "Activity", "value": "L"},
             "e2": {"attr": "Activity", "value": "A"}},
            {"constraint": "ChainPrecedence",
             "e": {"attr": "Activity", "value": "J"},
             "e2": {"attr": "Activity", "value": "K"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "F"},
             "e2": {"attr": "Activity", "value": "G"}},
            {"constraint": "RespondedExistence",
             "e": {"attr": "Activity", "value": "E"},
             "e2": {"attr": "Activity", "value": "G"}},
            # {"constraint": "RespondedExistence",
            #  "e": {"attr": "Activity", "value": "K"},
            #  "e2": {"attr": "Activity", "value": "L"}},
            {"constraint": "AlternatePrecedence",  # I no(J) J
             "e": {"attr": "Activity", "value": "I"},
             "e2": {"attr": "Activity", "value": "J"}},
            {"constraint": "AlternatePrecedence",
             "e": {"attr": "Activity", "value": "G"},
             "e2": {"attr": "Activity", "value": "H"}}
        ]

        self.setWindowTitle("Event Correlation Engine")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        grid_layout = QGridLayout()

        grid_layout2 = QGridLayout()

        # file selection
        file_button = QPushButton('Browse')
        file_button.clicked.connect(self.open_file_dialog)
        self.filename_edit = QLineEdit()
        # TODO remove next line
        self.filename_edit.setText('/Users/arinaulanova/PycharmProjects/pythonProject1/test_logs/data39.csv')

        grid_layout.addWidget(QLabel('Event log in csv format:'), 0, 0)
        grid_layout.addWidget(self.filename_edit, 0, 1)
        grid_layout.addWidget(file_button, 0, 2)

        generate_button = QPushButton('Generate')
        self.text_edit_constr = QTextEdit()

        grid_layout2.addWidget(QLabel('Enter constraints in json format:'), 0, 0)
        grid_layout2.addWidget(self.text_edit_constr, 1, 0)
        grid_layout2.addWidget(generate_button, 2, 0)

        # default constraints now
        self.text_edit_constr.setText(json.dumps(self.constraints, indent=1))

        main_layout = QVBoxLayout()
        # text box

        self.text_edit_result = QTextEdit()
        self.text_edit_measures = QTextEdit()

        grid_layout3 = QGridLayout()

        text_edit_label = QLabel("Assigned cases:")
        text_edit_label2 = QLabel("Measures:")
        grid_layout3.addWidget(text_edit_label, 0, 1)
        grid_layout3.addWidget(text_edit_label2, 0, 2)
        grid_layout3.addWidget(self.text_edit_result, 1, 1)
        grid_layout3.addWidget(self.text_edit_measures, 1, 2)

        generate_button.clicked.connect(self.set_generate_button)

        main_layout.addLayout(grid_layout)
        main_layout.addLayout(grid_layout2)
        main_layout.addLayout(grid_layout3)

        # Set the layout on the application's window
        self.setLayout(main_layout)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())




