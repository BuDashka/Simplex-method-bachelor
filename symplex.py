import re
from fractions import Fraction
from warnings import warn
import Pair

flag_max = True
objective_func = ''
fileLines = []


class Simplex(object):
    def __init__(self, num_vars, constraints, objective_function):
        """
        num_vars: Number of variables
        equations: A list of strings representing constraints
        each variable should be start with x followed by a underscore
        and a number
        eg of constraints
        ['1x_1 + 2x_2 >= 4', '2x_3 + 3x_1 <= 5', 'x_3 + 3x_2 = 6']
        Note that in x_num, num should not be more than num_vars.
        Also single spaces should be used in expressions.
        objective_function: should be a tuple with first element
        either 'min' or 'max', and second element be the equation
        eg
        ('min', '2x_1 + 4x_3 + 5x_2')
        For solution finding algorithm uses two-phase simplex method
        """
        self.num_vars = num_vars
        self.constraints = constraints
        # cur, num_variable, b, vars_dict = self.parseInput(fileLines)
        self.objective = objective_function[0]
        self.objective_function = objective_function[1]
        self.coeff_matrix, self.r_rows, self.num_s_vars, self.num_r_vars = self.construct_matrix_from_constraints()
        del self.constraints
        self.basic_vars = [0 for i in range(len(self.coeff_matrix))]
        self.phase1()
        r_index = self.num_r_vars + self.num_s_vars

        for i in self.basic_vars:
            if i > r_index:
                raise ValueError("Infeasible solution")

        self.delete_r_vars()

        if 'minimize' in self.objective.lower():
            self.solution = self.objective_minimize()

        else:
            self.solution = self.objective_maximize()
        self.optimize_val = self.coeff_matrix[0][-1]

    # parser
    def construct_matrix_from_constraints(self):
        num_s_vars = 0  # слабые и остаточные
        num_r_vars = 0  # дополнительные переменные
        for expression in self.constraints:
            if '>=' in expression:
                num_s_vars += 1

            elif '>' in expression:
                num_s_vars += 1

            elif '<=' in expression:
                num_s_vars += 1
                num_r_vars += 1

            elif '<' in expression:
                num_s_vars += 1
                num_r_vars += 1

            elif '=' in expression:
                num_r_vars += 1

        total_vars = self.num_vars + num_s_vars + num_r_vars

        coeff_matrix = [[Pair.Pair(Fraction(0, 1), Fraction(0, 1)) for i in range(total_vars + 1)] for j in range(len(self.constraints) + 1)]
        s_index = self.num_vars
        r_index = self.num_vars + num_s_vars
        r_rows = []
        for i in range(1, len(self.constraints) + 1):
            constraint = self.constraints[i - 1].split(' ')
            flag1 = False
            flag2 = False

            for j in range(len(constraint)):

                if '_' in constraint[j]:
                    coeff, index = constraint[j].split('_')
                    if constraint[j - 1] is '-':
                        coeff_matrix[i][int(index) - 1] = Pair.Pair(Fraction(-int(coeff[:-1]), 1), Fraction(0, 1))
                    else:
                        coeff_matrix[i][int(index) - 1] = Pair.Pair(Fraction(int(coeff[:-1]), 1), Fraction(0, 1))

                elif constraint[j] == '<=':
                    coeff_matrix[i][s_index] = Pair.Pair(Fraction(1, 1), Fraction(0, 1))  # добавление остаточной переменной
                    s_index += 1

                elif constraint[j] == '<':
                    coeff_matrix[i][s_index] = Pair.Pair(Fraction(1, 1), Fraction(0, 1))  # добавление остаточной переменной
                    s_index += 1
                    flag1 = True
                    flag2 = True
                    #constraint[j] = '<='

                elif constraint[j] == '>=':
                    coeff_matrix[i][s_index] = Pair.Pair(Fraction(-1, 1), Fraction(0, 1))  # слабой переменная
                    coeff_matrix[i][r_index] = Pair.Pair(Fraction(1, 1), Fraction(0, 1))  # дополнительная
                    s_index += 1
                    r_index += 1
                    r_rows.append(i)

                elif constraint[j] == '>':
                    coeff_matrix[i][s_index] = Pair.Pair(Fraction(-1, 1), Fraction(0, 1))  # слабой переменная
                    coeff_matrix[i][r_index] = Pair.Pair(Fraction(1, 1), Fraction(0, 1))  # дополнительная
                    s_index += 1
                    r_index += 1
                    r_rows.append(i)
                    flag1 = True
                    flag2 = False
                    #constraint[j] = '>='

                elif constraint[j] == '=':
                    coeff_matrix[i][r_index] = Pair.Pair(Fraction(1, 1), Fraction(0, 1))  # дополнительная
                    r_index += 1
                    r_rows.append(i)

            if flag1 == False:
                coeff_matrix[i][-1] = Pair.Pair(Fraction(int(constraint[-1]), 1), Fraction(0, 1))  # правая часть
            elif flag2 == True:
                coeff_matrix[i][-1] = Pair.Pair(Fraction(int(constraint[-1]), 1), Fraction(-1, 1))  # правая часть
            else:
                coeff_matrix[i][-1] = Pair.Pair(Fraction(int(constraint[-1]), 1), Fraction(1, 1))  # правая часть

        return coeff_matrix, r_rows, num_s_vars, num_r_vars


    def phase1(self):
        # Objective function here is minimize r1+ r2 + r3 + ... + rn
        r_index = self.num_vars + self.num_s_vars
        for i in range(r_index, len(self.coeff_matrix[0]) - 1):
            self.coeff_matrix[0][i] = Pair.Pair(Fraction(-1, 1), Fraction(0, 1))
        for i in self.r_rows:
            self.coeff_matrix[0] = add_row(self.coeff_matrix[0], self.coeff_matrix[i])
            self.basic_vars[i] = r_index
            r_index += 1
        s_index = self.num_vars
        for i in range(1, len(self.basic_vars)):
            if self.basic_vars[i] == 0:
                self.basic_vars[i] = s_index
                s_index += 1

        # Run the simplex iterations
        key_column = max_index(self.coeff_matrix[0])
        condition = self.coeff_matrix[0][key_column] > 0

        while condition is True:
            key_row = self.find_key_row(key_column)
            self.basic_vars[key_row] = key_column
            pivot = self.coeff_matrix[key_row][key_column]
            self.normalize_to_pivot(key_row, pivot)
            self.make_key_column_zero(key_column, key_row)

            key_column = max_index(self.coeff_matrix[0])
            condition = self.coeff_matrix[0][key_column] > 0

    def find_key_row(self, key_column):
        min_val = Pair.Pair(Fraction(999999), Fraction(999999))
        min_i = 0
        for i in range(1, len(self.coeff_matrix)):
            if self.coeff_matrix[i][key_column] > 0:
                val = self.coeff_matrix[i][-1] / self.coeff_matrix[i][key_column]
                if val < min_val:
                    min_val = val
                    min_i = i
        if min_val == Pair.Pair(Fraction(999999), Fraction(999999)):
            raise ValueError("Unbounded solution")
        # elif min_val == 0:
        #     warn("Dengeneracy")
        return min_i

    def normalize_to_pivot(self, key_row, pivot):
        for i in range(len(self.coeff_matrix[0])):
            self.coeff_matrix[key_row][i] /= pivot

    def make_key_column_zero(self, key_column, key_row):
        num_columns = len(self.coeff_matrix[0])
        for i in range(len(self.coeff_matrix)):
            if i != key_row:
                factor = self.coeff_matrix[i][key_column]
                for j in range(num_columns):
                    #print("до " + self.coeff_matrix[i][j].__str__())
                    tmp = self.coeff_matrix[key_row][j] * factor
                    self.coeff_matrix[i][j] = self.coeff_matrix[i][j] - tmp
                 #   self.coeff_matrix[i][j] = self.coeff_matrix[key_row][j] * factor
