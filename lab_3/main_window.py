import matplotlib
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.use("QtAgg")


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class EspressoExpertApp(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.setWindowTitle("Neylor System: Espresso Diagnostic")

        # Initialize the engine (make sure espresso_db.json exists)
        self.engine = engine

        # UI Setup
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.custom_layout = QVBoxLayout(self.main_widget)

        # Question Label
        self.question_label = QLabel("Click 'Start' to begin diagnostic")
        self.question_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 10px;"
        )
        self.question_label.setWordWrap(True)
        self.custom_layout.addWidget(self.question_label)

        # Chart
        self.canvas = MplCanvas(self, width=6, height=4)
        self.custom_layout.addWidget(self.canvas)

        # Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_yes = QPushButton("Да")
        self.btn_no = QPushButton("Нет")
        self.btn_skip = QPushButton("Не уверен")

        for btn in [self.btn_yes, self.btn_no, self.btn_skip]:
            btn.setMinimumHeight(40)
            self.btn_layout.addWidget(btn)

        self.custom_layout.addLayout(self.btn_layout)

        # Connect events
        self.btn_yes.clicked.connect(lambda: self.process_answer(True))
        self.btn_no.clicked.connect(lambda: self.process_answer(False))
        self.btn_skip.clicked.connect(self.process_skip)

        # Set initial state
        self.current_q = None
        self.update_chart()
        self.next_question()

    def update_chart(self):
        """
        Redraw the horizontal bar chart with pastel colors and improved spacing.
        Using barh (horizontal) is better for long Russian labels.
        """
        self.canvas.axes.cla()

        # Data preparation
        names = list(self.engine.hypotheses.keys())
        values = list(self.engine.hypotheses.values())

        # Soft pastel color palette
        # Light coffee, muted sage, dusty rose, etc.
        pastel_colors = [
            "#BCAAA4",
            "#A5D6A7",
            "#EF9A9A",
            "#90CAF9",
            "#CE93D8",
            "#FFF59D",
        ]

        # Highlight the leader with a slightly more saturated but still soft color
        max_val = max(values)
        colors = [
            pastel_colors[i % len(pastel_colors)] if v < max_val else "#922D0E"
            for i, v in enumerate(values)
        ]

        # Create horizontal bars
        self.canvas.axes.barh(
            names, values, color=colors, edgecolor="#5D4037", linewidth=0.5
        )

        # Styling the axes
        self.canvas.axes.set_xlim(0, 1.0)
        self.canvas.axes.set_title(
            "Вероятности диагнозов", fontsize=14, pad=15, color="#3E2723"
        )

        # Increase label size for "Borishchinova-proof" readability
        self.canvas.axes.tick_params(axis="y", labelsize=10)
        self.canvas.axes.tick_params(axis="x", labelsize=9)

        # Remove top and right spines for a modern look
        self.canvas.axes.spines["top"].set_visible(False)
        self.canvas.axes.spines["right"].set_visible(False)

        # Add thin grid for better estimation
        self.canvas.axes.xaxis.grid(True, linestyle="--", alpha=0.6)

        # Adjust layout to prevent label clipping
        self.canvas.fig.tight_layout()

        self.canvas.draw()

    def next_question(self):
        """Get the next best question from the engine."""
        self.current_q = self.engine.get_best_question()

        if self.current_q:
            self.question_label.setText(self.current_q["text"])
        else:
            best_h, prob = self.engine.get_top_hypothesis()
            self.question_label.setText(f"Result: {best_h} (Confidence: {prob:.1%})")
            self.btn_yes.setEnabled(False)
            self.btn_no.setEnabled(False)
            self.btn_skip.setEnabled(False)

    def process_skip(self):
        """Handle the 'Not Sure' button click."""
        if self.current_q:
            # Tell the engine to skip this evidence
            self.engine.skip_question(self.current_q["id"])
            # Chart update is not needed (probs didn't change), just move to next
            self.next_question()

    def process_answer(self, answer: bool):
        """Update engine and refresh UI."""
        if self.current_q:
            self.engine.update_probabilities(self.current_q["id"], answer)
            self.update_chart()
            self.next_question()
