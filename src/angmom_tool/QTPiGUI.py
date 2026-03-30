from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from angmom_tool.SelectionRules import find_allowed_l
from angmom_tool.Formatting import build_lowest_l_summary, build_report
from angmom_tool.Presets import (
    DEFAULT_GUI_VALUES,
    get_example_case,
    get_example_names,
    get_particle_names,
    get_particle_preset,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Angular Momentum Transfer Finder — Qt6")
        self.resize(1120, 820)
        self._build_ui()
        self._wire_signals()
        self.apply_default_values()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Allowed Angular Momentum Transfer Finder")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel(
            "Enter initial and final Jπ values, choose a transferred particle, "
            "and set the maximum l to check."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        input_box = QGroupBox("Inputs")
        input_layout = QGridLayout(input_box)
        input_layout.setHorizontalSpacing(16)
        input_layout.setVerticalSpacing(10)

        self.initial_edit = QLineEdit()
        self.final_edit = QLineEdit()
        self.spin_edit = QLineEdit()
        self.lmax_edit = QLineEdit()

        self.particle_combo = QComboBox()
        self.particle_combo.addItems(get_particle_names(include_custom=True))

        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["+", "-"])

        self.example_combo = QComboBox()
        self.example_combo.addItems(get_example_names())

        input_layout.addWidget(QLabel("Initial Jπ:"), 0, 0)
        input_layout.addWidget(self.initial_edit, 0, 1)
        input_layout.addWidget(QLabel("Final Jπ:"), 0, 2)
        input_layout.addWidget(self.final_edit, 0, 3)

        input_layout.addWidget(QLabel("Transferred particle:"), 1, 0)
        input_layout.addWidget(self.particle_combo, 1, 1)
        input_layout.addWidget(QLabel("Transferred spin s:"), 1, 2)
        input_layout.addWidget(self.spin_edit, 1, 3)

        input_layout.addWidget(QLabel("Transferred parity:"), 2, 0)
        input_layout.addWidget(self.parity_combo, 2, 1)
        input_layout.addWidget(QLabel("Maximum l to check:"), 2, 2)
        input_layout.addWidget(self.lmax_edit, 2, 3)

        input_layout.addWidget(QLabel("Quick example:"), 3, 0)
        input_layout.addWidget(self.example_combo, 3, 1)

        help_label = QLabel(
            "Accepted formats: Jπ like 1/2+, 3/2-, 2+, 0-. "
            "Choose a common transferred particle from the dropdown, "
            "or select custom to enter spin/parity manually."
        )
        help_label.setWordWrap(True)
        input_layout.addWidget(help_label, 4, 0, 1, 4)

        layout.addWidget(input_box)

        self.summary_label = QLabel("Ready")
        self.summary_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.summary_label.setStyleSheet(
            "QLabel { padding: 8px 10px; border-radius: 8px; background-color: #20242b; }"
        )
        layout.addWidget(self.summary_label)

        result_box = QGroupBox("Results")
        result_layout = QVBoxLayout(result_box)

        self.report_edit = QPlainTextEdit()
        self.report_edit.setReadOnly(True)

        report_font = QFont("Monospace")
        report_font.setStyleHint(QFont.StyleHint.TypeWriter)
        report_font.setPointSize(10)
        self.report_edit.setFont(report_font)
        self.report_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.report_edit.setPlainText(
            "Click 'Calculate' to compute allowed l values.\n\n"
            "This tool applies parity conservation and angular momentum coupling rules only."
        )

        result_layout.addWidget(self.report_edit)
        layout.addWidget(result_box, stretch=1)

        button_row = QHBoxLayout()
        self.calc_button = QPushButton("Calculate")
        self.copy_button = QPushButton("Copy Report")
        self.clear_button = QPushButton("Clear")

        button_row.addWidget(self.calc_button)
        button_row.addWidget(self.copy_button)
        button_row.addWidget(self.clear_button)
        button_row.addStretch(1)

        layout.addLayout(button_row)

    def _wire_signals(self) -> None:
        self.particle_combo.currentTextChanged.connect(self.update_particle_fields)
        self.example_combo.currentTextChanged.connect(self.apply_example)
        self.calc_button.clicked.connect(self.calculate)
        self.copy_button.clicked.connect(self.copy_report)
        self.clear_button.clicked.connect(self.clear_inputs)

    def apply_default_values(self) -> None:
        self.initial_edit.setText(DEFAULT_GUI_VALUES["initial_jpi"])
        self.final_edit.setText(DEFAULT_GUI_VALUES["final_jpi"])
        self.particle_combo.setCurrentText(DEFAULT_GUI_VALUES["particle"])
        self.spin_edit.setText(DEFAULT_GUI_VALUES["spin"])
        self.parity_combo.setCurrentText(DEFAULT_GUI_VALUES["parity"])
        self.lmax_edit.setText(DEFAULT_GUI_VALUES["l_max"])
        self.example_combo.setCurrentText(DEFAULT_GUI_VALUES["example"])
        self.update_particle_fields()

    def update_particle_fields(self) -> None:
        particle_name = self.particle_combo.currentText()
        preset = get_particle_preset(particle_name)

        if preset is not None:
            self.spin_edit.setText(preset["spin"])
            self.parity_combo.setCurrentText(preset["parity"])
            self.spin_edit.setEnabled(False)
            self.parity_combo.setEnabled(False)
        else:
            self.spin_edit.setEnabled(True)
            self.parity_combo.setEnabled(True)

    def apply_example(self, example_name: str) -> None:
        example = get_example_case(example_name)
        if example is None:
            return

        self.initial_edit.setText(example["initial_jpi"])
        self.final_edit.setText(example["final_jpi"])
        self.particle_combo.setCurrentText(example["particle"])
        self.spin_edit.setText(example["spin"])
        self.parity_combo.setCurrentText(example["parity"])
        self.lmax_edit.setText(example["l_max"])
        self.update_particle_fields()

    def calculate(self) -> None:
        try:
            transferred_parity = +1 if self.parity_combo.currentText() == "+" else -1
            l_max = int(self.lmax_edit.text().strip())

            result = find_allowed_l(
                jpi_initial=self.initial_edit.text(),
                jpi_final=self.final_edit.text(),
                transferred_spin=self.spin_edit.text(),
                transferred_parity=transferred_parity,
                l_max=l_max,
            )

            particle_name = self.particle_combo.currentText()
            self.report_edit.setPlainText(build_report(result, particle_name))
            self.summary_label.setText(build_lowest_l_summary(result))

        except Exception as exc:
            QMessageBox.critical(self, "Input error", str(exc))

    def copy_report(self) -> None:
        text = self.report_edit.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Nothing to copy", "There is no report to copy yet.")
            return

        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Report copied to clipboard.")

    def clear_inputs(self) -> None:
        blank = get_example_case("Blank")
        if blank is None:
            self.initial_edit.clear()
            self.final_edit.clear()
            self.particle_combo.setCurrentText("custom")
            self.spin_edit.clear()
            self.parity_combo.setCurrentText("+")
            self.lmax_edit.setText("8")
        else:
            self.initial_edit.setText(blank["initial_jpi"])
            self.final_edit.setText(blank["final_jpi"])
            self.particle_combo.setCurrentText(blank["particle"])
            self.spin_edit.setText(blank["spin"])
            self.parity_combo.setCurrentText(blank["parity"])
            self.lmax_edit.setText(blank["l_max"])

        self.update_particle_fields()
        self.report_edit.clear()
        self.summary_label.setText("Ready")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()