#                    print("после " + self.coeff_matrix[i][j].__str__())

    def delete_r_vars(self):
        for i in range(len(self.coeff_matrix)):
            non_r_length = self.num_vars + self.num_s_vars + 1
            length = len(self.coeff_matrix[i])
            while length != non_r_length:
                del self.coeff_matrix[i][non_r_length - 1]
                length -= 1

    def update_objective_function(self):
        objective_function_coeffs = self.objective_function.split()
        for i in range(len(objective_function_coeffs)):
            if '_' in objective_function_coeffs[i]:
                coeff, index = objective_function_coeffs[i].split('_')
                if objective_function_coeffs[i - 1] is '-':
                    self.coeff_matrix[0][int(index) - 1] = Pair.Pair(Fraction(int(coeff[:-1]), 1), Fraction(0, 1))
                else:
                    self.coeff_matrix[0][int(index) - 1] = Pair.Pair(Fraction(-int(coeff[:-1]), 1), Fraction(0, 1))

    def objective_minimize(self):
        self.update_objective_function()

        for row, column in enumerate(self.basic_vars[1:]):
            if self.coeff_matrix[0][column] != 0:
                self.coeff_matrix[0] = add_row(self.coeff_matrix[0], multiply_const_row(-self.coeff_matrix[0][column],
                                                                                        self.coeff_matrix[row + 1]))

        key_column = max_index(self.coeff_matrix[0])
        condition = self.coeff_matrix[0][key_column] > 0

        while condition is True:
            key_row = self.find_key_row(key_column)
            self.basic_vars[key_row] = key_column
            pivot = self.coeff_matrix[key_row][key_column]
            self.normalize_to_pivot(key_row, pivot)
            self.make_key_column_zero(key_column, key_row)

            key_column = max_index(self.coeff_matrix[0])
            condition = self.coeff_matrix[0][key_column] > 0

        solution = {}
        for i, var in enumerate(self.basic_vars[1:]):
            if var < self.num_vars:
                solution['x_' + str(var + 1)] = self.coeff_matrix[i + 1][-1].__str__()

        for i in range(0, self.num_vars):
            if i not in self.basic_vars[1:]:
                solution['x_' + str(i + 1)] = Pair.Pair(Fraction(0, 1), Fraction(0, 1)).__str__()
        #        self.check_alternate_solution()
        return solution

    def objective_maximize(self):
        self.update_objective_function()

        for row, column in enumerate(self.basic_vars[1:]):
            if self.coeff_matrix[0][column] != 0:
                self.coeff_matrix[0] = add_row(self.coeff_matrix[0], multiply_const_row(-self.coeff_matrix[0][column],
                                                                                        self.coeff_matrix[row + 1]))

        key_column = min_index(self.coeff_matrix[0])
        condition = self.coeff_matrix[0][key_column] < 0

        while condition is True:
            key_row = self.find_key_row(key_column)
            self.basic_vars[key_row] = key_column
            pivot = self.coeff_matrix[key_row][key_column]
            self.normalize_to_pivot(key_row, pivot)
            self.make_key_column_zero(key_column, key_row)

            key_column = min_index(self.coeff_matrix[0])
            condition = self.coeff_matrix[0][key_column] < 0

        solution = {}
        for i, var in enumerate(self.basic_vars[1:]):
            if var < self.num_vars:
                solution['x_' + str(var + 1)] = self.coeff_matrix[i + 1][-1].__str__()

        for i in range(0, self.num_vars):
            if i not in self.basic_vars[1:]:
                solution['x_' + str(i + 1)] = Pair.Pair(Fraction(0, 1), Fraction(0, 1)).__str__()

        # self.check_alternate_solution()

        return solution


