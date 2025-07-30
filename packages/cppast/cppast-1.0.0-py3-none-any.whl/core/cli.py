# Validate if the file works

def validate_c_cpp_file(file: str, use_typer_exit: bool = True):
    """Check if file exists and is a valid C/C++ file. Exit with message if not."""
    if not os.path.exists(file):
        typer.echo(f"Warning: File not found: {file}")
        if use_typer_exit:
            raise typer.Exit(1)
        else:
            import sys
            sys.exit(1)
    if not file.lower().endswith((".c", ".cpp", ".cc", ".cxx")):
        typer.echo("Error: Only C/C++ files are supported (.c, .cpp, .cc, .cxx). Please provide a valid file.")
        if use_typer_exit:
            raise typer.Exit(1)
        else:
            import sys
            sys.exit(1)
    
import os
import typer # type:ignore
from clang.cindex import Index, Config # type:ignore
import networkx as nx # type:ignore
from core.utils import print_ast, visualize_ast_graphviz, ast_to_nx, ast_to_json
from core.patterns import CodePatternMatcher
import platform
import sys

app = typer.Typer()

# Set to default libclang paths when you install it via brew on Darwin, Windows or Linux
# If you have a custom path for brew installation, you need to modify libclang_path
libclang_path = os.environ.get("LIBCLANG_PATH")
if not libclang_path:
    system = platform.system()
    if system == "Darwin":
        libclang_path = "/opt/homebrew/opt/llvm/lib/libclang.dylib"
    elif system == "Windows":
        libclang_path = r"C:\Program Files\LLVM\bin\libclang.dll"
    else:
        libclang_path = "/usr/lib/llvm-14/lib/libclang.so"
try:
    if libclang_path:
        Config.set_library_file(libclang_path)
    # Try to load libclang to check if it's available
    Index.create()
except Exception as e:
    print("\n[WARNING] libclang could not be loaded.\n"
          "Please ensure LLVM/Clang is installed and libclang is available on your system.\n"
          f"Error details: {e}\n", file=sys.stderr)

# Opening menu after cppast --help
@app.command(hidden=True)
def main(
    file: str = typer.Argument(None, help="C++ source file to analyze"),
    graph: bool = typer.Option(False, "--graph", help="Generate input_ast.dot and ast.svg"),
    hash: bool = typer.Option(False, "--hash", help="Output Weisfeiler-Lehman graph hash"),
    json: bool = typer.Option(False, "--json", help="Export AST as JSON"),
    compare: list[str] = typer.Option(None, "--c", help="Compare hash/isomorphism with other files")
):
    if not file:
        typer.echo("Please provide a C/C++ source file.")
        raise typer.Exit(1)
    validate_c_cpp_file(file)
    index = Index.create()

# cppast file_name.cpp
# Print AST as a tree in the terminal.
@app.command()
def ast(file: str = typer.Argument(..., help="C++ source file to analyze")):
    """Print AST as a tree in the terminal."""
    validate_c_cpp_file(file)
    index = Index.create()
    tu = index.parse(file)
    print_ast(tu.cursor, indent="", is_last=True)

# cppast --nodes file_name.cpp
@app.command(help="Print all AST node names (kinds and spellings) in the AST.")
def nodes(file: str = typer.Argument(..., help="C++ source file to list AST node names")):
    """Print all AST node names (kinds and spellings)."""
    validate_c_cpp_file(file)
    index = Index.create()
    tu = index.parse(file)
    def visit(cursor):
        label = ''.join([w.capitalize() for w in cursor.kind.name.lower().split('_')])
        if cursor.spelling:
            label += f" '{cursor.spelling}'"
        typer.echo(label)
        for child in cursor.get_children():
            visit(child)
    visit(tu.cursor)

# cppast --leaf file_name.cpp
# Print all AST leaf node names (kinds and spellings).
@app.command(help="Print all AST leaf node names (kinds and spellings) in the AST.")
def leaf(file: str = typer.Argument(..., help="C++ source file to list AST leaf node names")):
    """Print all AST leaf node names (kinds and spellings)."""
    validate_c_cpp_file(file)
    index = Index.create()
    tu = index.parse(file)
    def visit(cursor):
        children = list(cursor.get_children())
        if not children:
            label = ''.join([w.capitalize() for w in cursor.kind.name.lower().split('_')])
            if cursor.spelling:
                label += f" '{cursor.spelling}'"
            typer.echo(label)
        for child in children:
            visit(child)
    visit(tu.cursor)

# cppast --graph file_name.cpp
# Generate input_ast.dot and ast.svg.
@app.command()
def graph(file: str = typer.Argument(..., help="C++ source file to analyze")):
    """Generate input_ast.dot and ast.svg."""
    validate_c_cpp_file(file)
    index = Index.create()
    tu = index.parse(file)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file))[0] + "_ast"
    output_path = os.path.join(output_dir, base_name)
    dot = visualize_ast_graphviz(tu.cursor)
    svg_path = dot.render(output_path, format="svg", view=True)
    typer.echo(f"Graphviz AST visualization saved as {svg_path} (SVG, high quality, scalable). Opened in your default viewer.")
    dot.save(output_path)
    typer.echo(f"Graphviz DOT file saved as {output_path} (for further processing or visualization).")

# cppast --hash file_name.cpp
# Output Weisfeiler-Lehman graph hash.
@app.command()
def hash(file: str = typer.Argument(..., help="C++ source file to hash")):
    """Output Weisfeiler-Lehman graph hash."""
    validate_c_cpp_file(file)
    index = Index.create()
    tu = index.parse(file)
    matcher = CodePatternMatcher()
    h = matcher.hash_ast(tu.cursor)
    typer.echo(f"WL hash: {h}")

# cppast --json file_name.cpp
# Export AST as JSON and save to output folder.
@app.command()
def json(file: str = typer.Argument(..., help="C++ source file to export as JSON")):
    """Export AST as JSON and save to output folder."""
    validate_c_cpp_file(file)
    index = Index.create()
    tu = index.parse(file)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file))[0] + "_ast.json"
    output_path = os.path.join(output_dir, base_name)
    with open(output_path, "w") as f:
        f.write(ast_to_json(tu.cursor))
    typer.echo(f"AST JSON saved as {output_path}")

# cppast --compare file_name1.cpp file_name2.cpp
# Compare hash/isomorphism with other files.
@app.command()
def compare(file: str = typer.Argument(..., help="First C++ file"), files: list[str] = typer.Argument(..., help="Other C++ files to compare")):
    """Compare hash/isomorphism with other files."""
    validate_c_cpp_file(file)
    index = Index.create()
    tu = index.parse(file)
    matcher = CodePatternMatcher()
    h1 = matcher.hash_ast(tu.cursor)
    g1 = ast_to_nx(tu.cursor)
    for f in files:
        try:
            validate_c_cpp_file(f)
        except typer.Exit:
            continue
        tu2 = Index.create().parse(f)
        h2 = matcher.hash_ast(tu2.cursor)
        g2 = ast_to_nx(tu2.cursor)
        is_iso = nx.is_isomorphic(g1, g2, node_match=lambda n1, n2: n1['kind'] == n2['kind'])
        typer.echo(f"{file} hash: {h1}\n{f} hash: {h2}")
        if is_iso:
            typer.echo("Match! ASTs are isomorphic.")
        else:
            typer.echo("No match! ASTs are not isomorphic.")

if __name__ == "__main__":
    app()
