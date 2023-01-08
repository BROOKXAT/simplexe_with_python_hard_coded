import sys
from numpy import array
import pysimptests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFormLayout, QLineEdit, QTableWidget, QTableWidgetItem,QLabel,QComboBox,QVBoxLayout,QGridLayout
)

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.num_vars_line_edit = QLineEdit()
        self.num_constraints_line_edit = QLineEdit()
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.on_submitest)

        # Set up the layout for the first window.
        self.layout = QFormLayout()
        self.layout.addRow('Number of variables:', self.num_vars_line_edit)
        self.layout.addRow('Number of constraints:', self.num_constraints_line_edit)
        self.layout.addRow(self.submit_button)
        self.setLayout(self.layout)
        self.show()
    def on_submitest(self):
        vars=self.num_vars_line_edit.text()
        constraintes=self.num_constraints_line_edit.text()
        self.w = Contraintes_UI(int(constraintes),int(vars))
        self.w.show()
        self.hide()

        # Set the layout for the second window.
class Contraintes_UI(QWidget):
    def __init__(self, n, m):
        super().__init__()
        self.initUI(n, m)

    def initUI(self, n, m):
        grid = QGridLayout()
        self.coeffaij = []
        # Create the text boxes and add them to the grid layout
        for i in range(n):
            self.coeffaij.append([])
            for j in range(m):
                line_edit = QLineEdit()
                
                if j != m-1:
                    label = QLabel("X{} +".format(j+1))
                elif j == m-1 :
                    label = QLabel("X{} ".format(j+1))
                
                grid.addWidget(line_edit, i, 2*j)
                grid.addWidget(label, i, 2*j+1)
            line_edit2 = QLineEdit()
            combox = QComboBox()
            combox.addItem("<", 1)  # The second argument is the value for this item
            combox.addItem(">", -1)
            combox.addItem("=", 0)
            grid.addWidget(combox,i,2*m)
            grid.addWidget(line_edit2,i,2*m+1)
        combox2 = QComboBox()
        combox2.addItem('MAX',1)
        combox2.addItem('Min',-1)
        label_3 = QLabel("Fonction objectif :")
        grid.addWidget(label_3,n,0)
        grid.addWidget(combox2,n,1)

        
        for i in range(2,m+2):
            line_edit = QLineEdit()
            if i != m+1:
                    label = QLabel("X{} +".format(i-1))
            elif i == m+1 :
                    label = QLabel("X{} ".format(i-1))
            grid.addWidget(line_edit,n , 2*i-2)
            grid.addWidget(label, n, 2*i-1)
        submitButton1 = QPushButton('submit')
        grid.addWidget(submitButton1,n+1,3)
        
        self.setLayout(grid)
        submitButton1.clicked.connect(lambda :self.getTheProblem(grid,n,m,combox2.currentData()))
    def prinnnt(self,word):
        print(word)

    def getTheProblem(self,grid,n,m,MinMax):
        A = []
        q = []
        b = []
        function_obj = [grid.itemAtPosition(n, 2*i-2).widget().text() for i in range(2,m+2)]
        for i in range(n):
            line = [float(grid.itemAtPosition(i, 2*j).widget().text()) for j in range(m)]
            A.append(line)
            q.append(grid.itemAtPosition(i, 2*m).widget().currentData())
            b.append(grid.itemAtPosition(i, 2*m+1).widget().text())
        A = array(A
        )
        q = array([int(j) for j in q])
        b = array([float(k) for k in b])
        function_obj = array([float(l) for l in function_obj])
        self.sol = Solution(A,q,b,function_obj,MinMax)
        self.sol.show()
        self.hide()
        return A,q,b,function_obj

class Solution(QWidget):
    def __init__(self,A,q,b,function_obj,MinMax):
        super().__init__()
        layout = QVBoxLayout()
        pysimptests.simplexe(A,q,b,function_obj,MinMax,layout,pyqt=True)
        layout.addStretch(1)
        self.setLayout(layout)


    


app = QApplication(sys.argv)
win=MyWidget()
sys.exit(app.exec_())