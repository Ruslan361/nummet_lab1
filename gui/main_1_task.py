from PySide6.QtWidgets import QCheckBox, QApplication, QPushButton, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QDoubleSpinBox, QVBoxLayout, QLineEdit, QLabel, QDialog, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QDoubleValidator, QIntValidator
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import sys
import json
import os
import typing
import ctypes
import platform
import subprocess
import pandas as pd
from RK import l1_1, l1_test  # Импортируем оба класса
from custom_loyauts import LatexRendererLayout, GraphLayout, IntNumberInput, FloatNumberInput, NumericalIntegrationParametersInput, ScalarStartConditions, XlimitsInput, NewWindow

# ... (остальные классы: CPPDynamicLibrary, CSVReaderPandas, l1_1, l1_test,
# GraphLayout, LatexRendererLayout, MatplotlibGraph, MatplolibLatexRenderer,
# ErrorDialog, FloatNumberInput, IntNumberInput, ScalarStartConditions,
# NumericalIntegrationParametersInput, XlimitsInput)


class TabMainTask1(QWidget):
    def __init__(self):
        super().__init__()
        mainLayout = QVBoxLayout()
        self.RK = l1_1()  # Инициализируем l1_1

        testTaskLayout = LatexRendererLayout()
        texTask1 = r"$\frac{d^2 u}{dx} = \frac{x}{1 + x^2} \cdot u^2 + u - u^3 \cdot \sin{10x}$"
        testTaskLayout.render(texTask1)
        mainLayout.addLayout(testTaskLayout, 1)

        self.initialConditions = ScalarStartConditions()
        mainLayout.addLayout(self.initialConditions)

        self.xlimitsInput = XlimitsInput()
        mainLayout.addLayout(self.xlimitsInput)

        self.numericalIntegrationParametersInput = NumericalIntegrationParametersInput()
        mainLayout.addLayout(self.numericalIntegrationParametersInput)

        calculatePushButton = QPushButton()
        calculatePushButton.setText("Начать вычисления")
        mainLayout.addWidget(calculatePushButton)
        calculatePushButton.clicked.connect(self.calculateClick)


        self.amountOfStepsInput = IntNumberInput("Количество шагов")
        mainLayout.addLayout(self.amountOfStepsInput)

        self.graph = GraphLayout()
        mainLayout.addLayout(self.graph, 3)

        aboutLoyaut = QHBoxLayout()
        referenceButton = QPushButton()
        referenceButton.setText("Справка")
        referenceButton.clicked.connect(self.referenceButtonClick)
        aboutLoyaut.addWidget(referenceButton)
        ShowTableButton = QPushButton()
        ShowTableButton.setText("Вывести таблицу")
        ShowTableButton.clicked.connect(self.ShowTableButtonClick)
        aboutLoyaut.addWidget(ShowTableButton)

        # Сохранение и загрузка настроек (по аналогии с TabTestTask)
        saveSettingsButton = QPushButton()
        saveSettingsButton.setText("Сохранить настройки")
        saveSettingsButton.clicked.connect(self.saveSettings)
        aboutLoyaut.addWidget(saveSettingsButton)
        loadSettingsButton = QPushButton()
        loadSettingsButton.setText("Загрузить настройки")
        loadSettingsButton.clicked.connect(self.loadSettings)
        aboutLoyaut.addWidget(loadSettingsButton)

        mainLayout.addLayout(aboutLoyaut)

        self.setLayout(mainLayout)

        self.settings_file = "main_task_1.json"  # Отдельный файл для настроек
        self.loadSettings()
        self.tryLoadResult(self.to_be_control_local_error)

    def refreshPlot(self):
        self.tryLoadResult(self.to_be_control_local_error)
        self.graph.clear()

        self.graph.plot(self.x_, self.v, label="Численное решение")

        self.graph.set_title("График решения")
        self.graph.set_xlabel("x")
        self.graph.set_ylabel("u(x)")
        self.graph.legend()
        self.graph.draw()

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()

    def ShowTableButtonClick(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("Таблица результатов")
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        layout.addWidget(table)

        table.setColumnCount(len(self.columns))
        table.setRowCount(len(self.data))
        table.setHorizontalHeaderLabels(self.columns)

        for row, data_row in enumerate(self.data):
            for col, value in enumerate(data_row):
                item = QTableWidgetItem(str(value))
                table.setItem(row, col, item)

        dialog.exec()

    def referenceButtonClick(self):
        try:
            if self.to_be_control_local_error:
                df = pd.read_csv("output/output_1.csv", delimiter=";", header=None,
                                 names=['x', 'v', 'v2i', 'v-v2i', 'E', 'h', 'c1', 'c2'])
            else:
                df = pd.read_csv("output/output_1.csv", delimiter=";", header=None, names=['x', 'v'])

            report = ""
            amountOfIterations = len(df['x']) - 1
            report += f"Количество итераций: {amountOfIterations} \n"
            x = self.getColumnValues(df, 'x')
            l = len(x)
            difference_between_the_right_border_and_the_last_calculated_point = abs(
                x[l - 1] - self.xlimitsInput.getEndX())
            report += f'разница между правой границей и последней вычисленной точки: {difference_between_the_right_border_and_the_last_calculated_point}\n'
            if self.to_be_control_local_error:
                E = self.getColumnValues(df, 'E')
                maxError = max(E)
                report += f'Максимальное значение ОЛП {maxError}\n'
                doubling = self.getColumnValues(df, 'c2')
                countOfDoubling = sum(doubling)
                report += f'Количество удвоений {countOfDoubling}\n'
                doubling = self.getColumnValues(df, 'c1')
                countOfDoubling = sum(doubling)
                report += f'Количество делений {countOfDoubling}\n'
                h = self.getColumnValues(df, 'h')
                maxStep = max(h)
                minStep = min(h)
                xMinStep = h.index(minStep)
                xMinStep = x[xMinStep]
                xMaxStep = h.index(maxStep)
                xMaxStep = x[xMaxStep]
                report += f'максимальный шаг {maxStep} при x={xMaxStep}\n'
                report += f'Минимальный шаг {minStep} при x={xMinStep}\n'


            window = NewWindow('Справка', report)
            window.show()
            window.exec()
        except Exception as e:
            print(f"Ошибка во время анализа: {e}", file=sys.stderr)

            #window.exec()

    def calculateClick(self):
        x_end = self.xlimitsInput.getEndX()
        x0 = self.initialConditions.getX0()
        u_x0 = self.initialConditions.getUX0()
        epsilon_border = self.xlimitsInput.getEndEpsilon()
        amountOfSteps = self.amountOfStepsInput.getIntNumber()
        h0 = self.numericalIntegrationParametersInput.getStartStep()
        local_error = self.numericalIntegrationParametersInput.getEpsilonLocalError()
        self.to_be_control_local_error = self.numericalIntegrationParametersInput.isControlLocalError()

        if x_end <= x0:
            print("Ошибка: Конечное значение X должно быть больше начального.", file=sys.stderr)
            return

        if amountOfSteps <= 0:
            print("Ошибка: Количество шагов должно быть положительным числом.", file=sys.stderr)
            return

        if h0 <= 0:
            print("Ошибка: Начальный шаг должен быть положительным числом.", file=sys.stderr)
            return

        if local_error <= 0:
            print("Ошибка: Допустимая локальная погрешность должна быть положительным числом.", file=sys.stderr)
            return

        if self.to_be_control_local_error:
            self.RK.rk4_adaptive(x0, u_x0, h0, x_end, local_error, epsilon_border, amountOfSteps)
        else:
            self.RK.rk_4(x0, u_x0, h0, x_end, amountOfSteps)

        self.tryLoadResult(self.to_be_control_local_error)
        self.refreshPlot()

    def tryLoadResult(self, to_be_control_local_error):
        try:
            if to_be_control_local_error:
                df = pd.read_csv("output/output_1.csv", delimiter=";", header=None,
                                 names=['x', 'v', 'v2i', 'v-v2i', 'E', 'h', 'c1', 'c2'])
                self.setXUV(df)
                self.columns = ['x', 'v', 'v2i', 'v-v2i', 'E', 'h', 'c1', 'c2']
                self.data = df[self.columns][1:].values.tolist()  # Данные для таблицы
            else:
                df = pd.read_csv("output/output_1.csv", delimiter=";", header=None, names=['x', 'v'])
                self.setXUV(df)
                self.columns = ['x', 'v']
                self.data = df[self.columns][1:].values.tolist()  # Данные для таблицы

        except Exception as e:
            print(f"Ошибка во время загрузки: {e}", file=sys.stderr)

    def setXUV(self, df):
        self.x_ = self.getColumnValues(df, 'x')
        self.v = self.getColumnValues(df, 'v')
        minlen = min(len(self.x_), len(self.v))
        self.x_ = self.x_[:minlen]
        self.v = self.v[:minlen]

    def getColumnValues(self, df, column):
        return pd.to_numeric(df[column][1:], errors='coerce').dropna().tolist()

    def saveSettings(self):
        settings = {
            "initialConditions": {
                "X0": self.initialConditions.X0Input.floatNumberLineEdit.text(),
                "UX0": self.initialConditions.UX0Input.floatNumberLineEdit.text()
            },
            "xlimits": {
                "endX": self.xlimitsInput.endXInput.floatNumberLineEdit.text(),
                "epsilonBorder": self.xlimitsInput.epsilonBorderInput.floatNumberLineEdit.text()
            },
            "numericalIntegrationParameters": {
                "h0": self.numericalIntegrationParametersInput.h0Input.floatNumberLineEdit.text(),
                "controlLocalError": self.numericalIntegrationParametersInput.controlLocalErrorCheckBox.isChecked(),
                "epsilon": self.numericalIntegrationParametersInput.epsilonInput.floatNumberLineEdit.text(),
                "to_be_control_local_error": self.to_be_control_local_error
            },
            "amountOfSteps": self.amountOfStepsInput.intNumberLineEdit.text()
        }

        try:
            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=4)
            print(f"Настройки сохранены в файл {self.settings_file}")
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}", file=sys.stderr)

    def loadSettings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)

                self.initialConditions.X0Input.floatNumberLineEdit.setText(settings["initialConditions"]["X0"])
                self.initialConditions.UX0Input.floatNumberLineEdit.setText(settings["initialConditions"]["UX0"])
                self.xlimitsInput.endXInput.floatNumberLineEdit.setText(settings["xlimits"]["endX"])
                self.xlimitsInput.epsilonBorderInput.floatNumberLineEdit.setText(settings["xlimits"]["epsilonBorder"])
                self.numericalIntegrationParametersInput.h0Input.floatNumberLineEdit.setText(
                    settings["numericalIntegrationParameters"]["h0"])
                self.numericalIntegrationParametersInput.controlLocalErrorCheckBox.setChecked(
                    settings["numericalIntegrationParameters"]["controlLocalError"])
                self.numericalIntegrationParametersInput.epsilonInput.floatNumberLineEdit.setText(
                    settings["numericalIntegrationParameters"]["epsilon"])
                self.amountOfStepsInput.intNumberLineEdit.setText(settings["amountOfSteps"])
                self.numericalIntegrationParametersInput.setChecked(
                    settings["numericalIntegrationParameters"]["to_be_control_local_error"])
                self.to_be_control_local_error = settings["numericalIntegrationParameters"]["to_be_control_local_error"]
                print(f"Настройки загружены из файла {self.settings_file}")
            except Exception as e:
                print(f"Ошибка при загрузке настроек: {e}", file=sys.stderr)
        else:
            print(
                f"Файл настроек {self.settings_file} не найден. Будут использованы настройки по умолчанию.")

# ... (остальной код, например, создание главного окна и вкладок)