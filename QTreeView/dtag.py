from PyQt5.QtWidgets import QTreeView, QFileSystemModel, QApplication, \
    QMenu, QAbstractItemView, QWidget, QHBoxLayout, QMessageBox
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


class Tree(QTreeView):

    def __init__(self, *args, **kwargs):
        QTreeView.__init__(self, *args, **kwargs)
        self.setHeaderHidden(True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_custom_context_menu)

        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        # self.setDropIndicatorShown(True)

        self.dmodel = QStandardItemModel(self)
        self.setModel(self.dmodel)

        self.load_tree(self.dmodel.invisibleRootItem(), tree)

    def add_node(self, parent, value):
        item1 = QStandardItem(value)
        item1.setIcon(get_icon_by_char('a'))
        item1.setText(value)
        item1.setEditable(False)

        item2 = QStandardItem(value)
        item2.setIcon(get_icon_by_char('3'))
        item2.setText(value)
        item2.setEditable(False)

        parent.appendRow([item1, item2])
        return item1

    def load_tree(self, root, tree):
        for key, value in tree.items():
            if type(value) is dict:
                sub_root = self.add_node(root, key)
                self.load_tree(sub_root, value)
            else:
                self.add_node(root, value)


    def dragEnterEvent(self, event):
        # print("bdx drop enter event", event)
        # m = event.mimeData()
        # if m.hasUrls():
        #     for url in m.urls():
        #         if url.isLocalFile():
        #             event.accept()
        #             return
        # event.ignore()
        super(Tree, self).dragEnterEvent(event)

    def dropEvent(self, event):
        # print("bdx", "drop event", event)
        # if event.source():
        #     QTreeView.dropEvent(self, event)
        # else:
        #     ix = self.indexAt(event.pos())
        #     if not self.model().isDir(ix):
        #         ix = ix.parent()
        #     pathDir = self.model().filePath(ix)
        #     m = event.mimeData()
        #     if m.hasUrls():
        #         urlLocals = [url for url in m.urls() if url.isLocalFile()]
        #         accepted = False
        #         for urlLocal in urlLocals:
        #             path = urlLocal.toLocalFile()
        #             info = QFileInfo(path)
        #             n_path = QDir(pathDir).filePath(info.fileName())
        #             o_path = info.absoluteFilePath()
        #             if n_path == o_path:
        #                 continue
        #             if info.isDir():
        #                 QDir().rename(o_path, n_path)
        #             else:
        #                 qfile = QFile(o_path)
        #                 if QFile(n_path).exists():
        #                     n_path += "(copy)"
        #                 qfile.rename(n_path)
        #             accepted = True
        #         if accepted:
        #             event.acceptProposedAction()
        idx = self.indexAt(event.pos())
        value = self.model().data(idx)
        source = event.source()
        if source == self:
            source_value = self.model().data(source.currentIndex())
            source_item = self.model().itemFromIndex(source.currentIndex())
            print("drop event self s: %s v: %s" % (source_value, value))
            print("drop source_item: ", source_item)
            if not source_value.startswith(value):
                print("not match")
                return
            else:
                print("match")

        else:
            # super(Tree, self).dropEvent(event)
            pass

        # super(Tree, self).dropEvent(event)

    def dragMoveEvent(self, event):
        # print("bdx drag move event", event)
        drop_indicator = self.dropIndicatorPosition()
        if drop_indicator == self.AboveItem:
            # print("Above")
            pass
        elif drop_indicator == self.OnItem:
            # print("OnItem")
            pass
        super(Tree, self).dragMoveEvent(event)

    def startDrag(self, actions):
        print("bdx start drag")
        if True:
            super().startDrag(actions)

    def open_menu(self):
        menu = QMenu()
        menu.addAction("Create new folder")
        menu.exec_(QCursor.pos())

    def rename(self, pindex):
        index = QModelIndex(pindex)
        item = self.model().itemFromIndex(index)
        item.setEditable(True)
        self.item_changed_record = item.text()
        self.edit(index)
        item.setEditable(False)
        # 一定要动态connect 否则出现递归调用
        self.dmodel.itemChanged.connect(self.on_item_changed)

        print("rename", item)

    def on_item_changed(self, item):
        self.dmodel.itemChanged.disconnect()

        result = item.text()
        print("item change", item, result)

        if result == '':
            # self.item_changing = True
            item.setEditable(True)
            item.setText(self.item_changed_record)
            item.setEditable(False)
            # self.item_changing = False
            self.item_changed_record = None


    def on_custom_context_menu(self, point):
        index = self.indexAt(point)
        print("menu", type(index))
        if index.isValid():
            print("menu2", type(index))
            menu = QMenu()
            action = menu.addAction(QIcon(get_icon_by_char('d')), "重命名")
            action.triggered.connect(lambda check, pindex=QPersistentModelIndex(index):self.rename(pindex))
            menu.exec_(QCursor.pos())



class windows(QWidget):
    def __init__(self, *args, **kwargs):
        super(windows, self).__init__(*args, **kwargs)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(Tree(self))
        layout.addWidget(Tree(self))

        # QMessageBox.information(self, "添加失败",
        #                      "%s 未支持！\n请在函数 add_component 中添加"%"adf",
        #                      QMessageBox.Ok,
        #                      )
        # msgBox.show()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = windows()
    w.show()
    sys.exit(app.exec_())