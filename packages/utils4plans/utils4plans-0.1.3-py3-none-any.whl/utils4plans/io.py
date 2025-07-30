from pathlib import Path
import json
import pickle

import networkx as nx
from utils4plans.printing import StyledConsole


class NotImplementedError(Exception):
    pass


def get_or_make_folder_path(root_path: Path, folder_name: str):
    path_to_outputs = root_path / folder_name
    if not path_to_outputs.exists():
        path_to_outputs.mkdir()

    return path_to_outputs


def write_graph(G: nx.Graph, name: str, folder_path):
    G_json = nx.node_link_data(G, edges="edges")  # pyright: ignore[reportCallIssue]
    with open(folder_path / f"{name}.json", "w+") as file:
        json.dump(G_json, default=str, fp=file)


def read_graph(name: str, folder_path: Path):
    with open(folder_path / f"{name}.json", "r") as file:
        d = json.load(file)
    G: nx.Graph = nx.node_link_graph(d, edges="edges")  # pyright: ignore[reportCallIssue]
    return G


def write_pickle(item, folder_path: Path, file_name: str):
    path = folder_path / f"{file_name}.pickle"
    if path.exists():  # TODO handle overwriting in a unified way..
        raise Exception(f"File already exists at {path} - try another name")
    with open(path, "wb") as handle:
        pickle.dump(item, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Wrote pickle to {path.parent} / {path.name}")


def read_pickle(folder_path: Path, file_name: str):
    with open(folder_path / f"{file_name}.pickle", "rb") as handle:
        result = pickle.load(handle)

    return result

def check_folder_exists_and_return(p: Path):
    assert p.exists(), StyledConsole.print(f"Error: {p} does not exist", style="error")
    return p
    # TODO -> handle different behavior if doesnt exist.. 


if __name__ == "__main__":
    pass


