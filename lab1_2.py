def fill_matrix(rows, cols):
    matrix = []
    print(f"Enter the elements of a {rows}x{cols} matrix:")
    for i in range(rows):
        row = []
        for j in range(cols):
            while True:
                try:
                    val = int(input(f"  [{i}][{j}]: ").strip())
                    break
                except ValueError:
                    print("Invalid input. Please enter an integer.")
            row.append(val)
        matrix.append(row)
    return matrix

def print_matrix(matrix):
    for row in matrix:
        print("\t".join(map(str, row)))
    print()

def find_k(matrix):
    matching = []
    n = len(matrix)
    for k in range(n):
        if matrix[k] == [matrix[i][k] for i in range(n)]:
            matching.append(k)
    return matching

def sum_rows_with_negative(matrix):
    sums = {}
    for idx, row in enumerate(matrix):
        if any(x < 0 for x in row):
            sums[idx] = sum(row)
    return sums

def main():
    # size = input("Choose size ('8x8' or '16x16'): ").strip().lower()
    # if size not in ("8x8", "16x16"):
    #     print("Invalid size. Please enter '8x8' or '16x16'.")
    #     return

    # rows, cols = map(int, size.split('x'))
    matrix = [
    [ 4,  5, -7,  1,  2,  3,  6,  8],
    [ 9,  0, 12,  7,  4,  1,  2,  3],
    [-7, 12, -7,  8,  3,  0,  5,  9],  
    [ 1,  4,  8,  6,  7,  2,  8,  0],
    [ 3,  2,  3,  4,  9,  5,  1,  7],
    [ 8,  6,  0,  9,  1,  4,  3,  2],
    [ 5,  9,  5,  2,  8,  6,  7,  1],
    [ 0,  1,  9,  3,  0,  9,  4,  6],
]

    print("\nMatrix:")
    print_matrix(matrix)

    matching_k = find_k(matrix)
    message = f"Indices k where k-th row equals k-th column: {matching_k}" if matching_k \
              else "No k found where a row equals its corresponding column."
    print(message)

    neg_sums = sum_rows_with_negative(matrix)
    if neg_sums:
        print("\nSum of elements in rows containing at least one negative element:")
        print(*[f"Row {idx}: sum = {total}" for idx, total in neg_sums.items()], sep="; ")
    else:
        print("\nNo rows contain negative elements.")


if __name__ == "__main__":
    main()
