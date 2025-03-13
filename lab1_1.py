import random

def fill_matrix(rows, cols):
    matrix = []
    for i in range(rows):
        row = [random.randint(0, 100) for _ in range(cols)]
        matrix.append(row)
    return matrix

def print_matrix(matrix):
    for row in matrix:
        print("\t".join(map(str, row)))
    print()  

def shift_right(matrix, n):

    rows = len(matrix)
    if rows == 0:
        return matrix
    cols = len(matrix[0])
    n = n % cols 
    new_matrix = []
    for row in matrix:
        new_row = row[-n:] + row[:-n]
        new_matrix.append(new_row)
    return new_matrix

def shift_down(matrix, n):
    rows = len(matrix)
    if rows == 0:
        return matrix
    cols = len(matrix[0])
    n = n % rows  
    new_matrix = [row[:] for row in matrix]  
    for j in range(cols):
        col = [matrix[i][j] for i in range(rows)]
        new_col = col[-n:] + col[:-n]
        for i in range(rows):
            new_matrix[i][j] = new_col[i]
    return new_matrix

def main():
    try:
        rows = int(input("Rows: "))
        cols = int(input("Cols: "))
    except ValueError:
        print("Please input integer")
        return

    matrix = fill_matrix(rows, cols)
    print("\nMatrix:")
    print_matrix(matrix)

    mode = input(" 'right' / 'down' ").strip().lower()
    try:
        shift_value = int(input("Elements to shift: "))
    except ValueError:
        print("Please input integer")
        return

    if mode == "right":
        shifted_matrix = shift_right(matrix, shift_value)
    elif mode == "down":
        shifted_matrix = shift_down(matrix, shift_value)
    else:
        print("Input 'right' / 'down' ")
        return

    print("\nMatrix after shift:")
    print_matrix(shifted_matrix)

if __name__ == '__main__':
    main()
