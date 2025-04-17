import random


def fillMatrix(size, min_value=-10, max_value=123):
    return [[random.randint(min_value,max_value) for _ in range(size)] for _ in  range(size)]

def task1(matrix):
    for i, row in enumerate(matrix):
        if all(x >= 0 for x in row):
            row_sum = sum(row)
            print(f"Row {i}: sum of elements = {row_sum}")
        

def task2(matrix):
    size = len(matrix)
    diagonal_sums = []
    
    for d in range(1, size):
        diag_sum = sum(matrix[i][i + d] for i in range(size - d))
        diagonal_sums.append(diag_sum)
    
    for d in range(1, size):
        diag_sum = sum(matrix[i + d][i] for i in range(size - d))
        diagonal_sums.append(diag_sum)
    
    return max(diagonal_sums) if diagonal_sums else 0

def main():
    size = 5
    matrix = fillMatrix(size)
    for row in matrix:
        print(row)
        
    task1(matrix)
    max_sum = task2(matrix)
    print(f"The maximum sum of a diagonal among parallel main diagonals: {max_sum}")
 
if __name__ == '__main__':
    main()