"""Small regression check; this is not a security sandbox or complete scanner."""
import ast
from pathlib import Path

FORBIDDEN_IMPORTS = {
    "socket", "subprocess", "urllib", "http", "requests", "httpx",
    "pickle", "marshal", "importlib", "ctypes", "webbrowser", "shutil",
}
FORBIDDEN_CALLS = {"eval", "exec", "__import__", "system", "popen"}


def main():
    issues = []
    root = Path(__file__).resolve().parents[1]
    files = sorted((root / "src").rglob("*.py"))
    if not files:
        raise SystemExit("No source files found")
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [item.name.split(".")[0] for item in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            elif isinstance(node, ast.Call):
                target = node.func
                name = target.id if isinstance(target, ast.Name) else target.attr if isinstance(target, ast.Attribute) else ""
                if name in FORBIDDEN_CALLS:
                    issues.append(f"{path.relative_to(root)}:{node.lineno}: {name}")
            if any(name in FORBIDDEN_IMPORTS for name in names):
                issues.append(f"{path.relative_to(root)}:{node.lineno}: forbidden import")
    if issues:
        raise SystemExit("\n".join(issues))
    print(f"offline surface check: {len(files)} source files checked")


if __name__ == "__main__":
    main()
