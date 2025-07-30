from __future__ import annotations
import re
from typing import Type, Dict, Any, Optional, List, cast, TypeVar, Generic, Callable
from datetime import datetime, timezone
from pydantic import BaseModel, create_model, Field as PydanticField, ConfigDict, ValidationError as PydanticValidationError
import abc
import inspect

from .fields import Field
from .exceptions import ValidationError

# Type variables for Generic classes to preserve subclass information
D = TypeVar("D", bound="Document")
C = TypeVar("C", bound="Collection")
T_Document = TypeVar("T_Document", bound=BaseModel)


class FirestoreNode(abc.ABC):
    """Base class for any node in the Firestore tree (collection or document)."""
    _path_template: str
    _path_params_model: Optional[Type[BaseModel]] = None

    # Subclasses are expected to define this
    class PathParams: ...

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Dynamically create a Pydantic model for path parameters
        if hasattr(cls, 'PathParams'):
            path_param_fields: Dict[str, Any] = {
                name: (typ, PydanticField(...))
                for name, typ in inspect.get_annotations(cls.PathParams).items()
            }
            if path_param_fields:
                cls._path_params_model = create_model(
                    f"{cls.__name__}PathParamsModel",
                    __config__=None,
                    __base__=None,
                    __module__=__name__,
                    __validators__=None,
                    **path_param_fields,
                )

    def __init__(self, **kwargs: str) -> None:
        if self._path_params_model:
            try:
                self._path_params_model.model_validate(kwargs)
            except PydanticValidationError as e:
                raise ValidationError(f"Invalid path parameters for {self.__class__.__name__}: {e}") from e
        self._path_params = kwargs
        self._path = ""  # Path will be set by the factory/creator

    @classmethod
    def path(cls, **kwargs: Any) -> str:
        """Returns the fully rendered path for this node, validating path parameters."""
        if not hasattr(cls, '_path_template'):
            raise NotImplementedError(f"Class {cls.__name__} must define _path_template")
        if cls._path_params_model:
            try:
                cls._path_params_model.model_validate(kwargs)
            except PydanticValidationError as e:
                raise ValidationError(f"Invalid path parameters for {cls.__name__}: {e}") from e
        return cls._path_template.format(**kwargs)

    @property
    def instance_path(self) -> str:
        """Returns the fully rendered path for this node instance."""
        return self._path

    @classmethod
    def template(cls) -> str:
        """Returns the raw path template for the class."""
        if not hasattr(cls, '_path_template'):
            raise NotImplementedError(f"Class {cls.__name__} must define _path_template")
        return cls._path_template