def add_row(row1, row2):
    row_sum = [Pair.Pair(Fraction(0, 1), Fraction(0, 1)) for i in range(len(row1))]
    for i in range(len(row1)):
        row_sum[i].num = row1[i].num + row2[i].num
        row_sum[i].k = row1[i].k + row2[i].k
    return row_sum


def max_index(row):
    max_i = 0
    for i in range(0, len(row) - 1):
        if row[i] > row[max_i]:
            max_i = i

    return max_i


def multiply_const_row(const, row):
    mul_row = []
    for i in row:
        mul_row.append(i * const)
    return mul_row


def min_index(row):
    min_i = 0
    for i in range(0, len(row)):
        if row[min_i] > row[i]:
            min_i = i

    return min_i


def isSymbol(str_i):
    return re.match(r"[a-z]", str_i)

def isDidgit(str_i):
    return re.match(r"[1-9]", str_i)

def isSign(str_i):
    return str_i == '+' or str_i == '-'

def isPlus(str_i):
    return str_i == '+'

def isMinus(str_i):
    return str_i == '-'

def isEq(str_i):
    return str_i == '='

def isLess(str_i):
    return str_i == '<'

def isMore(str_i):
    return str_i == '>'

if __name__ == '__main__':
    objective = ('maximize', '1x_1 + 2x_2')
    constraints = ['1x_2 > 0', '1x_1 - 1x_2 >= 0', '1x_1 - 3x_2 <= 6', '1x_1 + 1x_2 <= 6']
    #constraints = ('3x_1 - 7x_2 < 9', '1x_1 + 1x_2 <= 10', '3x_1 + 1x_2 <= 18', '1x_1 <= 5', '1x_2 <= 7')
    #constraints = "minimize; 1x_2 - 2x_1, 3x_1 - 7x_2 <= 9, 1x_1 + 1x_2 <= 10,3x_1 + 1x_2 <= 18,1x_1 < 5,1x_2 <= 7,5x_1 + 1x_2 >= 3"
    Lp_system = Simplex(2, constraints, objective)

    print(Lp_system.solution)
    print(Lp_system.optimize_val)
    #
    #Opening text file
    # input_obj = open("input.txt", "r")
    # input = input_obj.read()
    #
    # for line in input.splitlines():
    #     fileLines.append(line)
    # Lp_system = Simplex(3, constraints, objective)


    

#'3x_1 - 7x_2 < 9', '1x_1 + 1x_2 <= 10', '3x_1 + 1x_2 <= 18', '1x_1 <= 5', '1x_2 <= 7'