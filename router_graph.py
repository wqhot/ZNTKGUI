import math

from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath, QPixmap, QPainter
from PyQt5.QtCore import Qt, QPointF, QLine
import socket
import json

class Edge:

    def __init__(self, scene, start_item, end_item):
        super().__init__()
        self.scene = scene
        self.start_item = start_item
        self.end_item = end_item

        self.gr_edge = GraphicEdge(self)
        # add edge on graphic scene
        self.scene.add_edge(self.gr_edge)

        if self.start_item is not None:
            self.update_positions()

    def store(self):
        self.scene.add_edge(self.gr_edge)

    def update_positions(self):
        patch = self.start_item.width / 2
        src_pos = self.start_item.pos()
        self.gr_edge.set_src(src_pos.x()+patch, src_pos.y()+patch)
        if self.end_item is not None:
            end_pos = self.end_item.pos()
            self.gr_edge.set_dst(end_pos.x()+patch, end_pos.y()+patch)
        else:
            self.gr_edge.set_dst(src_pos.x()+patch, src_pos.y()+patch)
        self.gr_edge.update()

    def remove_from_current_items(self):
        self.end_item = None
        self.start_item = None

    def remove(self):
        self.remove_from_current_items()
        self.scene.remove_edge(self.gr_edge)
        self.gr_edge = None


class GraphicEdge(QGraphicsPathItem):

    def __init__(self, edge_wrap, parent=None):
        super().__init__(parent)
        self.edge_wrap = edge_wrap
        self.width = 3.0
        self.pos_src = [0, 0]
        self.pos_dst = [0, 0]

        self._pen = QPen(QColor("#000"))
        self._pen.setWidthF(self.width)

        self._pen_dragging = QPen(QColor("#000"))
        self._pen_dragging.setStyle(Qt.DashDotLine)
        self._pen_dragging.setWidthF(self.width)

        self._mark_pen = QPen(Qt.green)
        self._mark_pen.setWidthF(self.width)
        self._mark_brush = QBrush()
        self._mark_brush.setColor(Qt.green)
        self._mark_brush.setStyle(Qt.SolidPattern)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def set_src(self, x, y):
        self.pos_src = [x, y]

    def set_dst(self, x, y):
        self.pos_dst = [x, y]

    def calc_path(self):
        path = QPainterPath(QPointF(self.pos_src[0], self.pos_src[1]))
        path.lineTo(self.pos_dst[0], self.pos_dst[1])
        return path

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calc_path()

    def paint(self, painter, graphics_item, widget=None):
        self.setPath(self.calc_path())
        path = self.path()
        if self.edge_wrap.end_item is None:
            painter.setPen(self._pen_dragging)
            painter.drawPath(path)
        else:
            x1, y1 = self.pos_src
            x2, y2 = self.pos_dst
            radius = 5    # marker radius
            length = 70   # marker length
            k = math.atan2(y2 - y1, x2 - x1)
            new_x = x2 - length * math.cos(k) - self.width
            new_y = y2 - length * math.sin(k) - self.width

            painter.setPen(self._pen)
            painter.drawPath(path)

            painter.setPen(self._mark_pen)
            painter.setBrush(self._mark_brush)
            painter.drawEllipse(new_x, new_y, radius, radius)

class GraphicItem(QGraphicsPixmapItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pix = QPixmap("./res/Model.png")
        self.width = 85
        self.height = 85
        self.setPixmap(self.pix)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.left = True
        self.index = 0

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # update selected node and its edge
        if self.isSelected():
            for gr_edge in self.scene().edges:
                gr_edge.edge_wrap.update_positions()

class GraphicScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)

        # settings
        self.grid_size = 20
        self.grid_squares = 5

        self._color_background = QColor('#393939')
        self._color_light = QColor('#2f2f2f')
        self._color_dark = QColor('#292929')

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)
        self.setSceneRect(0, 0, 700, 500)

        self.nodes = []
        self.edges = []

    def remove_all_node(self):
        for node in self.nodes:
            for edge in self.edges:
                if edge.edge_wrap.start_item is node or edge.edge_wrap.end_item is node:
                    self.remove_edge(edge)
            self.removeItem(node)
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)
        self.addItem(node)

    def remove_node(self, node):
        self.nodes.remove(node)
        for edge in self.edges:
            if edge.edge_wrap.start_item is node or edge.edge_wrap.end_item is node:
                self.remove_edge(edge)
        self.removeItem(node)

    def add_edge(self, edge):
        self.edges.append(edge)
        self.addItem(edge)

    def remove_edge(self, edge):
        self.edges.remove(edge)
        self.removeItem(edge)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if x % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if y % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # draw the lines
        painter.setPen(self._pen_light)
        if lines_light:
            painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        if lines_dark:
            painter.drawLines(*lines_dark)

