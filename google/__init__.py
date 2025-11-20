import pkgutil

# Allow this local `google` package to be a namespace package so that
# installed `google.*` packages (like `google.auth`) remain importable.
__path__ = pkgutil.extend_path(__path__, __name__)
