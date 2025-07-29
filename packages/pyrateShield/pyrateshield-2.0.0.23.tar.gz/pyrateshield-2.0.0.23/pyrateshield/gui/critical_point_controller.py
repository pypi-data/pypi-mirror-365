import pandas as pd

from PyQt5.QtWidgets  import QFileDialog
from PyQt5 import QtCore


class PandasModel(QtCore.QAbstractTableModel):
    NUMBER_OF_DIGITS = 2
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.original_data = data
        data = data.copy()
        
        self._data = data
        
        for col in data.columns:
            try:
                self._data[col] = self._data[col].apply(self.precision_round)
            except:
                pass
            
        self._cols = self._data.columns
        
    def columns(self):
        columns = []
        for i in range(0, self.columnCount()):
            columns += [self.headerData(i, QtCore.Qt.Horizontal, 
                                        QtCore.Qt.DisplayRole)]
        return columns
            
        
    def sortBy(self, column_name):
        if column_name in self.columns():
            index = self.columns().index(column_name)
            self.sort(index, QtCore.Qt.AscendingOrder)

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.iloc[index.row(), index.column()]))
        return QtCore.QVariant()
    
    def headerData(self, p_int, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._cols[p_int]
            elif orientation == QtCore.Qt.Vertical:
                return p_int
        return None
    
    def precision_round(self, number, digits=None):
        if digits is None:
            digits = self.NUMBER_OF_DIGITS
            
        power = "{:e}".format(number).split('e')[1]
        return round(number, -(int(power) - digits))


def ask_new_file(title):
    extensions = "Excel files (*.xlsx)"
    filedialog = QFileDialog()
    filedialog.setFileMode(QFileDialog.ExistingFile)
    file = str(QFileDialog.getSaveFileName(filedialog, title, "",
                                           extensions)[0])
    
    return file


class CriticalPointReportController:
    _table_model = None

    def __init__(self, view=None, model=None, controller=None, dosemapper=None):
        self.dosemapper = dosemapper
        self.view = view
        self.model = model
        self.controller = controller
        self.view.save_critcial_point_button.setEnabled(False)
        
        callback = self.calculate_critical_points
        button = self.view.critical_point_button
        button.clicked.connect(callback)
        
        callback = self.save_critical_points
        button = self.view.save_critcial_point_button
        button.clicked.connect(callback)
        
        callback = self.sort
        widget = self.view.sort_list
        widget.currentIndexChanged.connect(self.sort)
        
    def sort(self):
        column_name = self.view.sort_list.currentText()
        if self.table_model is not None:
            self.table_model.sortBy(column_name)

            
    def update(self):
        self.view.table_view.setModel(self.table_model)
        
    def set_model(self, model):
        self.model = model
        self.clear()
    
    def clear(self):
        if self.table_model is not None:
            self.table_model = PandasModel(pd.DataFrame())
            self.update()
        
    
    @property
    def table_model(self):
        return self._table_model
    
    @table_model.setter
    def table_model(self, table_model):
        if table_model is None:
            self.view.save_critcial_point_button.setEnabled(False)
        else:
            self.view.save_critcial_point_button.setEnabled(True)
        self._table_model = table_model    
        
    def calculate_critical_points(self):

        sum_sources = not self.view.source_checkbox.isChecked()
        pd_report = self.dosemapper.get_critical_points(self.model, 
                                                        sum_sources=sum_sources)
       
            
        self.table_model = PandasModel(pd_report)        
        self.update()
        
    def save_critical_points(self):
        file = ask_new_file('Save to Excel')
        if file != '':
            self.table_model.original_data.to_excel(file, engine='xlsxwriter')
            
            
        
        

        
      
