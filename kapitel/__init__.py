import importlib
import pkgutil

ALLE_KAPITEL = sorted(
    (importlib.import_module(f"{__name__}.{m.name}").KAPITEL
     for m in pkgutil.iter_modules(__path__) if m.name.startswith("k")),
    key=lambda k: k["nr"],
)
