# Dataclasses for json input
Because dataclasses weren't good enough. Yes, I didn't want to faff with pydantic.

1. `json_dataclass.Element` subclasses are recursively parsed for all attributes not beginning with `_` and not `Callable`.
2. `Element` expects either a `json` payload (`str`) or `dict` structure.
   1. Json structure key is taken from the **class attribute value**
   2. Type of the element is determined by the **type hint**
   3. Processing is `type(value)`.
      1. Processing can be overridden via `_{attribute_name}` function.
      2. This should've been a `processor` decorator, but I'm lazy.
   4. Mixin classes with common keys can be regular classes and shouldn't subclass `Element` to avoid MRO conflicts.
3. `Field` class extends the json key functionality.
   1. `alt_names` allow different keys to be used.
   2. `strict` raises an exception if no keys have been found
   3. `default` allows for a default value (obviously makes `strict` useless)
4. `FieldPack` works for keys-of-keys. A `map` is expected in the inbound value with the keys present.
5. For lists or dicts of expected objects there is `ListOfElement` type and `DictOfElement` type.
   1. `AnyOfElement` can be subclassed to add new processors.
6. If a class in a type hint haven't been initialized yet, `BackReference` returns a subclass of `Element` by name
on initialization instead of compilation.
   1. I might change this to global finding.