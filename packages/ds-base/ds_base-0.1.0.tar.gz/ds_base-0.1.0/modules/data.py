# === CSV PARSING ALGORITHM ===
# https://github.com/hurtki/DataSince

from io import TextIOWrapper
from typing import Callable
from numbers import Real


def get_list(csv_file: TextIOWrapper) -> list[dict]:
    """
    returns list of dictionaries from given csv file(open('file'))
    """
    columns = []
    # try to get columns from the top of csv 
    try:
        columns = csv_file.readline().strip().split(",")
    except Exception as e:
        print(f"error getting lines error: {e}")
        return [{}]

    try:
        data = csv_file.readlines()[1:]
    except Exception as e:
        print(f"error getting lines error: {e}")
        return [{}]

    array = []

    for i in range(len(data)):
        one_row = {}
        data[i] = data[i].strip()
        for j in range(len(columns)):
            try:
                one_row[columns[j]] = data[i].split(",")[j]
            except IndexError as e:
                print(f"warning getting column id:{j} in row id: {i}")
                continue
            except Exception as e:
                print(f"unexcpected error: {e}")
        array.append(one_row)

    return array


def graph(func: Callable[[float|int], float], 
          from_p: int | float, 
          to_p: int | float, 
          step: int | float, 
          canvas: str):
    """
    function that draws a nice graph using given function checking
    all x from from_p to to_p with also given step step
    REQUIRES CANVAS PARAMETRE: 'seaborn' / coming soon..
    """
    if canvas == "seaborn":
        try:
            import seaborn as sns
            import numpy as np
        except ImportError:
            print("no seaborn or numpy installed: do 'pip install seaborn numpy'")
            return
    else:
        print("supported canvases: 'seaborn'")
    X = []
    y = []
    for i in np.arange(from_p, to_p, step): 
        try:
            func_return = func(float(i))
        except Exception as e:
            continue

        X.append(i)
        y.append(func_return)
    sns.lineplot(x=X, y=y, color='g')
