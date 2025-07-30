from typing import Annotated, Type, TypeVar, Sequence, Any, Generic, Union, Callable, cast, overload
from typing import _GenericAlias, GenericAlias, _SpecialGenericAlias, _UnionGenericAlias, _SpecialForm # pyright: ignore[reportUnknownVariableType, reportAttributeAccessIssue, reportPrivateUsage ]
from types import UnionType, NoneType, EllipsisType, FunctionType

from typingutils.core.compat.typevar_tuple import TypeVarTuple
from typingutils.core.attributes import (
    BASES, NAME, QUALIFIED_NAME, MODULE, ORIGIN, ARGS, PARAMETERS, TYPE_PARAMS,
    GENERIC_CONSTRUCTOR, SPECIAL_CONSTRUCTOR, BOUND, CONSTRAINTS
)

TypeParameter = Annotated[ type | type[Any], "Represents any type." ]
UnionParameter = Annotated[ UnionType | tuple[TypeParameter, ...], "Represents a union of types." ]
TypeVarParameter = Annotated[ TypeVar | TypeVarTuple, "Represents a generic type parameter." ]
AnyType = Annotated[ TypeParameter | UnionParameter | TypeVarParameter, "Represents any type, union or typevar." ]
TypeArgs = Annotated[ tuple[AnyType, ...], "Represents a sequence of types, unions or typevars." ]
AnyFunction = Annotated[ FunctionType | Callable[..., Any], "Represents any function" ]

SetOfAny = set((Any,))

GENERIC_BASE_TYPES: set[type] = set(cast(list[type], [ _GenericAlias, GenericAlias, _SpecialGenericAlias ]))
GENERIC_SPECIAL_TYPES: set[type] = set(cast(list[type], [ _SpecialGenericAlias, _SpecialForm, _UnionGenericAlias ]))


def is_generic_type(cls: AnyType) -> bool:
    """
    Indicates whether or not type is a generic type, i.e. a type capable of subscripted generics like list[T].

    Args:
        cls (AnyType): A type.

    Returns:
        bool: A boolean indicating if type is a generic type or not.
    """

    if type(cls) is TypeVar:
        return False
    elif hasattr(cls, ORIGIN):
        from typingutils.core.instances import _extract_args # pyright: ignore[reportPrivateUsage]
        parameters, args, _ = _extract_args(cls)
        return any(parameters) if parameters is not None else args is None
    elif hasattr(cls, BASES) and ( bases := getattr(cls, BASES) ) and ( Generic in bases or [ base for base in bases if is_generic_type(base) ] ):
        return True
    elif type(cls) in GENERIC_BASE_TYPES:
        return True # pragma: no cover
    else:
        return False

def _is_special_generic_type(cls: AnyType) -> bool:
    """
    Indicates if type is a special generic type from the typing module.

    Args:
        cls (AnyType): A type.

    Returns:
        bool: A boolean indicating if type is a special generic type or not.
    """

    return type(cls) in GENERIC_SPECIAL_TYPES # pragma: no cover

def is_subscripted_generic_type(cls: AnyType) -> bool:
    """Indicates whether or not `cls` is a subscripted generic type as `list[str]` is a subscripted generic type of `list[T]` etc.

    Args:
        cls (AnyType): A type.

    Returns:
        bool: Returns True if cls is a subscripted generic type.
    """
    from typingutils.core.instances import get_generic_arguments

    return hasattr(cls, ARGS) and any(get_generic_arguments(cls))

def is_variadic_tuple_type(cls: type[tuple[Any, ...]]) -> bool:
    """Indicates whether or not `cls` is a variadic tuple type, eg. `tuple[str, ...]`.

    Args:
        cls (type[tuple[Any, ...]]): A type.

    Returns:
        bool: Returns True if cls is a variadic tuple type.
    """
    from typingutils.core.instances import get_generic_arguments
    args = get_generic_arguments(cls)

    return len(args) == 2 and args[1] == Ellipsis and args[0] != Ellipsis # pyright: ignore[reportUnnecessaryComparison]

