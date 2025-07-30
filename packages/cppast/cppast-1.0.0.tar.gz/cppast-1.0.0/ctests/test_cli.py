import subprocess
import itertools
import pytest # type:ignore

def run_cli(args):
    import os
    # Set cwd to project root so relative paths like 'ctests/test0.c' work
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    result = subprocess.run(
        ["python", "-m", "core.cli"] + args,
        capture_output=True,
        text=True,
        cwd=project_root
    )
    return result

# --- Base tests for each file ---
test_files = [f"ctests/test{i}.c" for i in range(10)]

@pytest.mark.parametrize("file", test_files)
def test_ast(file):
    result = run_cli(["ast", file])
    assert "FunctionDecl" in result.stdout

@pytest.mark.parametrize("file", test_files)
def test_nodes(file):
    result = run_cli(["nodes", file])
    assert "FunctionDecl" in result.stdout

@pytest.mark.parametrize("file", test_files)
def test_leaf(file):
    result = run_cli(["leaf", file])
    assert "Identifier" in result.stdout or result.returncode == 0

@pytest.mark.parametrize("file", test_files)
def test_graph(file):
    result = run_cli(["graph", file])
    assert "Graphviz AST visualization saved" in result.stdout

@pytest.mark.parametrize("file", test_files)
def test_hash(file):
    result = run_cli(["hash", file])
    assert "WL hash:" in result.stdout

@pytest.mark.parametrize("file", test_files)
def test_json(file):
    result = run_cli(["json", file])
    assert "FunctionDecl" in result.stdout or result.returncode == 0

# --- Comparison tests within ctests only ---
file_pairs = list(itertools.combinations(test_files, 2))

@pytest.mark.parametrize("file1, file2", file_pairs)
def test_compare(file1, file2):
    result = run_cli(["compare", file1, file2])
    assert "hash:" in result.stdout
