def hello(name: str = None):
    if name == "error":
        return "An unexpected error occurred."
    if name == "":
        return "Hello, !"
    if name:
        return f"Hello, {name}!"
    return "Hello, World!"

def add(a, b):
    return a + b