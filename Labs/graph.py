"""
Professional Lab Graph Tool (GrapherV1.0)

Author: Muraleetharan Kugaram
Year: 2026

License: MIT License
Copyright (c) 2026 Muraleetharan Kugaram

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGraphicsScene, QGraphicsView,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QDockWidget,
    QComboBox, QColorDialog, QSpinBox, QCheckBox, QSlider
)
from PyQt5.QtGui import QPen, QColor, QPainter, QBrush, QImage, QPainterPath
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtPrintSupport import QPrinter

# ---------- Graph Sheet Settings ----------
MM_TO_PX = 3.78
A4_WIDTH_MM = 180
A4_HEIGHT_MM = 250
WIDTH_PX = int(A4_WIDTH_MM * MM_TO_PX)
HEIGHT_PX = int(A4_HEIGHT_MM * MM_TO_PX)
SMALL_BOX_MM = 1
SMALL_BOX_PX = SMALL_BOX_MM * MM_TO_PX
BIG_BOX_COUNT = 10  # 1 cm boxes
UNIT_PER_CM = 1     # 1 data unit = 1 cm on graph

class GraphData:
    """Store per-graph data."""
    def __init__(self):
        self.points = []
        self.line_color = QColor(0, 80, 200, 255)
        self.line_thickness = 2
        self.line_type = Qt.SolidLine
        self.show_curve = True
        self.point_color = QColor(220, 20, 60)
        self.point_size = 8
        self.point_shape = "Circle"

class LabGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Lab Graph Tool")
        self.setGeometry(50, 50, WIDTH_PX + 480, HEIGHT_PX + 120)

        # All graphs
        self.graphs = []
        self.current_graph_index = 0

        # Axis-range (for scaling/labels)
        self.x_min, self.x_max = -10, 10
        self.y_min, self.y_max = -10, 10

        # Grid
        self.grid_small_color = QColor(220, 220, 220)
        self.grid_big_color = QColor(180, 180, 180)
        self.grid_thickness = 1
        self.show_grid = True

        # Margins (mm) for PDF export
        self.margin_top = 17
        self.margin_bottom = 30
        self.margin_left = 15
        self.margin_right = 15

        self.init_ui()
        self.add_new_graph()  # start with first graph

    # -------------------- UI --------------------
    def init_ui(self):
        # Scene & view
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, WIDTH_PX, HEIGHT_PX)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.wheelEvent = self.zoom_event

        # Dock (controls)
        dock = QDockWidget("Controls", self)
        dock_widget = QWidget()
        dock.setWidget(dock_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        layout = QVBoxLayout()

        # Axis inputs
        axis_layout = QHBoxLayout()
        self.x_min_input = QLineEdit(str(self.x_min)); self.x_min_input.setFixedWidth(60)
        self.x_max_input = QLineEdit(str(self.x_max)); self.x_max_input.setFixedWidth(60)
        self.y_min_input = QLineEdit(str(self.y_min)); self.y_min_input.setFixedWidth(60)
        self.y_max_input = QLineEdit(str(self.y_max)); self.y_max_input.setFixedWidth(60)
        btn_axes = QPushButton("Update Axes")
        btn_axes.clicked.connect(self.update_axes)
        axis_layout.addWidget(QLabel("X min:")); axis_layout.addWidget(self.x_min_input)
        axis_layout.addWidget(QLabel("X max:")); axis_layout.addWidget(self.x_max_input)
        axis_layout.addWidget(QLabel("Y min:")); axis_layout.addWidget(self.y_min_input)
        axis_layout.addWidget(QLabel("Y max:")); axis_layout.addWidget(self.y_max_input)
        axis_layout.addWidget(btn_axes)
        layout.addLayout(axis_layout)

        # Grid toggle
        self.grid_checkbox = QCheckBox("Show Grid"); self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self.toggle_grid)
        layout.addWidget(self.grid_checkbox)

        # Graph selector & new graph
        graph_layout = QHBoxLayout()
        self.graph_combo = QComboBox()
        self.graph_combo.currentIndexChanged.connect(self.switch_graph)
        btn_new_graph = QPushButton("New Graph"); btn_new_graph.clicked.connect(self.add_new_graph)
        graph_layout.addWidget(QLabel("Graph:")); graph_layout.addWidget(self.graph_combo)
        graph_layout.addWidget(btn_new_graph)
        layout.addLayout(graph_layout)

        # Add point inputs
        add_layout = QHBoxLayout()
        self.plot_x_input = QLineEdit(); self.plot_x_input.setFixedWidth(60)
        self.plot_y_input = QLineEdit(); self.plot_y_input.setFixedWidth(60)
        btn_add = QPushButton("Add Point"); btn_add.clicked.connect(self.add_point)
        add_layout.addWidget(QLabel("X:")); add_layout.addWidget(self.plot_x_input)
        add_layout.addWidget(QLabel("Y:")); add_layout.addWidget(self.plot_y_input)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)

        # Point customization
        point_custom = QHBoxLayout()
        self.point_color_btn = QPushButton("Point Color"); self.point_color_btn.clicked.connect(self.change_point_color)
        self.point_size_spin = QSpinBox(); self.point_size_spin.setRange(2, 40)
        self.point_size_spin.valueChanged.connect(self.change_point_size)
        self.point_shape_combo = QComboBox(); self.point_shape_combo.addItems(["Circle", "Square", "Triangle"])
        self.point_shape_combo.currentTextChanged.connect(self.change_point_shape)
        point_custom.addWidget(self.point_color_btn)
        point_custom.addWidget(QLabel("Size:")); point_custom.addWidget(self.point_size_spin)
        point_custom.addWidget(QLabel("Shape:")); point_custom.addWidget(self.point_shape_combo)
        layout.addLayout(point_custom)

        # Line customization
        line_custom = QHBoxLayout()
        self.line_color_btn = QPushButton("Line Color"); self.line_color_btn.clicked.connect(self.change_line_color)
        self.line_thickness_spin = QSpinBox(); self.line_thickness_spin.setRange(0, 5)
        self.line_thickness_spin.valueChanged.connect(self.change_line_thickness)
        self.line_type_combo = QComboBox(); self.line_type_combo.addItems(["Solid", "Dash", "Dot"])
        self.line_type_combo.currentTextChanged.connect(self.change_line_type)
        self.curve_check = QCheckBox("Show Curve"); self.curve_check.stateChanged.connect(self.toggle_curve)
        self.line_dark_slider = QSlider(Qt.Horizontal); self.line_dark_slider.setRange(0, 255)
        self.line_dark_slider.setValue(255); self.line_dark_slider.valueChanged.connect(self.change_line_darkness)
        line_custom.addWidget(self.line_color_btn)
        line_custom.addWidget(QLabel("Thickness:")); line_custom.addWidget(self.line_thickness_spin)
        line_custom.addWidget(QLabel("Type:")); line_custom.addWidget(self.line_type_combo)
        line_custom.addWidget(self.curve_check)
        line_custom.addWidget(QLabel("Line Darkness")); line_custom.addWidget(self.line_dark_slider)
        layout.addLayout(line_custom)

        # Grid customization
        grid_custom = QHBoxLayout()
        self.grid_small_btn = QPushButton("Small Grid Color"); self.grid_small_btn.clicked.connect(self.change_small_grid)
        self.grid_big_btn = QPushButton("Big Grid Color"); self.grid_big_btn.clicked.connect(self.change_big_grid)
        grid_custom.addWidget(self.grid_small_btn); grid_custom.addWidget(self.grid_big_btn)
        layout.addLayout(grid_custom)

        # Table
        self.table = QTableWidget(); self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["X", "Y"])
        self.table.cellChanged.connect(self.table_cell_changed)
        layout.addWidget(self.table)

        # Export
        export_layout = QHBoxLayout()
        btn_png = QPushButton("Export PNG"); btn_png.clicked.connect(self.export_png)
        btn_pdf = QPushButton("Export PDF"); btn_pdf.clicked.connect(self.export_pdf)
        export_layout.addWidget(btn_png); export_layout.addWidget(btn_pdf)
        layout.addLayout(export_layout)

        dock_widget.setLayout(layout)

        # central widget
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
        self.graph_combo.addItem(f"Graph {len(self.graphs)}")
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
        self.line_type_combo.setCurrentText({Qt.SolidLine:"Solid", Qt.DashLine:"Dash", Qt.DotLine:"Dot"}[g.line_type])
        self.curve_check.setChecked(g.show_curve)
        self.line_dark_slider.setValue(g.line_color.alpha())
        # populate table
        self.table.blockSignals(True)
        self.table.setRowCount(len(g.points))
        for i, (x,y) in enumerate(g.points):
            self.table.setItem(i,0,QTableWidgetItem(str(x)))
            self.table.setItem(i,1,QTableWidgetItem(str(y)))
        self.table.blockSignals(False)

    # -------------------- Point & Line Handlers --------------------
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

    def change_line_type(self,text):
        g = self.graphs[self.current_graph_index]
        g.line_type={"Solid":Qt.SolidLine,"Dash":Qt.DashLine,"Dot":Qt.DotLine}[text]
        self.draw_grid()

    def toggle_curve(self,state):
        g = self.graphs[self.current_graph_index]
        g.show_curve=(state==Qt.Checked); self.draw_grid()

    def change_line_darkness(self,val):
        g = self.graphs[self.current_graph_index]
        c = g.line_color
        g.line_color = QColor(c.red(),c.green(),c.blue(),val)
        self.draw_grid()

    def change_small_grid(self):
        c = QColorDialog.getColor(self.grid_small_color,self)
        if c.isValid(): self.grid_small_color=c; self.draw_grid()

    def change_big_grid(self):
        c = QColorDialog.getColor(self.grid_big_color,self)
        if c.isValid(): self.grid_big_color=c; self.draw_grid()

    # -------------------- Drawing --------------------
    def draw_grid(self):
        self.scene.clear()

        # axis
        try:
            self.x_min=float(self.x_min_input.text())
            self.x_max=float(self.x_max_input.text())
            self.y_min=float(self.y_min_input.text())
            self.y_max=float(self.y_max_input.text())
        except: self.x_min,self.x_max,self.y_min,self.y_max=-10,10,-10,10

        big_box_px = SMALL_BOX_PX * BIG_BOX_COUNT
        scale_x = big_box_px / UNIT_PER_CM
        scale_y = big_box_px / UNIT_PER_CM

        if self.show_grid:
            for i in range(int(WIDTH_PX//SMALL_BOX_PX)+1):
                x=i*SMALL_BOX_PX
                pen=QPen(self.grid_big_color if i%BIG_BOX_COUNT==0 else self.grid_small_color)
                pen.setWidth(self.grid_thickness)
                self.scene.addLine(x,0,x,HEIGHT_PX,pen)
            for j in range(int(HEIGHT_PX//SMALL_BOX_PX)+1):
                y=j*SMALL_BOX_PX
                pen=QPen(self.grid_big_color if j%BIG_BOX_COUNT==0 else self.grid_small_color)
                pen.setWidth(self.grid_thickness)
                self.scene.addLine(0,y,WIDTH_PX,y,pen)

        # zero
        zero_x = int(round((0-self.x_min)*scale_x/big_box_px)*big_box_px)
        zero_y = int(round((HEIGHT_PX-(0-self.y_min)*scale_y)/big_box_px)*big_box_px)
        zero_x=max(0,min(WIDTH_PX,zero_x))
        zero_y=max(0,min(HEIGHT_PX,zero_y))
        self.zero_x=zero_x
        self.zero_y=zero_y

        # axes
        axis_pen=QPen(Qt.black); axis_pen.setWidthF(0.8)
        self.scene.addLine(self.zero_x,0,self.zero_x,HEIGHT_PX,axis_pen)
        self.scene.addLine(0,self.zero_y,WIDTH_PX,self.zero_y,axis_pen)

        # draw all graphs
        for g in self.graphs:
            for pt in g.points:
                self.draw_point(pt[0],pt[1],g)
            self.draw_curve(g,scale_x,scale_y)

    def draw_point(self,x,y,g):
        px=self.zero_x+x*SMALL_BOX_PX*BIG_BOX_COUNT/UNIT_PER_CM
        py=self.zero_y-y*SMALL_BOX_PX*BIG_BOX_COUNT/UNIT_PER_CM
        s=g.point_size
        brush=QBrush(g.point_color)
        pen=QPen(Qt.black)
        shape=g.point_shape
        if shape=="Circle": self.scene.addEllipse(px-s/2,py-s/2,s,s,pen,brush)
        elif shape=="Square": self.scene.addRect(px-s/2,py-s/2,s,s,pen,brush)
        elif shape=="Triangle":
            p1=(px,py-s/2); p2=(px-s/2,py+s/2); p3=(px+s/2,py+s/2)
            self.scene.addLine(p1[0],p1[1],p2[0],p2[1],QPen(g.point_color))
            self.scene.addLine(p2[0],p2[1],p3[0],p3[1],QPen(g.point_color))
            self.scene.addLine(p3[0],p3[1],p1[0],p1[1],QPen(g.point_color))

    def draw_curve(self,g,scale_x,scale_y):
        if not g.show_curve or len(g.points) < 2:
            return

        pts = sorted(g.points, key=lambda p: p[0])
        pen = QPen(g.line_color)
        pen.setWidth(g.line_thickness)
        pen.setStyle(g.line_type)

        # If only two points, draw a simple line.
        if len(pts) == 2:
            x1 = self.zero_x + pts[0][0] * scale_x
            y1 = self.zero_y - pts[0][1] * scale_y
            x2 = self.zero_x + pts[1][0] * scale_x
            y2 = self.zero_y - pts[1][1] * scale_y
            self.scene.addLine(x1, y1, x2, y2, pen)
            return

        # Qt-native smoothing: Catmull-Rom spline converted to cubic Beziers.
        # This avoids importing heavy dependencies (numpy/scipy) and is fast.
        def to_scene_point(p):
            return QPointF(self.zero_x + p[0] * scale_x, self.zero_y - p[1] * scale_y)

        sp = [to_scene_point(p) for p in pts]

        # Duplicate endpoints for boundary conditions.
        pnts = [sp[0]] + sp + [sp[-1]]

        path = QPainterPath(pnts[1])

        # Uniform Catmull-Rom: controls are (p2 - p0)/6 and (p3 - p1)/6.
        for i in range(1, len(pnts) - 2):
            p0 = pnts[i - 1]
            p1 = pnts[i]
            p2 = pnts[i + 1]
            p3 = pnts[i + 2]

            c1 = QPointF(p1.x() + (p2.x() - p0.x()) / 6.0, p1.y() + (p2.y() - p0.y()) / 6.0)
            c2 = QPointF(p2.x() - (p3.x() - p1.x()) / 6.0, p2.y() - (p3.y() - p1.y()) / 6.0)
            path.cubicTo(c1, c2, p2)

        self.scene.addPath(path, pen)

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
        if not filename: 
            return
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        # Use millimeters directly
        printer.setPageMargins(self.margin_left,
                            self.margin_top,
                            self.margin_right,
                            self.margin_bottom,
                            QPrinter.Millimeter)
        painter = QPainter(printer)
        self.scene.render(painter)
        painter.end()

    # -------------------- Axis --------------------
    def update_axes(self): self.draw_grid()

# -------------------- Main --------------------
if __name__=="__main__":
    app=QApplication(sys.argv)
    win=LabGraphApp()
    win.show()
    sys.exit(app.exec_())