import Rational
from fractions import Fraction
p_inf = float("inf")
n_inf = float("-inf")

class Pair(object):
    def __init__(self, num, k):
        if num == p_inf:
            self.num = p_inf
            self.k = Fraction(k)
        elif num == n_inf:
            self.num = n_inf
            self.k = Fraction(k)
        else:
            self.num = Fraction(num)
            self.k = Fraction(k)

    # сложение чисел
    def __add__(self, other):
        return Pair(self.num + other.num, self.k + other.k)

    # умножение пар
    def __mul__(self, other):
        # if type(other) == Pair:
        #     if self.k == 0:
        #         return Pair(self.num * other[0], self.k * other[1])
        #     elif other[1] == 0:
        #         return Pair(self.num * other[0], self.k * other[0])
        # else:
        return Pair(self.num * other, self.k * other)

    # умножение пары на число
    def __rmul__(self, other):
        return Pair(other * self.num, other * self.k)

    def __truediv__(self, other):
        a = self.num / other[0]
        if other[1] == 0:
            b = self.k
        else:
            b = self.k / other[1]
        return Pair(a, b)


    #не уверена
    def __neg__(self):
        return Pair(-self.num, -self.k)

    # деление чисел
    # def __truediv__(self, other):
    #     # добавить фрэкшен
    #     return Pair(self.num / other.num, self.k / other.k)

    #пары равны
    def __eq__(self, other):
        return self.__cmp__(other) == 0

    #пары не равны
    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __getitem__(self, index):
        if index == 0:
            return self.num
        elif index == 1:
            return self.k
        else:
            return self

    # разность пар
    def __sub__(self, secondpair):
        if type(secondpair) == Pair:
            a = self.num - secondpair[0]
            b = self.k - secondpair[1]
        else:
            a = self.num - secondpair
            b = self.num - secondpair
        return Pair(a, b)


    def __cmp__(self, secondpair):
        temp = self.__sub__(secondpair)
        if temp[0] > 0:
            return 1
        elif temp[0] < 0:
            return -1
        else:
            return 0

    # пара_1 больше пара_2
    def __gt__(self, other):
        return self.__cmp__(other) > 0

    # пара_1 больше или равна пара_2
    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    # пара_1 меньше пара_2
    def __lt__(self, other):
        return self.__cmp__(other) < 0

    # пара_1 меньше или равна пара_2
    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __str__(self):
        if self.k > 0:
            if self.num != 0:
                return str(self.num) + " + " + str(self.k) + "*delta"
            else:
                return str(self.k) + "*delta"
        elif self.k < 0:
            if self.num != 0:
                return str(self.num) + " - " + str(abs(self.k)) + "*delta"
            else:
                return str(self.k) + "*delta"
        else:
            return str(self.num)
#
# a = Rational.Rational(3, 4)
# b = Rational.Rational(-5, 7)
# print(a.__str__(), b.__str__())
# c = Pair(a, b)
# print(c.__str__())
