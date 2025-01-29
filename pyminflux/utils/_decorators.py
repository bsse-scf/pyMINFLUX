#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.


def deprecated(replacement=None, version=None):
    """Decorator to mark a class, a property, or a function as deprecated."""

    def decorator(obj):
        # Build the deprecation message
        message = f"{obj.__name__} is deprecated."
        if replacement:
            message += f" Use {replacement} instead."
        if version:
            message += f" It will be removed in version {version}."

        # Handle normal functions or methods
        if callable(obj) and not isinstance(obj, type):

            def wrapped(*args, **kwargs):
                import warnings

                warnings.warn(
                    message,
                    DeprecationWarning,
                    stacklevel=2,
                )
                return obj(*args, **kwargs)

            # Preserve metadata
            wrapped.__name__ = obj.__name__
            wrapped.__doc__ = f"{obj.__doc__ or ''}\n\n" f"Deprecated: {message}"
            return wrapped

        # Handle properties
        elif isinstance(obj, property):

            def deprecated_getter(instance):
                import warnings

                warnings.warn(
                    message,
                    DeprecationWarning,
                    stacklevel=2,
                )
                return obj.fget(instance)

            new_property = property(
                deprecated_getter if obj.fget else None,
                doc=(f"{obj.__doc__ or ''}\n\nDeprecated: {message}"),
            )

            if obj.fset:

                @new_property.setter
                def deprecated_setter(instance, value):
                    import warnings

                    warnings.warn(
                        f"Setting {obj.fset.__name__} is deprecated. {message}",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    obj.fset(instance, value)

            if obj.fdel:

                @new_property.deleter
                def deprecated_deleter(instance):
                    import warnings

                    warnings.warn(
                        f"Deleting {obj.fdel.__name__} is deprecated. {message}",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    obj.fdel(instance)

            return new_property

        # Handle classes
        elif isinstance(obj, type):
            # Wrap the class initializer to issue a warning
            class Wrapped(obj):
                def __init__(self, *args, **kwargs):
                    import warnings

                    warnings.warn(
                        message,
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    super().__init__(*args, **kwargs)

            Wrapped.__name__ = obj.__name__
            Wrapped.__doc__ = f"{obj.__doc__ or ''}\n\n" f"Deprecated: {message}"
            return Wrapped

        # Unsupported types
        else:
            raise TypeError(
                "The @deprecated decorator can only be used on functions, methods, properties, or classes."
            )

    return decorator
