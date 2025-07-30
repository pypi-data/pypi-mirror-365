"""This module is for matrix calculations"""
import numpy as np


n11 = int(input("n11: "))
n12 = int(input("n12: "))
n13 = int(input("n13: "))
n21 = int(input("n21: "))
n22 = int(input("n22: "))
n23 = int(input("n23: "))
n31 = int(input("n31: "))
n32 = int(input("n32: "))
n33 = int(input("n33: "))

matrix1 = np.array([[n11, n12, n13], [n21, n22, n23], [n31, n32, n33]])

m11 = int(input("m11: "))
m12 = int(input("m12: "))
m13 = int(input("m13: "))
m21 = int(input("m21: "))
m22 = int(input("m22: "))
m23 = int(input("m23: "))
m31 = int(input("m31: "))
m32 = int(input("n32: "))
m33 = int(input("m33: "))

matrix2 = np.array([[m11, m12, m13], [m21, m22, m23], [m31, m32, m33]])


def matrix_addtion():
    print("addtion of two matrices is: ",
          matrix1+matrix2)
    """
    Addtion of two matrices.

    Parameter:
    None

    returns:
    2-D array as sum of 2 matrices
    """


matrix_addtion()


def matrix_subtraction():
    print("subtraction of two matrices is: ",
          matrix1-matrix2)
    """
    Subtraction of two matrices.

    Parameter:
    None

    returns:
    2-D array as difference of 2 matrices
    """


matrix_subtraction()


def matrix_multiplication():
    a11 = (n11*m11)+(n12*m21)+(n13*m31)
    a12 = (n11*m12)+(n12*m22)+(n13*m32)
    a13 = (n11*m13)+(n12*m23)+(n13*m33)

    a21 = (n21*m11)+(n22*m21)+(n23*m31)
    a22 = (n21*m12)+(n22*m22)+(n23*m32)
    a23 = (n21*m13)+(n22*m23)+(n23*m33)

    a31 = (n31*m11)+(n32*m21)+(n33*m31)
    a32 = (n31*m12)+(n32*m22)+(n33*m32)
    a33 = (n31*m13)+(n32*m23)+(n33*m33)
    matrix3 = np.array([[a11, a12, a13], [a21, a22, a23], [a31, a32, a33]])
    print("multiplication of two matrices is:", matrix3)
    """
    Multiplication of two matrices.

    Parameter:
    None

    returns:
    2-D array as product  of 2 matrices
    """


matrix_multiplication()
