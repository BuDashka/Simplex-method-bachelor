# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window1.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from fractions import Fraction

from PyQt5.QtWidgets import QTableWidgetItem

import Pair
import symplex

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(720, 420)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(11, 0, 177, 700))
        self.plainTextEdit.setMaximumSize(QtCore.QSize(600, 300))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(353, 0, 300, 400))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(196, 194, 149, 32))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.calculate)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "Calculate simplex"))


    def parseIncome(self):
        #matrix_coeff = [[]]
        vars_dict = {}
        vec_B = []
        vec_obj = []

        flag_max = False    #False = min True = max
        sign_eq = [0, 0]       #(0 - меньше, 1 - больше; 0 - строгое, 1 - нестрогое)
        max_var_id = 0
        flag_obj = True     #целевая функция
        sign = 1
        curent = 0
        cur_var_number = ""
        cur_coef = ""
        line = 0
        N = ""
        num_s_var = 0
        num_r_vars = 0

        str = self.plainTextEdit.toPlainText()

        i = 0
        lenIncome = len(str)        #количество символов
        amount_equ = 0
        cur_eq = 0

        while line == 0:
            while str[i] != ':':
                while str[i] == ' ':
                    i += 1
                    curent += 1
                while str[i].isdigit():
                    N += str[i]
                    i += 1
                    curent += 1
                if len(N) > 0:
                    N = int(N)
                i += 1
                curent += 1
                while str[i] == ' ':
                    i += 1
                    curent += 1
                # i += 1
                # curent += 1
                break
            vec_obj = [Fraction(0) for i in range(0, N)]
            while str[i] != '=':
                if str[i] == '-':  # знак минус перед коэфициентом
                    sign = -1
                    i += 1
                    curent += 1
                elif str[i] == '+':
                    i += 1
                    curent += 1
                while str[i] == ' ':
                    i += 1
                    curent += 1
                while str[i].isdigit():
                    cur_coef += str[i]
                    i += 1
                    curent += 1
                if len(cur_coef) > 0:
                    cur_coef = int(cur_coef) * sign
                else:
                    cur_coef = sign
                if str[i].isalpha():  # переменная
                    cur_var_number += str[i]
                else:
                    print("неправильный ввод")
                    return 1
                if cur_var_number not in vars_dict:
                    vars_dict[str[i]] = max_var_id
                    max_var_id += 1
                    print(vars_dict[str[i]])
                    vec_obj[vars_dict[str[i]]] = Fraction(cur_coef)
                    i += 1
                    curent += 1
                else:
                    vec_obj[vars_dict[str[i]]] = cur_coef
                    i += 1
                    curent += 1
                sign = 1
                cur_var_number = ""
                cur_coef = ""
                while str[i] == ' ':
                    i += 1
                    curent += 1

            if str[i] == '=':
                temp = ""
                i += 1
                curent += 1
                while str[i] == ' ':
                    i += 1
                    curent += 1
                while str[i] != ' ' and str[i] != '\n':
                    temp += str[i]
                    i += 1
                    curent += 1
                if temp == 'max' or temp == 'maximize':
                    flag_max = True
                elif temp == 'min' or temp == 'minimize':
                    flag_max = False
                else:
                    print("неправильное введение действия")
                    return 1
                while str[i] != '\n':
                    i += 1
                    curent += 1
                line += 1
                i += 1
                curent = 0

            else:
                print("неправильныый ввод. Ожидается символ $")
                return 1

            if flag_max:
                for i in range(len(vec_obj)):
                    vec_obj[i] = -vec_obj[i]

        for j in range(i, lenIncome):
            if str[j] == ';':
                amount_equ += 1

        vec_B = [Fraction(0) for i in range(amount_equ)]
        matrix_coeff = [[Fraction(0) for i in range(amount_equ + max_var_id)] for j in range(amount_equ)]

        while i < lenIncome:
            while (str[i] != '<' and str[i] != '>'):
                # if str[i].isdigit():
                    if str[i] == '-':  # знак минус перед коэфициентом
                        sign = -1
                        i += 1
                        curent += 1
                    elif str[i] == '+':
                        i += 1
                        curent += 1
                    while str[i] == ' ':
                        i += 1
                        curent += 1
                    while str[i].isdigit():
                        cur_coef += str[i]
                        i += 1
                        curent += 1
                    if len(cur_coef) > 0:
                        cur_coef = int(cur_coef) * sign
                    else:
                        cur_coef = sign
                    if str[i].isalpha():  # переменная
                        cur_var_number += str[i]
                    else:
                        print("неправильный ввод")
                        return 1
                    if cur_var_number not in vars_dict:
                        print("переменные в ф-циях ограничения должна быть обхявлена в целевой")
                        return 1
                    else:
                        matrix_coeff[cur_eq][vars_dict[str[i]]] = Fraction(cur_coef)
                        i += 1
                        curent += 1
                    sign = 1
                    cur_var_number = ""
                    cur_coef = ""
                    while str[i] == ' ':
                        i += 1
                        curent += 1

            if str[i] == '>':
                sign_eq[0] = 1
            i += 1
            curent += 1
            if (str[i] == '='):
                sign_eq[1] = 1
                i += 1
                curent += 1

            #базисные переменные
            if sign_eq[0] == 0 and sign_eq[1] == 0:                 # <
                matrix_coeff[cur_eq][cur_eq + max_var_id] = Fraction(1)
            elif sign_eq[0] == 0 and sign_eq[1] == 1:               # <=
                matrix_coeff[cur_eq][cur_eq + max_var_id] = Pair.Pair(1, 0)
            elif sign_eq[0] == 1 and sign_eq[1] == 0:               # >
                matrix_coeff[cur_eq][cur_eq + max_var_id] = Fraction(-1)
            elif sign_eq[0] == 1 and sign_eq[1] == 1:               # >=
                matrix_coeff[cur_eq][cur_eq + max_var_id] = Fraction(-1)

            while str[i] == ' ':
                i += 1
                curent += 1
            if str[i] == '-':
                sign = -1
                curent += 1
                i += 1
            while str[i] == ' ':
                i += 1
                curent += 1
            while str[i].isdigit():
                cur_coef += str[i]
                i += 1
                curent += 1
            vec_B[cur_eq] = Fraction(cur_coef * sign)
            cur_eq += 1
            cur_coef = ""
            if cur_eq < amount_equ:
                while not str[i].isdigit() and not str[i].isalpha() and str[i] != '-':
                    i += 1
                    curent += 1
            else:
                return matrix_coeff, vec_B, vec_obj, vars_dict, N, flag_max



    def calculate(self):
        matrix_coeff, vec_B, vec_obj, vars_dict, N, flag = self.parseIncome()

        self.tableWidget.setRowCount(N+1)
        self.tableWidget.setColumnCount(2)
        i = 0
        for d in vars_dict:
            self.tableWidget.setItem(i, 0, QTableWidgetItem(d.__str__()))
            i += 1
        if flag:
            str = "F(x) max"
        else:
            str = "F(x) min"
        self.tableWidget.setItem(i, 0, QTableWidgetItem(str))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())


'''
2: 3x+y=min
y<5;
x < 2;
2x-y< 1;
x + y >= 0;

//знак >= быть не может с пробелом между > и =

'''