@overload
def get_generic_parameters(obj: TypeParameter | AnyFunction) -> tuple[TypeVar, ...]:
    """
    Returns the generic typevars required to create a subscripted generic type (or function, python 3.12).
    of an object. Will even work when called from within a constructor of the class.

    Examples:
        T = TypeVar('T')
        class GenClass(Generic[T]): pass
        a = get_generic_parameters(GenClass[str]) => ~T

    Args:
        obj (TypeParameter | AnyFunction): A type or function.

    Returns:
        TypeArgs: A sequence of types.
    """
    ...
@overload
def get_generic_parameters(obj: TypeParameter | AnyFunction, *, extract_types_from_typevars: bool = False) -> TypeArgs:
    """
    Returns the generic typevars required to create a subscripted generic type (or function, python 3.12).
    of an object. Will even work when called from within a constructor of the class.

    Examples:
        T = TypeVar('T')
        class GenClass(Generic[T]): pass
        a = get_generic_parameters(GenClass[str]) => ~T

    Args:
        obj (TypeParameter | AnyFunction): A type or function.
        extract_types_from_typevars (bool): Tries to extract types from TypeVars (if bound).

    Returns:
        TypeArgs: A sequence of types.
    """
    ...
def get_generic_parameters(obj: TypeParameter | AnyFunction, *, extract_types_from_typevars: bool = False) -> TypeArgs:
    for attr in (PARAMETERS, TYPE_PARAMS): # __type_params__ is new in python 3.12
        if hasattr(obj, attr):
            if params := getattr(obj, attr):
                return tuple(
                    get_types_from_typevar(param) if extract_types_from_typevars and isinstance(param, TypeVar) else param
                    for param in params
                )

    return ()

def get_type_name(cls: AnyType) -> str:
    """
    Gets the name of a type.

    Args:
        cls (AnyType): A type.

    Raises:
        Exception: An exception is raised if a type name cannot be produced.

    Returns:
        str: The name of the type.
    """

    if cls is None or cls == NoneType: # pyright: ignore[reportUnnecessaryComparison]
        return "None"
    if cls is EllipsisType:
        return "..."
    if isinstance(cls, TypeVarTuple):
        return f"*{cls}"
    if isinstance(cls, TypeVar):
        if hasattr(cls, BOUND) and ( bound := getattr(cls, BOUND) ):
            return f"{cls}<{get_type_name(bound)}>"
        elif hasattr(cls, CONSTRAINTS) and ( constraints := tuple( get_type_name(t) for t in getattr(cls, CONSTRAINTS) ) ):
            return f"{cls}<{'|'.join(constraints)}>"
        else:
            return f"{cls}"
    if isinstance(cls, tuple):
        return f"({', '.join( get_type_name(item) for item in cls )})"


    from typingutils.core.instances import get_generic_arguments
    args: Sequence[str] = [
        get_type_name(arg)
        for arg in get_generic_arguments(cls)
    ]

    if is_union(cls):
        return ' | '.join(args)

    type_name: str | None = None

    name = cls.__qualname__ if hasattr(cls, QUALIFIED_NAME) else getattr(cls, NAME) if hasattr(cls, NAME) else str(cls)

    if hasattr(cls, MODULE) and getattr(cls, MODULE) in [ "builtins", "__builtins__" ]:
        type_name = name
    elif hasattr(cls, MODULE) and not name.startswith(getattr(cls, MODULE)):
        type_name =  f"{getattr(cls, MODULE)}.{name}"
    else:
        type_name = name

    if args:
        return f"{type_name}[{', '.join(args)}]"
    elif type_name:
        return type_name
    else:
        raise Exception(f"Unable to get name of type {cls}") # pragma: no cover

