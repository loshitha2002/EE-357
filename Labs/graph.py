"""
Professional Lab Graph Tool (GrapherV1.5)
Added more Fit options (Poly 4th, Exponential) and a Remove Point button!
"""
import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGraphicsScene, QGraphicsView,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QDockWidget,
    QComboBox, QColorDialog, QSpinBox, QCheckBox, QFrame
)
from PyQt5.QtGui import QPen, QColor, QPainter, QBrush, QImage
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter
from scipy.interpolate import CubicSpline

# ---------- Graph Sheet Settings ----------
MM_TO_PX = 3.78
A4_WIDTH_MM = 180
A4_HEIGHT_MM = 250
WIDTH_PX = int(A4_WIDTH_MM * MM_TO_PX)
HEIGHT_PX = int(A4_HEIGHT_MM * MM_TO_PX)
SMALL_BOX_MM = 1
SMALL_BOX_PX = SMALL_BOX_MM * MM_TO_PX
BIG_BOX_COUNT = 10  # 1 cm boxes

class GraphData:
    """Store per-graph data."""
    def __init__(self):
        self.points = []
        self.line_color = QColor(0, 80, 200, 255)
        self.line_thickness = 2
        self.line_type = Qt.SolidLine
        self.show_curve = True
        self.fit_type = "Spline"  # Default fit type
        self.point_color = QColor(220, 20, 60)
        self.point_size = 8
        self.point_shape = "Circle"

class LabGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Lab Graph Tool")
        self.setGeometry(50, 50, WIDTH_PX + 480, HEIGHT_PX + 120)

        self.graphs = []
        self.current_graph_index = 0

        # Axis Starting Positions (Blocks)
        self.x_min, self.x_max = -2, 16
        self.y_min, self.y_max = -2, 23

        # Grid Colors
        self.grid_small_color = QColor(210, 235, 245)
        self.grid_mid_color = QColor(163, 209, 230)
        self.grid_big_color = QColor(122, 184, 211)
        self.grid_thickness = 1
        self.show_grid = True

        # Margins (mm)
        self.margin_top = 17
        self.margin_bottom = 30
        self.margin_left = 15
        self.margin_right = 15

        self.init_ui()
        self.add_new_graph()

    # -------------------- UI --------------------
    def init_ui(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, WIDTH_PX, HEIGHT_PX)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.wheelEvent = self.zoom_event

        dock = QDockWidget("Controls", self)
        dock_widget = QWidget()
        dock.setWidget(dock_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        layout = QVBoxLayout()

        # --- GRID & SCALE SETTINGS ---
        grid_frame = QFrame(); grid_frame.setFrameShape(QFrame.StyledPanel)
        grid_layout = QVBoxLayout(grid_frame)
        grid_layout.addWidget(QLabel("<b>1. Axis Position (Blocks)</b>"))
        
        axis_layout = QHBoxLayout()
        self.x_min_input = QLineEdit(str(self.x_min)); self.x_min_input.setFixedWidth(40)
        self.x_max_input = QLineEdit(str(self.x_max)); self.x_max_input.setFixedWidth(40)
        self.y_min_input = QLineEdit(str(self.y_min)); self.y_min_input.setFixedWidth(40)
        self.y_max_input = QLineEdit(str(self.y_max)); self.y_max_input.setFixedWidth(40)
        axis_layout.addWidget(QLabel("Xmin:")); axis_layout.addWidget(self.x_min_input)
        axis_layout.addWidget(QLabel("Xmax:")); axis_layout.addWidget(self.x_max_input)
        axis_layout.addWidget(QLabel("Ymin:")); axis_layout.addWidget(self.y_min_input)
        axis_layout.addWidget(QLabel("Ymax:")); axis_layout.addWidget(self.y_max_input)
        grid_layout.addLayout(axis_layout)

        grid_layout.addWidget(QLabel("<b>2. Data Scale (Value per Blocks)</b>"))
        
        # X Scale Inputs
        x_scale_layout = QHBoxLayout()
        self.x_val_input = QLineEdit("30"); self.x_val_input.setFixedWidth(50)
        self.x_blk_input = QLineEdit("3"); self.x_blk_input.setFixedWidth(30)
        x_scale_layout.addWidget(QLabel("X Axis: "))
        x_scale_layout.addWidget(self.x_val_input)
        x_scale_layout.addWidget(QLabel(" units per "))
        x_scale_layout.addWidget(self.x_blk_input)
        x_scale_layout.addWidget(QLabel(" blocks"))
        x_scale_layout.addStretch()
        grid_layout.addLayout(x_scale_layout)

        # Y Scale Inputs
        y_scale_layout = QHBoxLayout()
        self.y_val_input = QLineEdit("0.1"); self.y_val_input.setFixedWidth(50)
        self.y_blk_input = QLineEdit("6"); self.y_blk_input.setFixedWidth(30)
        y_scale_layout.addWidget(QLabel("Y Axis: "))
        y_scale_layout.addWidget(self.y_val_input)
        y_scale_layout.addWidget(QLabel(" units per "))
        y_scale_layout.addWidget(self.y_blk_input)
        y_scale_layout.addWidget(QLabel(" blocks"))
        y_scale_layout.addStretch()
        grid_layout.addLayout(y_scale_layout)

        btn_apply_grid = QPushButton("Apply Grid & Scale Settings")
        btn_apply_grid.setStyleSheet("background-color: #d0e8f2; font-weight: bold; padding: 5px;")
        btn_apply_grid.clicked.connect(self.update_axes)
        grid_layout.addWidget(btn_apply_grid)
        layout.addWidget(grid_frame)
        
        self.grid_checkbox = QCheckBox("Show Blue Grid Lines"); self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self.toggle_grid)
        layout.addWidget(self.grid_checkbox)

        # --- GRAPH & POINTS ---
        layout.addWidget(QLabel("<b>3. Plot Data</b>"))
        graph_layout = QHBoxLayout()
        self.graph_combo = QComboBox()
        self.graph_combo.currentIndexChanged.connect(self.switch_graph)
        btn_new_graph = QPushButton("New Curve"); btn_new_graph.clicked.connect(self.add_new_graph)
        graph_layout.addWidget(QLabel("Curve:")); graph_layout.addWidget(self.graph_combo)
        graph_layout.addWidget(btn_new_graph)
        layout.addLayout(graph_layout)

        add_layout = QHBoxLayout()
        self.plot_x_input = QLineEdit(); self.plot_x_input.setFixedWidth(45)
        self.plot_y_input = QLineEdit(); self.plot_y_input.setFixedWidth(45)
        btn_add = QPushButton("Add"); btn_add.clicked.connect(self.add_point)
        btn_remove = QPushButton("Remove Last"); btn_remove.clicked.connect(self.remove_point) # NEW BUTTON
        add_layout.addWidget(QLabel("X:")); add_layout.addWidget(self.plot_x_input)
        add_layout.addWidget(QLabel("Y:")); add_layout.addWidget(self.plot_y_input)
        add_layout.addWidget(btn_add)
        add_layout.addWidget(btn_remove)
        layout.addLayout(add_layout)

        # Appearance - Points
        point_custom = QHBoxLayout()
        self.point_color_btn = QPushButton("Pt Color"); self.point_color_btn.clicked.connect(self.change_point_color)
        self.point_size_spin = QSpinBox(); self.point_size_spin.setRange(2, 40)
        self.point_size_spin.valueChanged.connect(self.change_point_size)
        self.point_shape_combo = QComboBox(); self.point_shape_combo.addItems(["Circle", "Square", "Triangle"])
        self.point_shape_combo.currentTextChanged.connect(self.change_point_shape)
        point_custom.addWidget(self.point_color_btn)
        point_custom.addWidget(QLabel("Size:")); point_custom.addWidget(self.point_size_spin)
        point_custom.addWidget(QLabel("Shape:")); point_custom.addWidget(self.point_shape_combo)
        layout.addLayout(point_custom)

        # Appearance - Lines 
        line_custom_1 = QHBoxLayout()
        self.line_color_btn = QPushButton("Line Color"); self.line_color_btn.clicked.connect(self.change_line_color)
        
        # --- EXPANDED FIT DROPDOWN ---
        self.fit_combo = QComboBox()
        self.fit_combo.addItems(["Spline", "Linear", "Poly (2nd)", "Poly (3rd)", "Poly (4th)", "Exponential"])
        self.fit_combo.currentTextChanged.connect(self.change_fit_type)
        
        line_custom_1.addWidget(self.line_color_btn)
        line_custom_1.addWidget(QLabel("Fit Type:")); line_custom_1.addWidget(self.fit_combo)
        layout.addLayout(line_custom_1)

        line_custom_2 = QHBoxLayout()
        self.line_thickness_spin = QSpinBox(); self.line_thickness_spin.setRange(0, 5)
        self.line_thickness_spin.valueChanged.connect(self.change_line_thickness)
        self.curve_check = QCheckBox("Show Curve"); self.curve_check.setChecked(True)
        self.curve_check.stateChanged.connect(self.toggle_curve)
        line_custom_2.addWidget(QLabel("Thickness:")); line_custom_2.addWidget(self.line_thickness_spin)
        line_custom_2.addWidget(self.curve_check)
        line_custom_2.addStretch()
        layout.addLayout(line_custom_2)

        # Table
        self.table = QTableWidget(); self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Raw X", "Raw Y"])
        self.table.cellChanged.connect(self.table_cell_changed)
        layout.addWidget(self.table)

        # Export
        export_layout = QHBoxLayout()
        btn_png = QPushButton("Export PNG"); btn_png.clicked.connect(self.export_png)
        btn_pdf = QPushButton("Export PDF"); btn_pdf.clicked.connect(self.export_pdf)
        export_layout.addWidget(btn_png); export_layout.addWidget(btn_pdf)
        layout.addLayout(export_layout)

        dock_widget.setLayout(layout)

        central = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.view)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    # -------------------- Event Handlers --------------------
    def zoom_event(self, event):
        factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
        self.view.scale(factor, factor)

    def toggle_grid(self, state):
        self.show_grid = (state == Qt.Checked)
        self.draw_grid()

    def switch_graph(self, idx):
        self.current_graph_index = idx
        self.update_controls()
        self.draw_grid()

    def add_new_graph(self):
        g = GraphData()
        self.graphs.append(g)
        self.current_graph_index = len(self.graphs) - 1
        self.graph_combo.addItem(f"Curve {len(self.graphs)}")
        self.graph_combo.setCurrentIndex(self.current_graph_index)
        self.update_controls()
        self.draw_grid()

    def update_controls(self):
        g = self.graphs[self.current_graph_index]
        self.point_color_btn.setStyleSheet(f"background-color: {g.point_color.name()}")
        self.point_size_spin.setValue(g.point_size)
        self.point_shape_combo.setCurrentText(g.point_shape)
        self.line_color_btn.setStyleSheet(f"background-color: {g.line_color.name()}")
        self.line_thickness_spin.setValue(g.line_thickness)
        self.fit_combo.setCurrentText(g.fit_type)
        self.curve_check.setChecked(g.show_curve)
        self.table.blockSignals(True)
        self.table.setRowCount(len(g.points))
        for i, (x,y) in enumerate(g.points):
            self.table.setItem(i,0,QTableWidgetItem(str(x)))
            self.table.setItem(i,1,QTableWidgetItem(str(y)))
        self.table.blockSignals(False)

    def add_point(self):
        try:
            x = float(self.plot_x_input.text())
            y = float(self.plot_y_input.text())
        except: return
        g = self.graphs[self.current_graph_index]
        g.points.append((x,y))
        self.table.insertRow(len(g.points)-1)
        self.table.setItem(len(g.points)-1,0,QTableWidgetItem(str(x)))
        self.table.setItem(len(g.points)-1,1,QTableWidgetItem(str(y)))
        self.plot_x_input.clear()
        self.plot_y_input.clear()
        self.plot_x_input.setFocus()
        self.draw_grid()

    def remove_point(self):
        """Removes the last added point from the current curve."""
        g = self.graphs[self.current_graph_index]
        if len(g.points) > 0:
            g.points.pop() # Remove last item from list
            self.table.setRowCount(len(g.points)) # Shrink table
            self.draw_grid()

    def table_cell_changed(self, row, col):
        g = self.graphs[self.current_graph_index]
        try:
            x = float(self.table.item(row,0).text())
            y = float(self.table.item(row,1).text())
            g.points[row] = (x,y)
            self.draw_grid()
        except: pass

    def change_point_color(self):
        g = self.graphs[self.current_graph_index]
        c = QColorDialog.getColor(g.point_color,self)
        if c.isValid(): g.point_color=c; self.draw_grid()

    def change_point_size(self,val):
        g = self.graphs[self.current_graph_index]
        g.point_size=val; self.draw_grid()

    def change_point_shape(self,text):
        g = self.graphs[self.current_graph_index]
        g.point_shape=text; self.draw_grid()

    def change_line_color(self):
        g = self.graphs[self.current_graph_index]
        c = QColorDialog.getColor(g.line_color,self)
        if c.isValid(): g.line_color=c; self.draw_grid()

    def change_line_thickness(self,val):
        g = self.graphs[self.current_graph_index]
        g.line_thickness=val; self.draw_grid()

    def change_fit_type(self,text):
        g = self.graphs[self.current_graph_index]
        g.fit_type=text; self.draw_grid()

    def toggle_curve(self,state):
        g = self.graphs[self.current_graph_index]
        g.show_curve=(state==Qt.Checked); self.draw_grid()

    # -------------------- Drawing --------------------
    def draw_grid(self):
        self.scene.clear()

        # 1. Read physical bounds
        try:
            self.x_min, self.x_max = float(self.x_min_input.text()), float(self.x_max_input.text())
            self.y_min, self.y_max = float(self.y_min_input.text()), float(self.y_max_input.text())
        except: 
            self.x_min, self.x_max, self.y_min, self.y_max = -2, 16, -2, 23

        # 2. Read scales safely
        try:
            data_per_block_x = float(self.x_val_input.text()) / float(self.x_blk_input.text())
        except: data_per_block_x = 10.0 # Default if empty/error
        
        try:
            data_per_block_y = float(self.y_val_input.text()) / float(self.y_blk_input.text())
        except: data_per_block_y = 0.1 / 6.0

        big_box_px = SMALL_BOX_PX * BIG_BOX_COUNT
        scale_x = big_box_px / data_per_block_x
        scale_y = big_box_px / data_per_block_y

        if self.show_grid:
            for i in range(int(WIDTH_PX//SMALL_BOX_PX)+1):
                x = i * SMALL_BOX_PX
                if i % BIG_BOX_COUNT == 0: pen = QPen(self.grid_big_color); pen.setWidth(self.grid_thickness + 1)
                elif i % 5 == 0: pen = QPen(self.grid_mid_color); pen.setWidth(self.grid_thickness)
                else: pen = QPen(self.grid_small_color); pen.setWidth(max(1, self.grid_thickness - 1))
                self.scene.addLine(x, 0, x, HEIGHT_PX, pen)
                
            for j in range(int(HEIGHT_PX//SMALL_BOX_PX)+1):
                y = j * SMALL_BOX_PX
                if j % BIG_BOX_COUNT == 0: pen = QPen(self.grid_big_color); pen.setWidth(self.grid_thickness + 1)
                elif j % 5 == 0: pen = QPen(self.grid_mid_color); pen.setWidth(self.grid_thickness)
                else: pen = QPen(self.grid_small_color); pen.setWidth(max(1, self.grid_thickness - 1))
                self.scene.addLine(0, y, WIDTH_PX, y, pen)

        zero_x = int(round((0 - self.x_min) * big_box_px))
        zero_y = int(round(HEIGHT_PX - (0 - self.y_min) * big_box_px))
        self.zero_x = max(0, min(WIDTH_PX, zero_x))
        self.zero_y = max(0, min(HEIGHT_PX, zero_y))

        axis_pen = QPen(Qt.black)
        axis_pen.setWidthF(0.8)
        self.scene.addLine(self.zero_x, 0, self.zero_x, HEIGHT_PX, axis_pen)
        self.scene.addLine(0, self.zero_y, WIDTH_PX, self.zero_y, axis_pen)

        for g in self.graphs:
            for pt in g.points: self.draw_point(pt[0], pt[1], g, scale_x, scale_y)
            self.draw_curve(g, scale_x, scale_y)

    def draw_point(self, x, y, g, scale_x, scale_y):
        px = self.zero_x + x * scale_x
        py = self.zero_y - y * scale_y
        s = g.point_size
        brush = QBrush(g.point_color); pen = QPen(Qt.black)
        shape = g.point_shape
        if shape == "Circle": self.scene.addEllipse(px-s/2, py-s/2, s, s, pen, brush)
        elif shape == "Square": self.scene.addRect(px-s/2, py-s/2, s, s, pen, brush)
        elif shape == "Triangle":
            p1 = (px, py-s/2); p2 = (px-s/2, py+s/2); p3 = (px+s/2, py+s/2)
            self.scene.addLine(p1[0], p1[1], p2[0], p2[1], QPen(g.point_color))
            self.scene.addLine(p2[0], p2[1], p3[0], p3[1], QPen(g.point_color))
            self.scene.addLine(p3[0], p3[1], p1[0], p1[1], QPen(g.point_color))

    def draw_curve(self, g, scale_x, scale_y):
        if not g.show_curve or len(g.points) < 2: return
        pts = sorted(g.points, key=lambda p: p[0])
        x = np.array([p[0] for p in pts])
        y = np.array([p[1] for p in pts])
        
        # Generate dense X points for smooth drawing
        xs = np.linspace(x[0], x[-1], 300)
        ys = None

        try:
            if g.fit_type == "Linear":
                coeff = np.polyfit(x, y, 1)
                poly = np.poly1d(coeff)
                ys = poly(xs)
            elif g.fit_type == "Poly (2nd)":
                deg = min(2, len(x)-1)
                coeff = np.polyfit(x, y, deg)
                poly = np.poly1d(coeff)
                ys = poly(xs)
            elif g.fit_type == "Poly (3rd)":
                deg = min(3, len(x)-1)
                coeff = np.polyfit(x, y, deg)
                poly = np.poly1d(coeff)
                ys = poly(xs)
            elif g.fit_type == "Poly (4th)":
                deg = min(4, len(x)-1)
                coeff = np.polyfit(x, y, deg)
                poly = np.poly1d(coeff)
                ys = poly(xs)
            elif g.fit_type == "Exponential":
                # Only use points where y > 0 to avoid math errors with log()
                valid = y > 0
                if np.sum(valid) > 1:
                    # Fit: ln(y) = ln(a) + bx
                    b, log_a = np.polyfit(x[valid], np.log(y[valid]), 1)
                    ys = np.exp(log_a) * np.exp(b * xs)
                else:
                    ys = y # Fallback if invalid data
            else: # Spline
                cs = CubicSpline(x, y)
                ys = cs(xs)
        except:
            # Fallback to straight lines between raw points if any math fails
            xs = x
            ys = y

        pen = QPen(g.line_color)
        pen.setWidth(g.line_thickness)
        pen.setStyle(g.line_type)

        for i in range(len(xs)-1):
            x1 = self.zero_x + xs[i] * scale_x; y1 = self.zero_y - ys[i] * scale_y
            x2 = self.zero_x + xs[i+1] * scale_x; y2 = self.zero_y - ys[i+1] * scale_y
            self.scene.addLine(x1, y1, x2, y2, pen)

    # -------------------- Export --------------------
    def scene_to_image(self):
        image = QImage(WIDTH_PX, HEIGHT_PX, QImage.Format_ARGB32)
        image.fill(Qt.white)
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()
        return image

    def export_png(self):
        filename,_=QFileDialog.getSaveFileName(self,"Save PNG","","PNG Files (*.png)")
        if filename: self.scene_to_image().save(filename,"PNG")

    def export_pdf(self):
        filename,_ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not filename: return
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        printer.setPageMargins(self.margin_left, self.margin_top, self.margin_right, self.margin_bottom, QPrinter.Millimeter)
        painter = QPainter(printer)
        self.scene.render(painter)
        painter.end()

    def update_axes(self): self.draw_grid()

if __name__=="__main__":
    app=QApplication(sys.argv)
    win=LabGraphApp()
    win.show()
    sys.exit(app.exec_())