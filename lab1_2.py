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
    
def find_k(matrix):
    matching_indices = []
    size = len(matrix)
    
    for k in range(size):
        row = matrix[k]
        column = [matrix[i][k] for i in range(size)]
        
        if row == column:
            matching_indices.append(k)
            print(f"Find k: {k}")
    return matching_indices

def main():
    
    try:
        size = input(" '8x8' / '16x16' ").strip().lower()
    except ValueError:
        print("Please input correct form")
        return

    if size == "8x8":
        matrix = fill_matrix(8, 8)
    elif size == "16x16":
        matrix = fill_matrix(16, 16)
    else:
        print("input correct form ")
        return
    

    print("\nMatrix:")
    print_matrix(matrix)
    result = find_k(matrix)
    print("\nRow:", result)    

if __name__ == '__main__':
    main()