def get_generic_origin(cls: AnyType) -> TypeParameter:
    """
    Gets the generic origin of a type i.e. the type a generic type originates from.

    Args:
        cls (AnyType): A type.

    Raises:
        ValueError: Raises a ValueError exception if cls is a typevar.

    Returns:
        TypeParameter: A type.
    """
    if type(cls) is TypeVar:
        raise ValueError("TypeVar is not a generic type")
    elif hasattr(cls, ORIGIN):
        return cast(type, getattr(cls, ORIGIN))
    elif isinstance(cls, UnionType):
        return UnionType # pyright: ignore[reportReturnType]

    return cast(type, cls)

def get_union_types(cls: UnionParameter) -> TypeArgs:
    """
    Returns the types which make up a union.

    Args:
        cls (UnionParameter): A union of types.

    Raises:
        ValueError: A ValueError is raised if type is not a union.

    Returns:
        TypeArgs: A sequence of types.
    """

    if type(cls) is not TypeVar and hasattr(cls, ARGS): # pyright: ignore[reportUnnecessaryComparison]
        args = tuple([
            arg
            for arg in cast(tuple[Any], getattr(cls, ARGS))
            if arg != NoneType
        ])
        return args
    else:
        raise ValueError(f"Type {get_type_name(cls)} is not a union") # pragma: no cover

def is_union(cls: AnyType) -> bool:
    """
    Indicates whenter or not type is a union of types.

    Args:
        cls (AnyType): A type.

    Returns:
        bool: Returns true if type is a union of types.
    """

    if type(cls) is TypeVar:
        return False
    elif isinstance(cls, UnionType):
        return True
    else:
       return get_generic_origin(cast(TypeParameter, cls)) is Union

def is_optional(cls: AnyType) -> bool:
    """
    Indicates if type is an optional type, i.e. a union containing None or a typing.Optional[T].

    Args:
        cls (AnyType): A type.

    Returns:
        bool: True if type is optional.
    """

    if is_union(cls):
        classes = getattr(cls, ARGS)
        if NoneType in classes:
            return True

    return False

def get_optional_type(cls: AnyType) -> tuple[AnyType, bool]:
    """
    Returns the actual type from an optional type.

    Examples:
        get_optional_type(str) # => (str, False)
        get_optional_type(Optional[str]) # => (str, True)
        get_optional_type(str | int | None) # => (str | int, True)

    Args:
        cls (AnyType): A type.

    Returns:
        tuple[AnyType, bool]: A tuple with the type and a boolean indicating if optional or not.
    """

    if is_union(cls):
        classes_org = getattr(cls, ARGS)
        optional: bool = NoneType in classes_org
        classes = [ c for c in classes_org if c != NoneType ]

        if len(classes) == 1:
            return classes[0], optional
        else:
            return cast(type, Union[tuple(classes)]), optional

    return cast(type, cls), False