class Document(FirestoreNode):
    @classmethod
    def get_doc_id_key(cls) -> str | None:
        """Parses _path_template to find the dynamic document ID key name."""
        if not hasattr(cls, '_path_template'):
            return None
        match = re.search(r'\{([^{}]+)\}', cls._path_template)
        return match.group(1) if match else None

    """Represents a document in Firestore, defined by its Fields and Subcollections."""
    class PathParams: ...
    class Fields: ...
    class Subcollections: ...
    class SubcollectionNames: ...

    _pydantic_model: Type[BaseModel] = BaseModel
    _pydantic_partial_model: Type[BaseModel] = BaseModel
    _subcollections: Dict[str, SubcollectionType] = {}
    _field_definitions: Dict[str, Field] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # --- Pydantic Field Model Generation ---
        pydantic_fields: Dict[str, Any] = {}
        cls._field_definitions = {}
        if hasattr(cls, 'Fields'):
            for name, field_obj in vars(cls.Fields).items():
                if isinstance(field_obj, Field):
                    cls._field_definitions[name] = field_obj
                    field_type = field_obj.field_type
                    pydantic_field_args = {}
                    if not field_obj.required:
                        field_type = Optional[field_type]
                        if field_obj.default is None and field_obj.default_factory is None:
                            pydantic_field_args['default'] = None
                    if field_obj.auto_now_add:
                        pydantic_field_args['default_factory'] = lambda: datetime.now(timezone.utc)
                    elif field_obj.default_factory is not None:
                        pydantic_field_args['default_factory'] = field_obj.default_factory
                    elif field_obj.default is not None:
                        pydantic_field_args['default'] = field_obj.default
                    pydantic_field_info = PydanticField(**{**pydantic_field_args, **field_obj.kwargs})
                    pydantic_fields[name] = (field_type, pydantic_field_info)
        model_name = f"{cls.__name__}Model"
        config = ConfigDict(arbitrary_types_allowed=True)
        cls._pydantic_model = create_model(model_name, __config__=config, **pydantic_fields)
        partial_pydantic_fields = {}
        for name, field_obj in cls._field_definitions.items():
            pydantic_field_info = PydanticField(default=None, **field_obj.kwargs)
            partial_type = Optional[field_obj.field_type]
            partial_pydantic_fields[name] = (partial_type, pydantic_field_info)
        partial_model_name = f"{cls.__name__}PartialModel"
        cls._pydantic_partial_model = create_model(partial_model_name, __config__=config, **partial_pydantic_fields)

        # --- Method Delegation --- 
        # Delegate Pydantic's methods to the class so they can be called directly
        # e.g., UserDocument.model_validate(data)
        for method_name in ['model_validate', 'model_validate_json', 'model_dump', 'model_dump_json']:
            if hasattr(cls._pydantic_model, method_name):
                setattr(cls, method_name, getattr(cls._pydantic_model, method_name))

        # --- Typed Subcollection Accessor Generation ---
        cls._subcollections = {}
        if hasattr(cls, 'Subcollections'):
            for name, subcoll_type in vars(cls.Subcollections).items():
                if isinstance(subcoll_type, SubcollectionType):
                    upper_name = name.upper()
                    cls._subcollections[name.lower()] = subcoll_type

                    class SubcollectionAccessor(Generic[C]):
                        def __init__(self, subcoll_type: SubcollectionType[C]):
                            self.subcoll_type = subcoll_type

                        def __get__(self, instance: Optional[Document], owner: Type[Document]) -> C:
                            if instance is None:
                                raise AttributeError(f"Subcollection '{upper_name}' can only be accessed on a Document instance.")
                            
                            coll_class = self.subcoll_type.collection_class
                            # The document's path is the base path for its subcollection.
                            subcollection_instance = coll_class(base_path=instance.instance_path, **instance._path_params)
                            return cast(C, subcollection_instance)

                    setattr(cls, upper_name, SubcollectionAccessor(subcoll_type))

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> BaseModel:
        try:
            return cls._pydantic_model.model_validate(data)
        except PydanticValidationError as e:
            raise ValidationError(str(e)) from e

    @classmethod
    def parse(cls, data: Dict[str, Any]) -> BaseModel:
        return cls.validate(data)

    @classmethod
    def serialize(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        validated_model = cls.validate(data)
        return validated_model.model_dump(exclude_none=True)
    
    @classmethod
    def validate_partial(cls, data: Dict[str, Any], fields_to_update: Optional[List[str]] = None) -> Dict[str, Any]:
        if not cls._field_definitions:
            return data
        if fields_to_update is None:
            fields_to_update = list(data.keys())
        valid_fields = set(cls._field_definitions.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields and k in fields_to_update}
        try:
            model_instance = cls._pydantic_partial_model.model_validate(filtered_data)
            return model_instance.model_dump(exclude_unset=True)
        except PydanticValidationError as e:
            raise ValidationError(f"Partial validation failed: {str(e)}") from e

class DocumentType(Generic[D]):
    """Defines a document type within a collection, preserving the specific Document subclass."""
    def __init__(self, document_class: Type[D], is_static: bool = False, static_id: str | None = None):
        if not (isinstance(document_class, type) and issubclass(document_class, Document)):
            raise TypeError(f"document_class must be a subclass of Document, but got {document_class}")
        self.document_class = document_class
        self.is_static = is_static
        self.static_id = static_id

    def create_static_instance(self, collection_path: str, **kwargs: str) -> D:
        """Creates an instance of a static document, returning the specific subclass `D`."""
        if not self.is_static:
            raise TypeError("This method can only be called on a static DocumentType.")
        instance = self.document_class(**kwargs)
        instance._path = f"{collection_path}/{self.static_id}"
        return instance

    def create_instance(self, collection_path: str, doc_id: str, **kwargs: str) -> D:
        """Creates an instance of a dynamic document, returning the specific subclass `D`."""
        if self.is_static:
            raise TypeError("Use create_static_instance() for static document types.")
        
        # Combine all parameters (parent + document)
        doc_id_key = self.document_class.get_doc_id_key()
        all_params = {**kwargs}
        if doc_id_key:
            all_params[doc_id_key] = doc_id
        
        # Create instance with all combined parameters
        instance = self.document_class(**all_params)

        # Explicitly set the combined path params on the instance, as the constructor
        # may have only validated and stored its own params.
        instance._path_params = all_params

        # Render the document's own path segment using its template
        doc_segment = self.document_class.path(**all_params)
        instance._path = f"{collection_path}/{doc_segment}"
        return instance

C = TypeVar("C", bound="Collection")

class SubcollectionType(Generic[C]):
    """Defines a subcollection type within a document, preserving the specific Collection subclass."""
    def __init__(self, collection_class: Type[C], is_static: bool = False, static_id: str | None = None):
        if not (isinstance(collection_class, type) and issubclass(collection_class, Collection)):
            raise TypeError(f"collection_class must be a subclass of Collection, but got {collection_class}")
        self.collection_class = collection_class
        self.is_static = is_static
        self.static_id = static_id
        if is_static and not static_id:
            raise ValueError("static_id must be provided for static subcollections.")

class Collection(FirestoreNode, Generic[T_Document]):
    """Represents a collection in Firestore with support for multiple document types."""
    class PathParams: ...
    class DocumentTypes: ...
    class DocumentNames: ...
    
    _document_types: Dict[str, DocumentType] = {}
    _document_class: Optional[Type[Document]] = None
    _default_document_class: Optional[Type[Document]] = None

    @property
    def model(self) -> Optional[Type[T_Document]]:
        """Returns the Pydantic model for the collection's documents."""
        # If there are defined document types, return the model of the first one.
        if self._document_types:
            first_doc_type = next(iter(self._document_types.values()))
            return cast(Type[T_Document], first_doc_type.document_class._pydantic_model)
        # Fallback for older-style single document class definitions.
        if self._default_document_class:
            return cast(Type[T_Document], self._default_document_class._pydantic_model)
        return None

    def __init__(self, base_path: str, **kwargs: str):
        # First, initialize with the collection's own specific path parameters.
        # The `path` method validates and uses only the params defined in the collection's PathParams.
        collection_segment = self.path(**kwargs)

        # Now, call the parent constructor with ALL kwargs (including parent's)
        # to ensure they are all stored in _path_params for later use.
        super().__init__(**kwargs)

        # The full path is the parent's path joined with the collection's segment
        self._path = f"{base_path}/{collection_segment}"

    ...

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._document_types = {}

        if hasattr(cls, 'DocumentTypes'):
            for name, doc_type_or_class in vars(cls.DocumentTypes).items():
                if name.startswith('_'):
                    continue

                doc_type = None
                if isinstance(doc_type_or_class, DocumentType):
                    doc_type = doc_type_or_class
                elif isinstance(doc_type_or_class, type) and issubclass(doc_type_or_class, Document):
                    doc_type = DocumentType(doc_type_or_class, is_static=False)
                
                if doc_type:
                    upper_name = name.upper()
                    cls._document_types[name.lower()] = doc_type

                    if doc_type.is_static:
                        # --- Static Document Accessor ---
                        class StaticDocAccessor(Generic[D]):
                            def __init__(self, doc_type: DocumentType[D]):
                                self.doc_type = doc_type
                            
                            def __get__(self, instance: Optional[Collection], owner: Type[Collection]) -> D:
                                path_params = instance._path_params if instance else {}
                                base_path = instance.instance_path if instance else owner.path(**path_params)
                                return self.doc_type.create_static_instance(base_path, **path_params)

                        setattr(cls, upper_name, StaticDocAccessor(doc_type))
                    else:
                        # --- Dynamic Document Builder (Descriptor) ---
                        class DynamicDocBuilder(Generic[D]):
                            def __init__(self, doc_type: DocumentType[D]):
                                self.doc_type = doc_type
                                # Set annotations on the builder instance itself for inspection
                                self.__annotations__ = {'return': self.doc_type.document_class}

                            def __call__(self, self_or_cls, doc_id: str, **kwargs: str) -> D:
                                """This method is called when the descriptor is called like a function."""
                                if isinstance(self_or_cls, Collection):
                                    # Called on an instance (e.g., course_doc.ENROLLMENTS.ENROLLMENT(...))
                                    base_path = self_or_cls.instance_path
                                    parent_kwargs = self_or_cls._path_params
                                else:
                                    # Called on a class (e.g., TestCoursesCollection.COURSE(...))
                                    base_path = self_or_cls.path(**kwargs)
                                    parent_kwargs = kwargs
                                
                                # The key for the doc_id in the path template (e.g., 'course_id')
                                doc_id_key = self.doc_type.document_class.get_doc_id_key()
                                if doc_id_key:
                                    combined_kwargs = {**parent_kwargs, **kwargs, doc_id_key: doc_id}
                                else:
                                    combined_kwargs = {**parent_kwargs, **kwargs}

                                return self.doc_type.create_instance(base_path, doc_id, **combined_kwargs)

                            def __get__(self, instance: Optional[Collection], owner: Type[Collection]) -> Callable[..., D]:
                                """Returns a callable that is bound to the owner class or instance."""
                                # This makes CourseCollection.COURSE(doc_id='123') work by binding `self` of __call__
                                # to the correct class or instance.
                                bound_callable = lambda doc_id, **kwargs: self(owner if instance is None else instance, doc_id, **kwargs)
                                # Carry over annotations for type inspection if needed
                                bound_callable.__annotations__ = self.__annotations__
                                return bound_callable

                        setattr(cls, upper_name, DynamicDocBuilder(doc_type))

        # For backward compatibility
        if hasattr(cls, '_document_class') and cls._document_class:
            cls._default_document_class = cls._document_class
