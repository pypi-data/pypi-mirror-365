"""Parameter parsing and validation for Velithon framework.

This module provides functionality for parsing and validating HTTP request
parameters including query parameters, path parameters, and request bodies.
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping, Sequence
from typing import Annotated, Any, Optional, Union, get_args, get_origin

import orjson
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined
from pydash import get

from velithon.cache import parser_cache
from velithon.datastructures import FormData, Headers, QueryParams, UploadFile
from velithon.di import Provide
from velithon.exceptions import (
    BadRequestException,
    InvalidMediaTypeException,
    UnsupportParameterException,
    ValidationException,
)
from velithon.params.params import Body, Cookie, File, Form, Header, Path, Query
from velithon.requests import Request


def _convert_underscore_to_hyphen(name: str) -> str:
    """Convert underscore to hyphen for parameter name aliases."""
    return name.replace('_', '-')


def _is_auth_dependency(annotation: Any) -> bool:
    """Check if a parameter annotation represents an authentication dependency.

    Args:
        annotation: The parameter annotation to check

    Returns:
        True if this is an authentication dependency, False otherwise

    """
    if get_origin(annotation) is Annotated:
        _, *metadata = get_args(annotation)

        # Check for Provide dependency injection
        for meta in metadata:
            if isinstance(meta, Provide):
                return True
            elif callable(meta):
                func_name = getattr(meta, '__name__', '').lower()
                module_name = getattr(meta, '__module__', '')

                # Check for common authentication function patterns
                if (
                    any(
                        keyword in func_name
                        for keyword in [
                            'auth',
                            'user',
                            'token',
                            'jwt',
                            'login',
                            'current',
                        ]
                    )
                    or 'security' in module_name
                    or 'auth' in module_name
                ):
                    return True

    return False


# Performance optimization: Pre-compiled type converters
_TYPE_CONVERTERS = {
    int: int,
    float: float,
    str: str,
    bool: lambda v: str(v).lower() in ('true', '1', 'yes', 'on'),
    bytes: lambda v: v.encode() if isinstance(v, str) else v,
}


class ParameterResolver:
    """Parameter resolver for Velithon request handlers."""

    def __init__(self, request: Request):
        """Initialize the ParameterResolver with the request."""
        self.request = request
        self.data_cache = {}
        self.type_handlers = {
            int: self._parse_primitive,
            float: self._parse_primitive,
            str: self._parse_primitive,
            bool: self._parse_primitive,
            bytes: self._parse_primitive,
            list: self._parse_list,
            Request: self._parse_special,
            FormData: self._parse_special,
            Headers: self._parse_special,
            QueryParams: self._parse_special,
            UploadFile: self._parse_special,
            dict: self._parse_special,
        }
        self.param_types = {
            Query: 'query_params',
            Path: 'path_params',
            Body: 'json_body',
            Form: 'form_data',
            File: 'file_data',
            Header: 'headers',
            Cookie: 'cookies',
        }

    async def _fetch_data(self, param_type: str) -> Any:
        """Fetch and cache request data for the given parameter type."""
        if param_type not in self.data_cache:
            parsers = {
                'query_params': lambda: self.request.query_params,
                'path_params': lambda: self.request.path_params,
                'form_data': self._get_form_data,
                'json_body': self.request.json,
                'file_data': self.request.files,
                'headers': lambda: self.request.headers,
                'cookies': lambda: self.request.cookies,
            }
            parser = parsers.get(param_type)
            if not parser:
                raise BadRequestException(
                    details={'message': f'Invalid parameter type: {param_type}'}
                )

            result = parser()
            # Check if the result is a coroutine and await it if necessary
            self.data_cache[param_type] = (
                await result if inspect.iscoroutine(result) else result
            )
        return self.data_cache[param_type]

    def _get_param_value_with_alias(
        self, data: Any, param_name: str, param_metadata: Any = None
    ) -> Any:
        """Get parameter value from data, trying the actual parameter name.

        explicit alias, and auto-generated alias (underscore to hyphen).
        """
        # First try explicit alias if provided
        if param_metadata and hasattr(param_metadata, 'alias') and param_metadata.alias:
            value = data.get(param_metadata.alias)
            if value is not None:
                return value

        # Try the original parameter name
        value = data.get(param_name)
        if value is not None:
            return value

        # Auto-generate alias by converting underscores to hyphens
        if '_' in param_name:
            auto_alias = _convert_underscore_to_hyphen(param_name)
            value = data.get(auto_alias)
            if value is not None:
                return value

        return None

    async def _get_form_data(self):
        """Return form data from cached form."""
        form = await self.request._get_form()
        # Convert form data to a dictionary for Pydantic parsing
        return dict(form)

    def _get_type_key(self, annotation: Any) -> Any:
        """Determine the key for type dispatching, handling inheritance."""
        origin = get_origin(annotation)
        if origin in (list, Annotated, Union, Optional):
            if origin is Annotated:
                base_type = get_args(annotation)[0]
                return self._get_type_key(base_type)
            if origin in (Union, Optional) and any(
                t is type(None) for t in get_args(annotation)
            ):
                base_type = next(t for t in get_args(annotation) if t is not type(None))
                return self._get_type_key(base_type)
            return list
        # Handle Pydantic models by checking if annotation is a subclass of BaseModel
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return BaseModel
        return annotation if isinstance(annotation, type) else type(annotation)

    async def _parse_primitive(
        self,
        param_name: str,
        annotation: Any,
        data: Any,
        default: Any,
        is_required: bool,
        param_metadata: Any = None,
    ) -> Any:
        """Parse primitive types (int, float, str, bool, bytes) - OPTIMIZED."""
        value = self._get_param_value_with_alias(data, param_name, param_metadata)
        if value is None:
            if default is not None and default is not ...:
                return default
            if is_required:
                raise BadRequestException(
                    details={'message': f'Missing required parameter: {param_name}'}
                )

        try:
            # Use optimized type converters
            converter = _TYPE_CONVERTERS.get(annotation)
            if converter:
                return converter(value)

            # Fallback for bytes type
            if annotation is bytes:
                return value[0] if isinstance(value, tuple) else value
            return annotation(value)
        except (ValueError, TypeError) as e:
            raise ValidationException(
                details={
                    'field': param_name,
                    'msg': f'Invalid value for type {annotation}: {e!s}',
                }
            ) from e

    async def _parse_list(
        self,
        param_name: str,
        annotation: Any,
        data: Any,
        default: Any,
        is_required: bool,
        param_metadata: Any = None,
    ) -> Any:
        """Parse list types."""
        item_type = get_args(annotation)[0]
        values = self._get_param_value_with_alias(data, param_name, param_metadata)
        if values is None:
            values = []
        if not isinstance(values, Sequence):
            values = [values]
        if not values and default is not None and default is not ...:
            return default
        if not values and is_required:
            raise BadRequestException(
                details={'message': f'Missing required parameter: {param_name}'}
            )

        if item_type in (int, float, str, bool, bytes):
            list_type_map = {
                str: lambda vs: vs,
                int: lambda vs: [int(v) for v in vs],
                float: lambda vs: [float(v) for v in vs],
                bool: lambda vs: [v.lower() in ('true', '1', 'yes') for v in vs],
                bytes: lambda vs: [v[0] if isinstance(v, tuple) else v for v in vs],
            }
            try:
                return list_type_map[item_type](values)
            except (ValueError, TypeError) as e:
                raise ValidationException(
                    details={
                        'field': param_name,
                        'msg': f'Invalid list item type {item_type}: {e!s}',
                    }
                ) from e
        elif isinstance(item_type, type) and issubclass(item_type, BaseModel):
            try:
                return [item_type(**item) for item in values]
            except ValidationError as e:
                invalid_fields = orjson.loads(e.json())
                raise ValidationException(
                    details=[
                        {'field': get(item, 'loc')[0], 'msg': get(item, 'msg')}
                        for item in invalid_fields
                    ]
                ) from e
        elif item_type is UploadFile:
            # Handle list of UploadFile items
            if not all(isinstance(v, UploadFile) for v in values):
                raise BadRequestException(
                    details={
                        'message': f'Invalid file type for parameter: {param_name}'
                    }
                )
            return values
        raise BadRequestException(
            details={'message': f'Unsupported list item type: {item_type}'}
        )

    async def _parse_model(
        self,
        param_name: str,
        annotation: Any,
        data: Any,
        default: Any,
        is_required: bool,
    ) -> Any:
        """Parse Pydantic models."""
        if not data and default is not None and default is not ...:
            return default
        if not data and is_required:
            raise BadRequestException(
                details={'message': f'Missing required parameter: {param_name}'}
            )
        try:
            # Accept any Mapping type for Pydantic model
            if isinstance(data, Mapping):
                return annotation(**data)
            raise ValueError('Invalid data format for model: expected a mapping')
        except ValidationError as e:
            invalid_fields = orjson.loads(e.json())
            raise ValidationException(
                details=[
                    {'field': get(item, 'loc')[0], 'msg': get(item, 'msg')}
                    for item in invalid_fields
                ]
            ) from e

    async def _parse_special(
        self,
        param_name: str,
        annotation: Any,
        data: Any,
        default: Any,
        is_required: bool,
        param_metadata: Any = None,
    ) -> Any:
        """Parse special types (Request, FormData, Headers, etc.)."""
        type_map = {
            Request: lambda: self.request,
            FormData: lambda: self.request.form().__aenter__(),
            Headers: lambda: self.request.headers,
            QueryParams: lambda: self.request.query_params,
            dict: lambda: self.request.scope,
            UploadFile: lambda: self._get_file(
                param_name, data, default, is_required, param_metadata, annotation
            ),
        }
        handler = type_map.get(annotation)
        if handler:
            result = handler()
            return await result if inspect.iscoroutine(result) else result
        raise BadRequestException(
            details={'message': f'Unsupported special type: {annotation}'}
        )

    async def _get_file(
        self,
        param_name: str,
        data: Any,
        default: Any,
        is_required: bool,
        param_metadata: Any = None,
        annotation: Any = None,
    ) -> Any:
        """Handle file uploads."""
        # data is a dict[str, list[UploadFile]] from request.files()
        files = self._get_param_value_with_alias(data, param_name, param_metadata)
        if not files and default is not None and default is not ...:
            return default
        if not files and is_required:
            raise BadRequestException(
                details={'message': f'Missing required parameter: {param_name}'}
            )

        # files is a list of UploadFile objects
        if isinstance(files, list):
            if not all(isinstance(f, UploadFile) for f in files):
                raise BadRequestException(
                    details={
                        'message': f'Invalid file type for parameter: {param_name}'
                    }
                )

            # Check if the annotation expects a list
            if annotation and get_origin(annotation) is list:
                # Return the entire list for list[UploadFile] annotations
                return files
            else:
                # Return the first file for single UploadFile annotations
                return files[0] if files else None

        # If files is a single UploadFile, return it
        if isinstance(files, UploadFile):
            return files

        return None

    @parser_cache()
    def _resolve_param_metadata(
        self, param: inspect.Parameter
    ) -> tuple[Any, str, Any, bool, Any]:
        """Cache parameter metadata (annotation, param_type, default, is_required, param_metadata)."""  # noqa: E501
        annotation = param.annotation
        default = (
            param.default if param.default is not inspect.Parameter.empty else None
        )
        is_required = default is None and param.default is inspect.Parameter.empty
        param_type = 'query_params'  # Default
        param_metadata = None

        if get_origin(annotation) is Annotated:
            base_type, *metadata = get_args(annotation)

            # Check if this is an authentication dependency using centralized function
            if _is_auth_dependency(annotation):
                # Find the Provide dependency or callable in the metadata
                provider = None
                for meta in metadata:
                    if isinstance(meta, Provide):
                        provider = meta
                        break
                    elif callable(meta):
                        provider = meta
                        break

                if provider:
                    return base_type, 'provide', provider, is_required, None
                else:
                    # Fallback to dummy provider if no provider found
                    dummy_provider = Provide()
                    return base_type, 'provide', dummy_provider, is_required, None

            # Define parameter types tuple outside the generator expression
            param_types = (Query, Path, Body, Form, File, Header, Cookie, Provide)
            param_metadata = next(
                (m for m in metadata if isinstance(m, param_types)),
                None,
            )
            if not param_metadata:
                raise InvalidMediaTypeException(
                    details={
                        'message': f'Unsupported parameter metadata for '
                        f'{param.name}: {annotation}'
                    }
                )

            if hasattr(param_metadata, 'media_type'):
                content_type = self.request.headers.get('Content-Type', '')
                # Extract main media type (ignore parameters like boundary)
                main_media_type = content_type.split(';')[0].strip()
                expected_media_type = param_metadata.media_type.split(';')[0].strip()

                if main_media_type != expected_media_type:
                    raise InvalidMediaTypeException(
                        details={
                            'message': f'Invalid media type for parameter: {param.name}'
                        }
                    )

            if isinstance(param_metadata, Provide):
                return base_type, 'provide', param_metadata, is_required, param_metadata
            param_type = self.param_types.get(type(param_metadata), 'query_params')
            metadata_default = (
                param_metadata.default
                if hasattr(param_metadata, 'default')
                and param_metadata.default is not PydanticUndefined
                else None
            )
            default = metadata_default if metadata_default is not None else default
            annotation = base_type
            # If File() is used, ensure param_type remains file_data
            if isinstance(param_metadata, File):
                return annotation, 'file_data', default, is_required, param_metadata
            # If Form() is used, ensure param_type remains form_data even for BaseModel
            elif isinstance(param_metadata, Form):
                return annotation, 'form_data', default, is_required, param_metadata

        if annotation is inspect._empty:
            param_type = (
                'path_params'
                if param.name in self.request.path_params
                else 'query_params'
            )
        elif annotation is UploadFile:
            param_type = 'file_data'
        elif (
            get_origin(annotation) is list
            and len(get_args(annotation)) > 0
            and get_args(annotation)[0] is UploadFile
        ):
            param_type = 'file_data'
        elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
            param_type = (
                'json_body' if self.request.method.upper() != 'GET' else 'query_params'
            )
        elif (
            get_origin(annotation) is list
            and isinstance(get_args(annotation)[0], type)
            and issubclass(get_args(annotation)[0], BaseModel)
        ):
            param_type = (
                'json_body' if self.request.method.upper() != 'GET' else 'query_params'
            )
        elif param.name in self.request.path_params:
            param_type = 'path_params'

        return annotation, param_type, default, is_required, param_metadata

    async def resolve(self, signature: inspect.Signature) -> dict[str, Any]:
        """Resolve all parameters for the given function signature."""
        kwargs = {}
        for param in signature.parameters.values():
            (
                annotation,
                param_type,
                default,
                is_required,
                param_metadata,
            ) = self._resolve_param_metadata(param)
            name = param.name

            if param_type == 'provide':
                # If the default is a callable (authentication function), call it
                if callable(default):
                    # Check if the function expects the request
                    import inspect as func_inspect

                    func_sig = func_inspect.signature(default)
                    if len(func_sig.parameters) > 0:
                        # Pass the request to the authentication function
                        kwargs[name] = await default(self.request)
                    else:
                        # Call without arguments
                        kwargs[name] = await default()
                else:
                    kwargs[name] = default  # Provide dependency injection
                continue

            type_key = self._get_type_key(annotation)
            # Special handling for BaseModel subclasses
            handler = self.type_handlers.get(type_key)
            if (
                not handler
                and isinstance(annotation, type)
                and issubclass(annotation, BaseModel)
            ):
                handler = self._parse_model
            if not handler:
                if default is not None and default is not ...:
                    kwargs[name] = default
                    continue
                raise UnsupportParameterException(
                    details={
                        'message': f'Unsupported parameter type for {name}: '
                        f'{annotation}'
                    }
                )
            data = await self._fetch_data(param_type)
            # Pass param_metadata to handlers that support it
            if handler in (
                self._parse_primitive,
                self._parse_list,
                self._parse_special,
            ):
                kwargs[name] = await handler(
                    name, annotation, data, default, is_required, param_metadata
                )
            else:
                kwargs[name] = await handler(
                    name, annotation, data, default, is_required
                )

        return kwargs


class InputHandler:
    """Input handler for resolving parameters from a request."""

    def __init__(self, request: Request):
        """Initialize the InputHandler with the request."""
        self.resolver = ParameterResolver(request)

    async def get_input(self, signature: inspect.Signature) -> dict[str, Any]:
        """Resolve parameters from the request based on the function signature."""
        return await self.resolver.resolve(signature)
