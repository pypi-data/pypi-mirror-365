"""
Schema introspection tools for analyzing and understanding Firestore schema structure.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Type, Set, Tuple, TYPE_CHECKING
from datetime import datetime
import json

if TYPE_CHECKING:
    from ..schema_manager import _FirestoreSchemaManager
    FirestoreSchema = _FirestoreSchemaManager

from ..core.base import Document, Collection
from ..schema_manager import FirestoreSchema as _FirestoreSchema
from ..core.exceptions import SchemaError


class SchemaIntrospector:
    """
    Analyze and introspect Firestore schema structure.
    """
    
    def __init__(self, schema: Optional['_FirestoreSchemaManager'] = None):
        """
        Initialize the schema introspector.
        
        Args:
            schema: FirestoreSchema instance (defaults to global instance)
        """
        self.schema: '_FirestoreSchemaManager' = schema or _FirestoreSchema
    
    def analyze_schema(self) -> Dict[str, Any]:
        """
        Analyze complete schema structure.
        
        Returns:
            Complete schema analysis dictionary
        """
        analysis = {
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'total_collections': len(self.schema._registry),
                'schema_version': '1.0'
            },
            'collections': {},
            'statistics': {},
            'relationships': {},
            'field_types_summary': {}
        }
        
        # Analyze each collection
        for collection_name, collection_class in self.schema._registry.items():
            analysis['collections'][collection_name] = self.analyze_collection(collection_class)
        
        # Generate statistics
        analysis['statistics'] = self._generate_statistics(analysis['collections'])
        
        # Analyze relationships
        analysis['relationships'] = self._analyze_relationships(analysis['collections'])
        
        # Generate field types summary
        analysis['field_types_summary'] = self._analyze_field_types(analysis['collections'])
        
        return analysis
    
    def analyze_collection(self, collection_class: Type[Collection]) -> Dict[str, Any]:
        """
        Analyze a specific collection.
        
        Args:
            collection_class: Collection class to analyze
        
        Returns:
            Collection analysis dictionary
        """
        if not collection_class._document_class:
            return {
                'error': f"Collection {collection_class.__name__} has no document class defined"
            }
        
        document_class = collection_class._document_class
        
        analysis = {
            'collection_name': collection_class.__name__,
            'document_class': document_class.__name__,
            'path_template': collection_class.template(),
            'fields': {},
            'subcollections': {},
            'field_count': 0,
            'required_fields': [],
            'optional_fields': [],
            'read_only_fields': [],
            'deprecated_fields': [],
            'field_types_used': set()
        }
        
        # Analyze fields
        if hasattr(document_class, '_field_definitions'):
            for field_name, field_obj in document_class._field_definitions.items():
                field_analysis = self.analyze_field(field_name, field_obj)
                analysis['fields'][field_name] = field_analysis
                
                # Update summary lists
                if field_obj.required:
                    analysis['required_fields'].append(field_name)
                else:
                    analysis['optional_fields'].append(field_name)
                
                if field_obj.read_only:
                    analysis['read_only_fields'].append(field_name)
                
                if field_obj.kwargs.get('deprecated'):
                    analysis['deprecated_fields'].append(field_name)
                
                analysis['field_types_used'].add(field_obj.field_type.__name__)
            
            analysis['field_count'] = len(document_class._field_definitions)
        
        # Analyze subcollections
        if hasattr(document_class, '_subcollections'):
            for subcoll_name, subcoll_class in document_class._subcollections.items():
                analysis['subcollections'][subcoll_name] = self.analyze_collection(subcoll_class)
        
        # Convert sets to lists for JSON serialization
        analysis['field_types_used'] = list(analysis['field_types_used'])
        
        return analysis
    
    def analyze_field(self, field_name: str, field_obj: Any) -> Dict[str, Any]:
        """
        Analyze a specific field.
        
        Args:
            field_name: Name of the field
            field_obj: Field object to analyze
        
        Returns:
            Field analysis dictionary
        """
        analysis = {
            'name': field_name,
            'type': field_obj.field_type.__name__ if hasattr(field_obj.field_type, '__name__') else str(field_obj.field_type),
            'required': field_obj.required,
            'read_only': field_obj.read_only,
            'has_default': field_obj.default is not None or field_obj.default_factory is not None,
            'auto_now_add': field_obj.auto_now_add,
            'firestore_alias': field_obj.kwargs.get('alias'),
            'deprecated': field_obj.kwargs.get('deprecated'),
        }
        
        return analysis
    
    def get_collection_hierarchy(self) -> Dict[str, Any]:
        """
        Get the hierarchical structure of collections and subcollections.
        
        Returns:
            Hierarchical structure dictionary
        """
        hierarchy = {}
        
        for collection_name, collection_class in self.schema._registry.items():
            hierarchy[collection_name] = self._build_collection_hierarchy(collection_class)
        
        return hierarchy
    
    def _build_collection_hierarchy(self, collection_class: Type[Collection], depth: int = 0) -> Dict[str, Any]:
        """
        Build hierarchy for a specific collection.
        
        Args:
            collection_class: Collection class
            depth: Current depth in hierarchy
        
        Returns:
            Collection hierarchy dictionary
        """
        if depth > 10:  # Prevent infinite recursion
            return {'error': 'Maximum depth exceeded'}
        
        hierarchy = {
            'class_name': collection_class.__name__,
            'path_template': collection_class.template(),
            'document_class': collection_class._document_class.__name__ if collection_class._document_class else None,
            'subcollections': {},
            'depth': depth
        }
        
        if collection_class._document_class and hasattr(collection_class._document_class, '_subcollections'):
            for subcoll_name, subcoll_class in collection_class._document_class._subcollections.items():
                hierarchy['subcollections'][subcoll_name] = self._build_collection_hierarchy(
                    subcoll_class, depth + 1
                )
        
        return hierarchy
    
    def get_field_usage_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about field usage across the schema.
        
        Returns:
            Field usage statistics
        """
        stats = {
            'field_types': {},
            'total_fields': 0,
            'required_fields': 0,
            'optional_fields': 0,
            'read_only_fields': 0,
            'deprecated_fields': 0,
            'fields_with_aliases': 0
        }
        
        for collection_name, collection_class in self.schema._registry.items():
            if not collection_class._document_class:
                continue
            
            document_class = collection_class._document_class
            if not hasattr(document_class, '_field_definitions'):
                continue
            
            for field_name, field_obj in document_class._field_definitions.items():
                stats['total_fields'] += 1
                
                # Count field types
                field_type = field_obj.field_type.__name__
                stats['field_types'][field_type] = stats['field_types'].get(field_type, 0) + 1
                
                # Count field characteristics
                if field_obj.required:
                    stats['required_fields'] += 1
                else:
                    stats['optional_fields'] += 1
                
                if field_obj.read_only:
                    stats['read_only_fields'] += 1
                
                if field_obj.kwargs.get('deprecated'):
                    stats['deprecated_fields'] += 1
                
                if field_obj.kwargs.get('alias'):
                    stats['fields_with_aliases'] += 1
        
        return stats
    
    def find_potential_issues(self) -> List[Dict[str, Any]]:
        """
        Find potential issues in the schema definition.
        
        Returns:
            List of potential issues
        """
        issues = []
        
        for collection_name, collection_class in self.schema._registry.items():
            if not collection_class._document_class:
                issues.append({
                    'type': 'missing_document_class',
                    'severity': 'error',
                    'collection': collection_name,
                    'message': f"Collection {collection_name} has no document class defined"
                })
                continue
            
            document_class = collection_class._document_class
            
            # Check for deprecated fields that are still required
            if hasattr(document_class, '_field_definitions'):
                for field_name, field_obj in document_class._field_definitions.items():
                    if field_obj.kwargs.get('deprecated') and field_obj.required:
                        issues.append({
                            'type': 'deprecated_required_field',
                            'severity': 'error',
                            'collection': collection_name,
                            'field': field_name,
                            'message': f"Deprecated field {field_name} should not be required"
                        })
        
        return issues
    
    def _generate_statistics(self, collections: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall statistics from collections analysis."""
        stats = {
            'total_collections': len(collections),
            'total_documents': 0,
            'total_fields': 0,
            'total_subcollections': 0,
            'avg_fields_per_collection': 0
        }
        
        total_fields = 0
        for collection_data in collections.values():
            if 'field_count' in collection_data:
                total_fields += collection_data['field_count']
                stats['total_documents'] += 1
            
            if 'subcollections' in collection_data:
                stats['total_subcollections'] += len(collection_data['subcollections'])
        
        stats['total_fields'] = total_fields
        if stats['total_documents'] > 0:
            avg_fields = total_fields / stats['total_documents']
            stats['avg_fields_per_collection'] = int(round(avg_fields, 2))
        
        return stats
    
    def _analyze_relationships(self, collections: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationships between collections."""
        relationships = {
            'parent_child': {},
            'depth_levels': {}
        }
        
        for collection_name, collection_data in collections.items():
            if 'subcollections' in collection_data and collection_data['subcollections']:
                relationships['parent_child'][collection_name] = list(collection_data['subcollections'].keys())
        
        return relationships
    
    def _analyze_field_types(self, collections: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze field type usage across collections."""
        field_types_summary = {}
        
        for collection_data in collections.values():
            if 'field_types_used' in collection_data:
                for field_type in collection_data['field_types_used']:
                    field_types_summary[field_type] = field_types_summary.get(field_type, 0) + 1
        
        return field_types_summary
    
    def export_analysis(self, output_path: str, format: str = 'json') -> None:
        """
        Export schema analysis to file.
        
        Args:
            output_path: Path to save the analysis
            format: Export format ('json' or 'yaml')
        """
        analysis = self.analyze_schema()
        
        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
        else:
            raise SchemaError(f"Unsupported export format: {format}")


def create_schema_introspector(schema: Optional['_FirestoreSchemaManager'] = None) -> 'SchemaIntrospector':
    """
    Create a schema introspector.
    
    Args:
        schema: FirestoreSchema instance (defaults to global instance)
    
    Returns:
        SchemaIntrospector instance
    """
    return SchemaIntrospector(schema)