def issubclass_typing(cls: AnyType, base: AnyType | TypeArgs ) -> bool:
    """
    Indicates whether or not one type is a subclass of another. This implementation
    works similarly to the builtin issubclass(), but supports generics as well.

    Args:
        cls (AnyType): A type.
        base (AnyType | TypeArgs): A type or typevar.

    Raises:
        ValueError: A ValueError is raised if cls is a typevar.

    Returns:
        bool: True if cls is an instance of base.
    """

    if isinstance(cls, (TypeVar, TypeVarTuple)):
        raise ValueError("Argument cls cannot be an instance of TypeVar or TypeVarTuple")
    if not cls:
        return False # pragma: no cover
    elif cls is base:
        return True
    elif base in (object, TypeParameter,  type[Any], Type[Any]):
        return True

    from typingutils.core.instances import get_generic_arguments, check_type

    if isinstance(base, tuple):
        for base_cls in cast(Sequence[TypeParameter], base):
            if issubclass_typing(cls, base_cls):
                return True
        return False


    cls_is_type, cls_is_generic_type, cls_is_subscripted_generic_type = check_type(cls)
    base_is_type, base_is_generic_type, base_is_subscripted_generic_type = check_type(base)
    base_args: TypeArgs = ()

    if base_is_subscripted_generic_type:
        base_args = get_generic_arguments(base)

    if base_args and set(base_args) == SetOfAny:
        base = get_generic_origin(cast(TypeParameter | UnionParameter | TypeVar, base))

    if is_union(base):
        classes = get_generic_arguments(base)
        return any([ issubclass_typing(cls, b) for b in classes ]) or cls_is_type and get_generic_origin(cast(type, cls)) is Union

    if cls_is_type:
        if base_is_type:
            if get_generic_origin(cls) is base:
                return True

            cls_args = get_generic_arguments(cls) if cls_is_subscripted_generic_type else get_union_types(cast(UnionParameter, cls)) if is_union(cls) else ()
            if base_is_generic_type:
                base_args = get_generic_parameters(cast(type[Any], base), extract_types_from_typevars = True)

            if get_generic_origin(cls) == get_generic_origin(base):
                if cls_args == base_args:
                    return True
                elif cls_args and base_args and len(cls_args) == len(base_args) and not [
                    t for t in zip(cls_args, base_args) if not issubclass_typing(t[0], t[1])
                ]:
                    return True
                else:
                    return not any(base_args)
            elif cls_is_type and not cls_is_generic_type and not cls_is_subscripted_generic_type and not base_is_subscripted_generic_type and isinstance(base, type):
                return issubclass(cast(type[Any], cls), base)

            else:
                return False

        elif type(base) is TypeVar:
            return issubclass_typing(cls, get_types_from_typevar(base))

    if cls_is_generic_type or cls_is_subscripted_generic_type or base_is_generic_type or base_is_subscripted_generic_type: # pragma: no cover
        return False

    return issubclass(cls, base) # fallback # pyright: ignore[reportArgumentType] # pragma: no cover

def get_types_from_typevar(typevar: TypeVarParameter) -> TypeParameter | UnionParameter:
    """The `get_types_from_typevar` function returns the type constraints from the typevar or typevar tuple. If no constraints are specified, `type[Any]` is returned.
    If typevar is a TypeVarTuple (new in Python 3.11), `tuple[type[Any], ...]` is returned.

    Args:
        typevar (TypeVarParameter): A typevar or typevar tuple.

    Returns:
        TypeParameter | UnionParameter: Returns the type constraints.
    """
    if isinstance(typevar, TypeVar) and hasattr(typevar, BOUND):
        if bound := getattr(typevar, BOUND):
            return Union[bound]
        elif constraints := getattr(typevar, CONSTRAINTS):
            return Union[constraints]
    elif isinstance(typevar, (TypeVar, TypeVarTuple)): # pyright: ignore[reportUnnecessaryIsInstance]
        return tuple[type[Any], ...]
    return type[Any]

def construct_generic_type(cls: type, *generic_arguments: AnyType | EllipsisType) -> type:
    generic_arguments = tuple( arg if arg != EllipsisType else Ellipsis for arg in generic_arguments )

    if hasattr(cls, GENERIC_CONSTRUCTOR): # types derived from Generic[T]
        return cast(Callable[[tuple[type, ...]], type], getattr(cls, GENERIC_CONSTRUCTOR))(generic_arguments) # pyright: ignore[reportArgumentType]
    elif _is_special_generic_type(cls): # types like Optional[T] and Union[T, ...]
        if len(generic_arguments) == 1:
            return cast(Callable[[type], type], getattr(cls, SPECIAL_CONSTRUCTOR))(generic_arguments[0]) # pyright: ignore[reportArgumentType]
        else:
            return cast(Callable[[tuple[type, ...]], type], getattr(cls, SPECIAL_CONSTRUCTOR))(generic_arguments) # pyright: ignore[reportArgumentType]
    else:
        return cast(Callable[[tuple[type, ...]], type], getattr(cls, SPECIAL_CONSTRUCTOR))(generic_arguments) # pyright: ignore[reportArgumentType] # pragma: no cover

