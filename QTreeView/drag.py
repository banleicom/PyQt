from PyQt5.QtWidgets import QTreeView, QFileSystemModel, QApplication, \
    QMenu, QAbstractItemView, QWidget, QHBoxLayout, QMessageBox, QMainWindow, \
    QDockWidget
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from src import config
import asyncio

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


class ItemModel(QStandardItemModel):
    def flags(self, index):
        # print('flags', index.data())
        return super(ItemModel, self).flags(index)

    def canDropMimeData(self, data, action, row, column, parent):
        # print('can drop mime data', data, action, row, column, parent.data())
        if data.hasText():
            print('can drop mime data', data.text())
        return super(ItemModel, self).canDropMimeData(data, action, row, column, parent)

    def mimeData(self, li):
        data = super(ItemModel, self).mimeData(li)
        if data:
            data.setText(li[0].data())

        return data



class Tree(QTreeView):

    def __init__(self, *args, **kwargs):
        QTreeView.__init__(self, *args, **kwargs)
        self.setHeaderHidden(True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_custom_context_menu)

        self.setSelectionMode(self.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        # self.setDropIndicatorShown(True)

        self.dmodel = ItemModel(self)
        self.setModel(self.dmodel)

        self.load_tree(self.dmodel.invisibleRootItem(), tree)

    def add_node(self, parent, value):
        item1 = QStandardItem(value)
        item1.setIcon(get_icon_by_char('a'))
        item1.setText(value)
        # item1.setData()
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


    def dragEnterEvent(self, event):
        print("bdx drop enter event", event, event.mimeData().hasText())
        # m = event.mimeData()
        # if m.hasUrls():
        #     for url in m.urls():
        #         if url.isLocalFile():
        #             event.accept()
        #             return
        # event.ignore()
        # index = self.indexAt(event.pos())
        # print(self.model().flags(index) & Qt.ItemIsDragEnabled)

        # super(Tree, self).dragEnterEvent(event)
        if event.mimeData().hasText():
            event.accept()
        else:
            super(Tree, self).dragEnterEvent(event)

    def dropEvent(self, event):

        idx = self.indexAt(event.pos())
        value = self.model().data(idx)
        source = event.source()
        if source == self:
            source_value = self.model().data(source.currentIndex())
            source_item = self.model().itemFromIndex(source.currentIndex())
            print("drop event self s: %s v: %s" % (source_value, value))
            print("drop source_item: ", source_item)
            if source_value and not source_value.startswith(value):
                print("not match")
                return
            else:
                print("match")

        else:
            # super(Tree, self).dropEvent(event)
            pass

        # super(Tree, self).dropEvent(event)
    """
    def dragMoveEvent(self, event):
        drop_indicator = self.dropIndicatorPosition()
        index = self.indexAt(event.pos())
        if drop_indicator == self.OnItem:
            text = event.mimeData().text()
            def callback(show):
                if show:
                    event.ignore()
                else:
                    super(Tree, self).dragMoveEvent(event)
            print('drag move event')
            asyncio.ensure_future(self.check_drag(callback, text, index.data()))
        else:
            super(Tree, self).dragMoveEvent(event)
    """

    """
    def dragMoveEvent(self, event):
        # print("bdx drag move event", event)
        drop_indicator = self.dropIndicatorPosition()

        index = self.indexAt(event.pos())

        if drop_indicator == self.OnItem:
            text = event.mimeData().text()
            print('text', text, type(text))
            if text:
                event.ignore()
            else:
                super(Tree, self).dragMoveEvent(event)
        else:
            super(Tree, self).dragMoveEvent(event)
    """
    def startDrag(self, actions):
        print("bdx start drag")
        if True:
            super().startDrag(actions)

    def open_menu(self):
        menu = QMenu()
        ac = menu.addAction("Create new folder")
        ac.setShortcut(Qt.CTRL | Qt.Key_A)
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
            _translate = QCoreApplication.translate
            action = menu.addAction(QIcon(get_icon_by_char('d')), "重命名")
            # action.setShortcut(Qt.CTRL | Qt.Key_A)
            action.setShortcut(Qt.CTRL | Qt.Key_P)
            action.setShortcutVisibleInContextMenu(True)
            # action.setShortcut("Ctrl+S")
            # action.setStatusTip('Exit application')
            action.triggered.connect(lambda check, pindex=QPersistentModelIndex(index):self.rename(pindex))
            print(PYQT_VERSION_STR)
            menu.exec_(QCursor.pos())

    async def check_drag(self, callback, text1, text2):
        print('check drag 1', text1, text2)
        show = await check_drag(text1, text2)
        callback and callback(show)


async def check_drag(text1, text2):
    print('check drag', text1, text2)
    return text1 == text2


class windows(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(windows, self).__init__(*args, **kwargs)

        self.dock1 = QDockWidget("tree1", self)
        self.dock2 = QDockWidget("tree2", self)
        self.dock1.setWidget(Tree(self.dock1))
        self.dock2.setWidget(Tree(self.dock2))

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock1)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock2)
        # layout = QHBoxLayout(self)
        # layout.setContentsMargins(0, 0, 0, 0)
        # layout.addWidget(Tree(self))
        # layout.addWidget(Tree(self))

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