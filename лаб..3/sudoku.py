import pathlib, random, multiprocessing, time
import typing as tp

T = tp.TypeVar("T")


def read_sudoku(path: tp.Union[str, pathlib.Path]) -> tp.List[tp.List[str]]:
    """ Прочитать Судоку из указанного файла """
    path = pathlib.Path(path)
    with path.open() as f:
        puzzle = f.read()
    return create_grid(puzzle)


def run_solve(filename: str) -> None:
    grid = read_sudoku(filename)
    display(grid)
    # start = time.time()
    solution = solve(grid)
    if not solution:
        print(f"Puzzle {filename} can't be solved")
    else:
        display(solution)
    # end = time.time()
    # print(f"{filename}: {end-start}")


def create_grid(puzzle: str) -> tp.List[tp.List[str]]:
    digits = [c for c in puzzle if c in "123456789."]
    grid = group(digits, 9)
    return grid


def display(grid: tp.List[tp.List[str]]) -> None:
    """Вывод Судоку """
    width = 2
    line = "+".join(["-" * (width * 3)] * 3)
    for row in range(9):
        print(
            "".join(
                grid[row][col].center(width) + ("|" if str(col) in "25" else "") for col in range(9)
            )
        )
        if str(row) in "25":
            print(line)
    print()


def group(values: tp.List[T], n: int) -> tp.List[tp.List[T]]:
    """
    Сгруппировать значения values в список, состоящий из списков по n элементов
    >>> group([1,2,3,4], 2)
    [[1, 2], [3, 4]]
    >>> group([1,2,3,4,5,6,7,8,9], 3)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    grouped_values = [values[i:i+n] for i in range(0, len(values), n)]
    return grouped_values


def get_row(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера строки, указанной в pos
    >>> get_row([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '2', '.']
    >>> get_row([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (1, 0))
    ['4', '.', '6']
    >>> get_row([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (2, 0))
    ['.', '8', '9']
    """
    # Output of the element row
    return grid[pos[0]]


def get_col(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера столбца, указанного в pos
    >>> get_col([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '4', '7']
    >>> get_col([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (0, 1))
    ['2', '.', '8']
    >>> get_col([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (0, 2))
    ['3', '6', '9']
    """
    # Output of the element col
    return [row[pos[1]] for row in grid]


def get_block(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения из квадрата, в который попадает позиция pos
    >>> grid = read_sudoku('puzzle1.txt')
    >>> get_block(grid, (0, 1))
    ['5', '3', '.', '6', '.', '.', '.', '9', '8']
    >>> get_block(grid, (4, 7))
    ['.', '.', '3', '.', '.', '1', '.', '.', '6']
    >>> get_block(grid, (8, 8))
    ['2', '8', '.', '.', '.', '5', '.', '7', '9']
    """
    # Output of the element block
    left_borders = [pos[0] - pos[0]%3, pos[1] - pos[1]%3]
    block = [grid[i][j] for i in range(left_borders[0], left_borders[0] + 3) for j in range(left_borders[1], left_borders[1] + 3)]
    return block


def find_empty_positions(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.Tuple[int, int]]:
    """Найти первую свободную позицию в пазле
    >>> find_empty_positions([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']])
    (0, 2)
    >>> find_empty_positions([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']])
    (1, 1)
    >>> find_empty_positions([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']])
    (2, 0)
    """
    # Search for the first empty position
    for i in range(len(grid)):
        if "." in grid[i]:
            return (i, grid[i].index('.'))



def find_possible_values(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.Set[str]:
    """Вернуть множество возможных значения для указанной позиции
    >>> grid = read_sudoku('puzzle1.txt')
    >>> values = find_possible_values(grid, (0,2))
    >>> values == {'1', '2', '4'}
    True
    >>> values = find_possible_values(grid, (4,7))
    >>> values == {'2', '5', '9'}
    True
    """
    # Search for all possible values in a given position
    values = set()
    for nums in '123456789':
        if nums not in get_row(grid, pos) and nums not in get_col(grid, pos) and nums not in get_block(grid, pos):
            values.add(nums)
    return values


def solve(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.List[tp.List[str]]]:
    empty_position = find_empty_positions(grid)
    if empty_position is None:
        return grid
    possible_values = find_possible_values(grid, empty_position)
    # search through all possible options
    for value in possible_values:
        old_value = grid[empty_position[0]][empty_position[1]]
        grid[empty_position[0]][empty_position[1]] = value
        temp = solve(grid)
        if temp is not None:
            return temp
        # roll back the program if the position value is unsuitable
        grid[empty_position[0]][empty_position[1]] = old_value


def check_solution(solution: tp.List[tp.List[str]]) -> bool:
    """ Если решение solution верно, то вернуть True, в противном случае False """
    for i in range(9):
        # checking if there are identical values in the rows and cols, also checking there are empty values
        if "." in solution[i]:
            return False
        row = get_row(solution, (i, 0))
        col = get_row(solution, (0, i))
        if len(row) != len(set(row)) or len(col) != len(set(col)):
            return False
    # checking if there are identical values in the blocks
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            block = get_block(solution, (i, j))
            if len(block) != len(set(block)):
                return False
    return True

def generate_sudoku(N: int) -> tp.List[tp.List[str]]:
    """Генерация судоку заполненного на N элементов
    >>> grid = generate_sudoku(40)
    >>> sum(1 for row in grid for e in row if e == '.')
    41
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(1000)
    >>> sum(1 for row in grid for e in row if e == '.')
    0
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(0)
    >>> sum(1 for row in grid for e in row if e == '.')
    81
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    """
    if N > 81:
        N = 81

    grid = [['.'] * 9 for _ in range(9)]

    for i in range(0, 9, 3):
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        random.shuffle(numbers)

        # randomly arrange the numbers diagonally blocks
        for j in range(3):
            for k in range(3):
                grid[i + j][i + k] = str(numbers.pop())

    # completely fill the sudoku with numbers
    solution = solve(grid)
    if not solution:
        return generate_sudoku(N)

    # remove the value from sudoku until the number of filled cells is equal to N
    counter = 81
    while counter != N:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if solution[row][col] != ".":
            solution[row][col] = "."
            counter -= 1

    return solution



if __name__ == "__main__":
    for filename in ("puzzle1.txt", "puzzle2.txt", "puzzle3.txt"):
        run_solve(filename)
        # p = multiprocessing.Process(target=run_solve, args=(filename,))
        # p.start()
