import importlib
import inspect

def import_models_from_package(package_name):
    models = []
    package = importlib.import_module(package_name)
    
    for name, module in inspect.getmembers(package, inspect.ismodule):
        model_class = getattr(module, "Model", None)
        if model_class:
            models.append(model_class)
    
    return models