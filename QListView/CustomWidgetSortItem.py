#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Created on 2018年8月4日
@author: Irony
@site: https://pyqt.site , https://github.com/PyQt5
@email: 892768447@qq.com
@file: QListView.显示自定义Widget并排序
@description:
"""
import string
from random import choice, randint
from time import time

try:
    from PyQt5.QtCore import QSortFilterProxyModel, Qt, QSize, pyqtSignal, QModelIndex, QRect, QEvent

    from PyQt5.QtGui import QStandardItem, QStandardItemModel, QPixmap, QPainter, QFont, QIcon, QCursor
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListView, \
        QHBoxLayout, QLineEdit, QApplication, QStyledItemDelegate, QStyleOptionButton, \
        QStyle, QLabel, QMenu
except ImportError:
    from PySide2.QtCore import QSortFilterProxyModel, Qt, QSize
    from PySide2.QtGui import QStandardItem, QStandardItemModel
    from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListView, \
        QHBoxLayout, QLineEdit, QApplication


def randomChar(y):
    # 返回随机字符串
    return ''.join(choice(string.ascii_letters) for _ in range(y))


def get_icon():
    # 测试模拟图标
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter()
    painter.begin(pixmap)
    painter.setFont(QFont('Webdings', 11))
    painter.setPen(Qt.GlobalColor(randint(4, 18)))
    painter.drawText(0, 0, 16, 16, Qt.AlignCenter,
                     choice(string.ascii_letters))
    painter.end()
    return QIcon(pixmap)


class CustomWidget(QWidget):

    def __init__(self, text, *args, **kwargs):
        super(CustomWidget, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.addWidget(QLineEdit(text, self))
        layout.addWidget(QPushButton(text[0:5], self))

    def sizeHint(self):
        # 决定item的高度
        return QSize(60, 40)


class SortFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, **kwargs):
        super(SortFilterProxyModel, self).__init__(*args, **kwargs)
        self._key = ''

    def set_key(self, key):
        self._key = key

    def lessThan(self, source_left, source_right):
        if not source_left.isValid() or not source_right.isValid():
            return False
        # 获取数据
        leftData = self.sourceModel().data(source_left)
        # print("bdx leftdata", leftData, type(source_left))
        rightData = self.sourceModel().data(source_right)
        if self.sortOrder() == Qt.DescendingOrder:
            # 按照时间倒序排序
            leftData = leftData.split('-')[-1]
            rightData = rightData.split('-')[-1]
            return leftData < rightData
        #         elif self.sortOrder() == Qt.AscendingOrder:
        #             #按照名字升序排序
        #             leftData = leftData.split('-')[0]
        #             rightData = rightData.split('-')[0]
        #             return leftData < rightData
        return super(SortFilterProxyModel, self).lessThan(source_left, source_right)

    def filterAcceptsRow(self, row, sourceParent):
        super(SortFilterProxyModel, self).filterAcceptsRow(row, sourceParent)
        value = self.sourceModel().index(row, 0, sourceParent).data()
        print("bdx filterAccepts row", value)
        if self._key == '' or value.startswith(self._key):
            return True
        else:
            return False


class WindowMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super(WindowMenu, self).__init__(*args, **kwargs)
        self.setFixedSize(250, 600)
        layout = QVBoxLayout(self)
        self.search = QLineEdit(self)
        self.search.editingFinished.connect(self.filterAcceptsRow)
        self.search.textChanged.connect(self.text_change)
        layout.addWidget(self.search)
        # # 名字排序
        # layout.addWidget(QPushButton('以名字升序', self, clicked=self.sortByName))
        # # 时间倒序
        # layout.addWidget(QPushButton('以时间倒序', self, clicked=self.sortByTime))
        # listview
        self.listView = QListView(self)
        layout.addWidget(self.listView)
        # 数据模型
        self.dmodel = QStandardItemModel(self.listView)
        # 排序代理模型
        self.fmodel = SortFilterProxyModel(self.listView)
        self.fmodel.setSourceModel(self.dmodel)
        self.listView.setModel(self.fmodel)
        self.listView.selectionModel().selectionChanged.connect(self.on_select)

        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 无边框、去掉自带阴影
        self.setWindowFlags(
            self.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

        # 模拟生成50条数据
        for _ in range(50):
            name = randomChar(5)
            times = time() + randint(0, 30)  # 当前时间随机+
            value = '{}-{}'.format(name, times)  # 内容用-分开
            item = QStandardItem(value)
            item.setEditable(False)
            #             item.setData(value, Qt.UserRole + 2)
            item.setIcon(get_icon())
            self.dmodel.appendRow(item)
            # 索引
            # index = self.fmodel.mapFromSource(item.index())
            # 自定义的widget
            # widget = CustomWidget(value, self)
            # item.setSizeHint(widget.sizeHint())
            # self.listView.setIndexWidget(index, widget)
        self.listView.setCurrentIndex(QModelIndex())

    def on_select(self, selectedSet, deselected):
        # str = self.dmodel.data(self.listView.currentIndex(), Qt.DisplayRole)
        # print("bdx on select", str)
        if selectedSet:
            for i in range(len(selectedSet.indexes())):
                item = selectedSet[i]
                index = selectedSet.indexes()[i]
                mts = self.fmodel.mapToSource(index)
                str = self.dmodel.data(mts)
                # self.sourceModel().data(source_left)
                # str = self.dmodel.itemData(index)
                print("bdx on select", type(mts), type(index), str)

    def sortByTime(self):
        # 按照时间倒序排序
        self.fmodel.sort(0, Qt.DescendingOrder)

    def sortByName(self):
        # 按照名字升序排序
        self.fmodel.sort(0, Qt.AscendingOrder)

    def filterAcceptsRow(self):
        key = self.search.text()
        print("bdx filter accepts row", key)
        self.fmodel.set_key(key)
        # self.fmodel.filteracceptsrow()
        # self.fmodel.sort(0, qt.ascendingorder)
        self.fmodel.setFilterRegExp("")

    def text_change(self, text):
        print("bdx text change", text)
        key = self.search.text()
        print("bdx filter accepts row", key)
        self.fmodel.set_key(key)
        # self.fmodel.filteracceptsrow()
        # self.fmodel.sort(0, qt.ascendingorder)
        self.fmodel.setFilterRegExp("")

    # def event(self, event):
    #     if event.type() == QEvent.ActivationChange:
    #         if QApplication.activeWindow() != self:
    #             self.close()
    #     return super(WindowMenu, self).event(event)

def about_qt():
    # 关于Qt
    QApplication.instance().aboutQt()


class Window(QLabel):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.resize(400, 400)
        self.setAlignment(Qt.AlignCenter)
        self.setText('右键弹出菜单')
        self.context_menu = WindowMenu(self)

    def contextMenuEvent(self, event):
        # self.context_menu.exec_(event.globalPos())
        self.context_menu.exec_(QCursor.pos())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