class GraphicView(QGraphicsView):

    def __init__(self, graphic_scene, parent=None):
        super().__init__(parent)

        self.gr_scene = graphic_scene
        self.parent = parent

        self.edge_enable = False
        self.drag_edge = None

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock.bind(("0.0.0.0", 5502))
        self.init_ui()

    def init_ui(self):
        self.setScene(self.gr_scene)
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setDragMode(self.RubberBandDrag)

    def get_router_rules(self):
        self.send_sock.sendto(b"GET", ("192.168.50.61", 5501))
        recv_data, source_ip = self.recv_sock.recvfrom(1024)
        recv_str = recv_data.decode()
        recv_json = json.loads(recv_str)
        self.left_list = {}
        self.right_list = {}
        for k, v in recv_json.items():
            id = v["id"]
            left_name = v["left_name"]
            right_idxs = v["right_idxs"]
            connect = []
            index = 0
            while right_idxs >> index:
                if (right_idxs >> index) & 1 :
                    connect.append(index)
                index = index + 1
            self.left_list[id] = {"index": id, "left_name": left_name, "right_idxs": right_idxs, "connect": connect}
            for index in connect:
                if str(index) in v.keys():
                    self.right_list[index] = {"index": index, "right_name": v[str(index)]["right_name"]}
        # self.left_list = sorted(self.left_list)
        # self.right_list = sorted(self.right_list)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_N:
            self.gr_scene.remove_all_node()
            self.get_router_rules()     
            max_size = max(len(self.right_list.keys()), len(self.left_list.keys()))
            print(max_size)
            height = 500 / (max_size)
            # right
            right_items = []
            for i, r in enumerate(sorted(self.right_list)):
                item = GraphicItem()
                item.setPos(300, i * height)
                self.gr_scene.add_node(item)
                right_items.append(item)
            # left
            for i, l in enumerate(sorted(self.left_list)):
                item = GraphicItem()
                item.setPos(0, i * height)
                self.gr_scene.add_node(item)
                for c in self.left_list[l]["connect"]:
                    self.edge_drag_start(item)
                    self.edge_drag_end(right_items[c])     
        if event.key() == Qt.Key_E:
            self.edge_enable = ~self.edge_enable

    def mousePressEvent(self, event):
        item = self.get_item_at_click(event)
        if event.button() == Qt.RightButton:
            if isinstance(item, GraphicEdge) and self.edge_enable:
                self.gr_scene.remove_edge(item)
        elif self.edge_enable and event.button() == Qt.LeftButton:
            if isinstance(item, GraphicItem):
                self.edge_drag_start(item)
        else:
            super().mousePressEvent(event)

    def get_item_at_click(self, event):
        """ Return the object that clicked on. """
        pos = event.pos()
        item = self.itemAt(pos)
        return item

    def get_items_at_rubber(self):
        """ Get group select items. """
        area = self.rubberBandRect()
        return self.items(area)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.edge_enable and self.drag_edge is not None:
            sc_pos = self.mapToScene(pos)
            self.drag_edge.gr_edge.set_dst(sc_pos.x(), sc_pos.y())
            self.drag_edge.gr_edge.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.edge_enable:
            self.edge_enable = False
            item = self.get_item_at_click(event)
            if isinstance(item, GraphicItem) and item is not self.drag_start_item:
                self.edge_drag_end(item)
            elif self.drag_edge is not None:
                self.drag_edge.remove()
                self.drag_edge = None
        else:
            super().mouseReleaseEvent(event)

    def edge_drag_start(self, item):
        self.drag_start_item = item
        self.drag_edge = Edge(self.gr_scene, self.drag_start_item, None)

    def edge_drag_end(self, item):
        new_edge = Edge(self.gr_scene, self.drag_start_item, item)
        self.drag_edge.remove()
        self.drag_edge = None
        new_edge.store()
