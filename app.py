import sys
from typing import NoReturn, Optional

import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from backend import CrossAnalysisSolver


class App(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.input_prob_file: Optional[QLineEdit] = None
        self.input_cond_prob_file: Optional[QLineEdit] = None
        self.number_of_executions: Optional[QLineEdit] = None
        self.table_widget: Optional[QTableWidget] = None
        self.value: Optional[QLineEdit] = None
        self.init_ui()

    def init_ui(self) -> NoReturn:
        font_bold = QFont()
        font_bold.setBold(True)

        up = QFrame(self)
        up.setFrameShape(QFrame.StyledPanel)

        label_open_prob = QLabel("Файл з ймовірностями експертів", up)
        label_open_prob.move(2, 10)
        self.input_prob_file = QLineEdit(up)
        self.input_prob_file.setText("./data/pv_variant_3_probabilities.txt")
        self.input_prob_file.setFixedWidth(300)
        self.input_prob_file.move(300, 7)

        open_prob_file = QPushButton("...", up)
        open_prob_file.setCheckable(True)
        open_prob_file.move(620, 7)
        open_prob_file.clicked[bool].connect(self.open_prob_file_dialog)

        label_open_cond_prob = QLabel("Файл з умовними ймовірностями", up)
        label_open_cond_prob.move(2, 50)
        self.input_cond_prob_file = QLineEdit(up)
        self.input_cond_prob_file.setText("./data/pv_variant_3_cond_probabilities.txt")
        self.input_cond_prob_file.setFixedWidth(300)
        self.input_cond_prob_file.move(300, 45)

        open_cond_prob_file = QPushButton("...", up)
        open_cond_prob_file.setCheckable(True)
        open_cond_prob_file.move(620, 45)
        open_cond_prob_file.clicked[bool].connect(self.open_cond_prob_file_dialog)

        label_number_of_executions = QLabel("Кількість ітерацій", up)
        label_number_of_executions.move(2, 90)
        self.number_of_executions = QLineEdit(up)
        self.number_of_executions.setText("10000")
        self.number_of_executions.setFixedWidth(100)
        self.number_of_executions.move(170, 86)

        execute_button = QPushButton("Виконати", up)
        execute_button.move(450, 130)
        execute_button.clicked.connect(self.execute)

        value = QLabel("Інтегральний коефіціент достовірності", up)
        value.move(2, 180)
        self.value = QLineEdit(up)
        # self.value.setText("10000")
        self.value.setFixedWidth(100)
        self.value.move(365, 177)

        table_frame = QFrame(self)
        table_frame.setFrameShape(QFrame.StyledPanel)

        self.table_widget = QTableWidget(table_frame)
        self.table_widget.resize(1800, 525)
        self.table_widget.setRowCount(8)
        self.table_widget.setColumnCount(10)
        self.table_widget.move(0, 0)
        header = self.table_widget.horizontalHeader()
        for index in range(10):
            header.setSectionResizeMode(index, QHeaderView.ResizeToContents)
        for index in range(8):
            self.table_widget.setVerticalHeaderItem(index, QTableWidgetItem(f"e{index + 1}"))
        self.table_widget.setHorizontalHeaderItem(0, QTableWidgetItem(f"Середні оцінки \n ймовірностей експертів"))
        self.table_widget.setHorizontalHeaderItem(1, QTableWidgetItem(f"Відкалібровані \n ймовірності"))
        for index in range(8):
            self.table_widget.setHorizontalHeaderItem(index + 2, QTableWidgetItem(f"Сценарій {index + 1}"))

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(up)
        vertical_layout.addWidget(table_frame)
        self.setLayout(vertical_layout)

        self.setGeometry(150, 150, 1450, 600)
        self.setWindowTitle("Метод перехресного впливу")
        self.show()

    def open_prob_file_dialog(self) -> NoReturn:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        target_path = str(QFileDialog.getOpenFileName(self, "Виберіть файл", options=options)[0])
        if target_path:
            self.input_prob_file.setText(target_path)

    def open_cond_prob_file_dialog(self) -> NoReturn:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        target_path = str(QFileDialog.getOpenFileName(self, "Виберіть файл", options=options)[0])
        if target_path:
            self.input_cond_prob_file.setText(target_path)

    def execute(self) -> NoReturn:
        solver = CrossAnalysisSolver(
            probs_path=self.input_prob_file.text(), cond_probs_path=self.input_cond_prob_file.text(),
        )
        try:
            final_table, value = solver.solve(number_of_executions=int(self.number_of_executions.text()))

            for i in range(final_table.shape[0]):  # pylint: disable=E1136
                for j in range(2):
                    self.table_widget.setItem(i, j, QTableWidgetItem("%.3f" % final_table[i][j]))
            for i in range(final_table.shape[0]):  # pylint: disable=E1136
                for j in range(2, final_table.shape[1]):  # pylint: disable=E1136
                    main_part = "%.3f" % final_table[i][j]
                    if i != j - 2:
                        delta = final_table[i][j] - final_table[i][1]
                        sign = "+" if delta > 0 else "-"
                        main_part += f" ({sign} {np.abs(delta):.3f})"
                    self.table_widget.setItem(i, j, QTableWidgetItem(main_part))

                self.value.setText(f"{value:.3f}")
        except ValueError:
            print("Кількість ітерацій має бути цілим значенням")


def main() -> NoReturn:
    pyqt_application = QApplication(sys.argv)
    _ = App()
    sys.exit(pyqt_application.exec_())


if __name__ == "__main__":
    main()
