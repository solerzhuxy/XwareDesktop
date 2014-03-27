# -*- coding: utf-8 -*-

import logging

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QListWidgetItem
from .ui_scheduler import Ui_Dialog

import Schedule

class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, parent):
        super().__init__(parent)


class SchedulerWindow(QDialog, Ui_Dialog):
    app = None
    scheduler = None

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.app = QApplication.instance()
        self.scheduler = self.app.scheduler
        self.loadFromScheduler()


    def loadFromScheduler(self):
        # actWhen ComboBox
        for row, pair in enumerate(self.scheduler.POSSIBLE_ACTWHENS):
            self.comboBox_actWhen.addItem(pair[1])
            self.comboBox_actWhen.setItemData(row, pair[0])

        self.slotActWhenChanged(self.scheduler.actWhen)
        self.comboBox_actWhen.setCurrentIndex(self.scheduler.actWhen)
        self.comboBox_actWhen.activated[int].connect(self.slotActWhenChanged)

        # tasks list
        runningTasks = self.app.etmpy.runningTasksStat.getTasks()
        waitingTaskIds = self.scheduler.waitingTaskIds
        for rTaskId, rTask in runningTasks.items():
            item = QListWidgetItem(rTask["name"])
            item.setData(Qt.UserRole, rTaskId)
            self.listWidget_tasks.addItem(item)

            # must be set before being added
            if rTaskId in waitingTaskIds:
                item.setSelected(True)
            else:
                item.setSelected(False)

        # action comboBox
        for row, pair in enumerate(self.scheduler.POSSIBLE_ACTIONS):
            self.comboBox_action.addItem(pair[1])
            self.comboBox_action.setItemData(row, pair[0])
        self.comboBox_action.setCurrentIndex(self.scheduler.action)

    @pyqtSlot(int)
    def slotActWhenChanged(self, choice):
        if choice == Schedule.ALL_TASKS_COMPLETED:
            self.listWidget_tasks.setEnabled(False)
        elif choice == Schedule.SELECTED_TASKS_COMPLETED:
            self.listWidget_tasks.setEnabled(True)
        else:
            raise Exception("Unknown Scheduler actWhen")

    @pyqtSlot()
    def accept(self):
        actWhen = self.comboBox_actWhen.currentData()
        taskIds = set(map(lambda item: item.data(Qt.UserRole),
                                  self.listWidget_tasks.selectedItems()))
        action = self.comboBox_action.currentData()

        self.scheduler.set(actWhen, taskIds, action)
        self.close()
