import sys
import shutil
from core.cli import app, print_ast, validate_c_cpp_file
from clang.cindex import Index # type:ignore

# System dependency checks
def check_system_dependencies():
    missing = []
    # Check for clang binary
    if shutil.which("clang") is None:
        missing.append("clang")
    # Check for graphviz binary (dot)
    if shutil.which("dot") is None:
        missing.append("graphviz (dot)")
    if missing:
        print("\nERROR: The following system dependencies are required but not installed:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nPlease install them for proper cppast functionality.")
        print("\nInstall instructions:")
        print("  macOS:   brew install llvm graphviz")
        print("  Linux:  sudo apt-get install clang graphviz")
        sys.exit(1)

def main():
    check_system_dependencies()
    # If called as `cppast file.cpp` (no subcommand), print AST
    # makes cppast ast filename.cpp redundant
    if len(sys.argv) == 2 and not sys.argv[1].startswith('-'):
        file = sys.argv[1]
        validate_c_cpp_file(file, use_typer_exit=False)
        index = Index.create()
        tu = index.parse(file)
        print_ast(tu.cursor, indent="", is_last=True)
    else:
        app()

if __name__ == "__main__":
    main()
