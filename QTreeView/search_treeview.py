from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from src import config

tree = {
    "test1":{
        "test11": "test11",
        "test12": "test12",
    },
    "test2":{
        "test21": "test21",
        "test22": "test22",
    },
    "test3": {
        "test31": "test21",
        "test32": "test22",
    }
}


# 第二次提交
def get_icon_by_char(char):
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter()
    painter.begin(pixmap)
    painter.setFont(QFont('Webdings', 11))
    painter.setPen(Qt.GlobalColor(ord(char)%14+4))
    painter.drawText(0, 0, 16, 16, Qt.AlignCenter,
                    char)
    painter.end()
    return QIcon(pixmap)


class TreeFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, **kwargs):
        super(TreeFilterProxyModel, self).__init__(*args, **kwargs)
        self.sortCaseSensitivity()

    def filterAcceptsRow(self, row, sourceParent):
        p_model = self.sourceModel()
        source_index = p_model.index(row, 0, sourceParent)
        print('filter arrent row', source_index.data(Qt.UserRole))
        if self.filterRegExp().pattern() == "":
            return True
        if self.filterRegExp().pattern() in p_model.data(source_index).lower():
            # self.sourceModel().itemFromIndex(source_index).setForeground(Qt.red)
            return True

        for r in range(p_model.rowCount(source_index)):
            if self.filterAcceptsRow(r, source_index):
                # self.sourceModel().itemFromIndex(p_model.index(r, 0, sourceParent)).expand()
                # self.treeview.expand(p_model.index(r, 0, sourceParent))
                return True

        return False

    def data(self, index, role=Qt.FontRole):
        if self.filterRegExp().pattern() != "" and role == Qt.TextColorRole:
            print(self.sourceModel().data(self.mapToSource(index)), self.filterRegExp().pattern())
            if self.filterRegExp().pattern() in self.sourceModel().data(self.mapToSource(index)).lower():
                # self.sourceModel().itemFromIndex(source_index).setForeground(Qt.red)
                return QColor("green")
            else:
                return QColor("lightslategray")
        return super(TreeFilterProxyModel, self).data(index, role)


class TreeButtonDelegate(QStyledItemDelegate):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        item = index.model


class Tree(QTreeView):

    def __init__(self, *args, **kwargs):
        QTreeView.__init__(self, *args, **kwargs)
        self._key = ""
        self.setHeaderHidden(True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setSelectionMode(self.SingleSelection)

        self.dmodel = QStandardItemModel(self)
        # self.setModel(self.dmodel)

        self.fmode = TreeFilterProxyModel(self)
        # self.fmode = QSortFilterProxyModel(self)
        self.fmode.setSourceModel(self.dmodel)
        self.setModel(self.fmode)

        self.load_tree(self.dmodel.invisibleRootItem(), tree)

    def set_key(self, key):
        self._key = str(key)

    def add_node(self, parent, value):
        item1 = QStandardItem(value)
        item1.setIcon(get_icon_by_char('a'))
        item1.setText(value)
        item1.setData({'name': value}, Qt.UserRole)
        # item1.setForeground(Qt.red)
        item1.setEditable(False)

        parent.appendRow(item1)
        return item1

    def load_tree(self, root, tree):
        for key, value in tree.items():
            if type(value) is dict:
                sub_root = self.add_node(root, key)
                self.load_tree(sub_root, value)
            else:
                self.add_node(root, value)

    def add_dynamc(self, name):
        self.add_node(self.dmodel.invisibleRootItem(), name)

    def update(self, index):
        super(Tree, self).update(index)
        item = self.model().itemFormIndex(index)
        if self._key == "":
            item.setForeground(QBrush())
        else:
            item.setForeground(Qt.red)



class windows(QWidget):
    def __init__(self, *args, **kwargs):
        super(windows, self).__init__(*args, **kwargs)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.search = QLineEdit(self)
        # self.search.editingFinished.connect(self.filterAcceptsRow)
        self.search.textChanged.connect(self.text_change)
        self.tree_view = Tree(self)
        layout.addWidget(self.search)
        layout.addWidget(self.tree_view)

    def text_change(self):
        key = self.search.text()
        # self.tree_view.fmode.set_key(key)
        self.tree_view.set_key(key)
        self.tree_view.fmode.setFilterRegExp(key)
        self.tree_view.viewport().update()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = windows()
    w.show()
    sys.exit(app.exec_())