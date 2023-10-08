import warnings
from functools import wraps

def deprecated(message):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator



def deprecated_class(cls):
    class DeprecatedClass(cls):
        def __init__(self, *args, **kwargs):
            warnings.warn(f"The use of {cls.__name__} is deprecated.", DeprecationWarning, stacklevel=2)
            super().__init__(*args, **kwargs)

    return DeprecatedClass

def to_be_implemented(info=None):
    def decorator(item):
        if callable(item):  # Check if item is a function
            def wrapper(*args, **kwargs):
                location_info = f"in {info}" if info else ""
                raise NotImplementedError(f"{item.__name__} {location_info} is to be implemented")
            return wrapper
        else:  # Assume item is a class
            class NewClass(item):
                def __init__(self, *args, **kwargs):
                    raise NotImplementedError(f"{item.__name__} {info} is to be implemented")
            return NewClass
    return decorator

# Usage
@to_be_implemented()
def my_function():
    pass

@to_be_implemented('MyPackage.MyModule')
def my_other_function():
    pass

@to_be_implemented()
class MyUnimplementedClass:
    pass

@to_be_implemented('MyPackage.MyModule')
class MyOtherUnimplementedClass:
    pass
# Usage
@deprecated_class
class DeprecatedClassExample:
    pass

@deprecated("This function is deprecated, use new_function instead")
def deprecated_function():
    # Function implementation
    print("Deprecated function called.")


if __name__ == "__main__":
    deprecated_function()
    deprecated_instance = DeprecatedClassExample()