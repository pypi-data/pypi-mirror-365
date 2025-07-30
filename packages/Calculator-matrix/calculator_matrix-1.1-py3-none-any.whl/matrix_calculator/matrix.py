"""This module is for matrix calculations"""
import numpy as np

print("Enter elements for matrix 1:")

matrix1 = np.array([
    [int(input("n11: ")), int(input("n12: ")), int(input("n13: "))],
    [int(input("n21: ")), int(input("n22: ")), int(input("n23: "))],
    [int(input("n31: ")), int(input("n32: ")), int(input("n33: "))]
])


print("Enter elements for matrix 2: ")

matrix2 = np.array([
    [int(input("m11: ")), int(input("m12: ")), int(input("m13: "))],
    [int(input("m21: ")), int(input("m22: ")), int(input("m23: "))],
    [int(input("m31: ")), int(input("m32: ")), int(input("m33: "))]

])


def matrix_addtion():
    """
    Addtion of two matrices.

    Parameter:
    None

    returns:
    numpy.ndarray : sum of matrix1 and matrix2
    """
    print("addtion of two matrices is:\n ",
          matrix1+matrix2)


matrix_addtion()


def matrix_subtraction():
    """
    Subtraction of two matrices.

    Parameter:
    None

    returns:
    numpy.ndarray: Difference of matrix1 matrix2
    """

    print("subtraction of two matrices is:\n ",
          matrix1-matrix2)


matrix_subtraction()


def matrix_multiplication():
    """
    Multiplication of two matrices.

    Parameter:
    None

    returns:
    numpy.ndarray:Product of matrix1 and matrix2

    """
    print("Multiplication of two matrices is:\n", np.dot(matrix1, matrix2))


matrix_multiplication()
