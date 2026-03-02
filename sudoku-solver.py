#!/usr/bin/env python
# vim: set ft=python :

import argparse
import contextlib
import itertools
import math
import shutil
import textwrap
from pathlib import Path

from ortools.sat.python import cp_model


class SudokuModelSolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, solution_limit, variables, num_rows, output_dir, sep):
        super().__init__()
        self._output_dir = output_dir
        self._row_idx_range = range(num_rows)
        self._sep = sep
        self.__solution_count = 0
        self.__solution_limit = solution_limit
        self.__variables = variables

    def on_solution_callback(self):
        path = self._output_dir.joinpath(str(self.__solution_count))
        with path.open(mode="wt") as fobj:
            for i in self._row_idx_range:
                fobj.write(
                    self._sep.join(
                        map(
                            str,
                            (self.Value(self.__variables[(i, j)]) for j in self._row_idx_range),
                        )
                    )
                )
                fobj.write("\n")
        self.__solution_count += 1

        solution_limit = self.__solution_limit
        if solution_limit and self.__solution_count >= solution_limit:
            self.StopSearch()

    def solution_count(self):
        return self.__solution_count


def read_sudoku_model(fobj, sep):
    rows = [
        [int(value) if value else None for value in line.rstrip("\n").split(sep)] for line in fobj
    ]

    num_rows = len(rows)
    if not num_rows:
        msg = "the input must not be empty"
        raise ValueError(msg)
    if not all(len(row) == num_rows for row in rows):
        msg = "the number of columns must equal the number of rows"
        raise ValueError(msg)
    block_size = math.isqrt(num_rows)
    if block_size**2 != num_rows:
        msg = "the number of rows must be a perfect square"
        raise ValueError(msg)

    model = cp_model.CpModel()
    model_vars = {}
    block_idx_range = range(block_size)
    row_idx_range = range(num_rows)

    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            var = model.NewIntVar(1, num_rows, f"{i}:{j}")
            if value is not None:
                if not 1 <= value <= num_rows:
                    msg = f"encountered unexpected value {value}"
                    raise ValueError(msg)
                model.Add(var == value)
            model_vars[(i, j)] = var

    for i in row_idx_range:
        model.AddAllDifferent([model_vars[(i, j)] for j in row_idx_range])
        model.AddAllDifferent([model_vars[(j, i)] for j in row_idx_range])

    for i, j in itertools.product(block_idx_range, repeat=2):
        model.AddAllDifferent([
            model_vars[(block_size * i + I, block_size * j + J)]
            for I in block_idx_range
            for J in block_idx_range
        ])

    return model, model_vars, num_rows


def main(input_file, output_dir, sep, solution_limit):
    if solution_limit < 0:
        msg = "if specified, solution limit must be non-negative"
        raise ValueError(msg)

    with input_file.open() as fobj:
        model, model_vars, num_rows = read_sudoku_model(fobj, sep)

    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    solver = cp_model.CpSolver()
    callback = SudokuModelSolutionCallback(
        solution_limit,
        model_vars,
        num_rows,
        output_dir,
        sep,
    )
    status = solver.SearchForAllSolutions(model, callback)

    print(
        textwrap.dedent(f"""\
            Status:          {solver.StatusName(status)}
            Solutions found: {callback.solution_count()}
            Wall time:       {solver.WallTime()}
            Branches:        {solver.NumBranches()}
            Conflicts:       {solver.NumConflicts()}""")
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output-dir",
        default=Path(__file__).with_name("output"),
        type=Path,
        help="Sudoku puzzle solutions will be written to this directory",
    )
    parser.add_argument(
        "--sep",
        default=",",
        help="separator delimiting values within a row (input and output)",
    )
    parser.add_argument(
        "--solution-limit",
        default=1,
        type=int,
        help="limit the number of solutions to this value (0 for no limit)",
    )
    parser.add_argument(
        "input_file",
        metavar="INPUT_FILE",
        type=Path,
        help="Sudoku puzzle will be read from this file",
    )
    args = parser.parse_args()

    main(
        input_file=args.input_file,
        output_dir=args.output_dir,
        sep=args.sep,
        solution_limit=args.solution_limit,
    )
