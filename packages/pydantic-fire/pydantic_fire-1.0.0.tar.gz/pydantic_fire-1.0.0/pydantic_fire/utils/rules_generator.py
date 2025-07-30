"""
Firestore security rules generator from schema definitions.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Type, TYPE_CHECKING
from datetime import datetime
from pathlib import Path

if TYPE_CHECKING:
    from ..schema_manager import _FirestoreSchemaManager
    FirestoreSchema = _FirestoreSchemaManager

from ..core.base import Document, Collection
from ..schema_manager import FirestoreSchema as _FirestoreSchema
from ..core.exceptions import SchemaError


class FirestoreRulesGenerator:
    """
    Generate Firestore security rules from schema definitions.
    """
    
    def __init__(self, schema: Optional['_FirestoreSchemaManager'] = None):
        """
        Initialize the rules generator.
        
        Args:
            schema: FirestoreSchema instance (defaults to global instance)
        """
        self.schema: '_FirestoreSchemaManager' = schema or _FirestoreSchema
        self.templates_dir = Path(__file__).parent / "templates"
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load rule templates from templates directory."""
        self.templates = {}
        
        template_files = {
            'base': 'base_rules.template',
            'collection': 'collection_rules.template',
            'field_validation': 'field_validation.template'
        }
        
        for template_name, filename in template_files.items():
            template_path = self.templates_dir / filename
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    self.templates[template_name] = f.read()
            else:
                raise SchemaError(f"Template file not found: {template_path}")
    
    def generate_rules(self, 
                      user_auth_field: str = "request.auth.uid",
                      admin_role_field: str = "request.auth.token.admin",
                      schema_version: str = "1.0") -> str:
        """
        Generate complete Firestore security rules from schema definitions.
        
        Args:
            user_auth_field: Field to check for user authentication
            admin_role_field: Field to check for admin role
            schema_version: Version string for the schema
        
        Returns:
            Complete Firestore rules as string
        """
        collection_rules = []
        
        # Generate rules for each registered collection
        for collection_name, collection_class in self.schema._registry.items():
            rules = self.generate_collection_rules(
                collection_class,
                user_auth_field,
                admin_role_field
            )
            collection_rules.append(rules)
        
        # Combine all rules using base template
        return self._render_template('base', {
            'generation_timestamp': datetime.now().isoformat(),
            'schema_version': schema_version,
            'collection_rules': '\n\n'.join(collection_rules)
        })
    
    def generate_collection_rules(self,
                                collection_class: Type[Collection],
                                user_auth_field: str = "request.auth.uid",
                                admin_role_field: str = "request.auth.token.admin") -> str:
        """
        Generate rules for a specific collection.
        
        Args:
            collection_class: Collection class to generate rules for
            user_auth_field: Field to check for user authentication
            admin_role_field: Field to check for admin role
        
        Returns:
            Rules string for the collection
        """
        if not collection_class._document_class:
            raise SchemaError(f"Collection {collection_class.__name__} has no document class defined")
        
        document_class = collection_class._document_class
        collection_path = collection_class.template()
        
        # Generate field validations
        field_validations = self._generate_field_validations(document_class)
        
        # Generate permission conditions
        read_conditions = self._generate_read_conditions(document_class, user_auth_field, admin_role_field)
        write_conditions = self._generate_write_conditions(document_class, user_auth_field, admin_role_field)
        delete_conditions = self._generate_delete_conditions(document_class, user_auth_field, admin_role_field)
        
        # Generate subcollection rules
        subcollection_rules = self._generate_subcollection_rules(document_class, user_auth_field, admin_role_field)
        
        return self._render_template('collection', {
            'collection_name': collection_class.__name__,
            'document_class_name': document_class.__name__,
            'collection_path': collection_path,
            'read_conditions': read_conditions,
            'write_conditions': write_conditions,
            'delete_conditions': delete_conditions,
            'field_validations': field_validations,
            'subcollection_rules': subcollection_rules
        })
    
    def _generate_field_validations(self, document_class: Type[Document]) -> str:
        """
        Generate field validation rules.
        
        Args:
            document_class: Document class to generate validations for
        
        Returns:
            Field validation rules string
        """
        if not hasattr(document_class, '_field_definitions'):
            return ""
        
        validations = []
        
        for field_name, field_obj in document_class._field_definitions.items():
            # Skip fields that don't need validation
            if not field_obj.required and not field_obj.read_only:
                continue

            field_type = self._get_firestore_type(field_obj.field_type)

            validation = self._render_template('field_validation', {
                'field_name': field_name,
                'field_type': field_type,
                'required': field_obj.required,
                'read_only': field_obj.read_only,
            })
            
            validations.append(validation)
        
        return '\n'.join(validations) if validations else ""
    
    def _generate_read_conditions(self,
                                document_class: Type[Document],
                                user_auth_field: str,
                                admin_role_field: str) -> str:
        """
        Generate read permission conditions.
        
        Args:
            document_class: Document class
            user_auth_field: User authentication field
            admin_role_field: Admin role field
        
        Returns:
            Read conditions string
        """
        conditions = []
        
        # Default: authenticated users can read
        return f"({user_auth_field} != null)"
    
    def _generate_write_conditions(self,
                                 document_class: Type[Document],
                                 user_auth_field: str,
                                 admin_role_field: str) -> str:
        """
        Generate write permission conditions.
        
        Args:
            document_class: Document class
            user_auth_field: User authentication field
            admin_role_field: Admin role field
        
        Returns:
            Write conditions string
        """
        conditions = []
        
        # Default: authenticated users can write
        return f"({user_auth_field} != null)"
    
    def _generate_delete_conditions(self,
                                  document_class: Type[Document],
                                  user_auth_field: str,
                                  admin_role_field: str) -> str:
        """
        Generate delete permission conditions.
        
        Args:
            document_class: Document class
            user_auth_field: User authentication field
            admin_role_field: Admin role field
        
        Returns:
            Delete conditions string
        """
        # Default: only admins can delete
        return f"({admin_role_field} == true)"
    
    def _generate_subcollection_rules(self,
                                    document_class: Type[Document],
                                    user_auth_field: str,
                                    admin_role_field: str) -> str:
        """
        Generate rules for subcollections.
        
        Args:
            document_class: Document class
            user_auth_field: User authentication field
            admin_role_field: Admin role field
        
        Returns:
            Subcollection rules string
        """
        if not hasattr(document_class, '_subcollections'):
            return ""
        
        subcollection_rules = []
        
        for subcoll_name, subcoll_class in document_class._subcollections.items():
            if subcoll_class._document_class:
                rules = self.generate_collection_rules(
                    subcoll_class,
                    user_auth_field,
                    admin_role_field
                )
                subcollection_rules.append(rules)
        
        return '\n\n'.join(subcollection_rules)
    

    
    def _get_firestore_type(self, python_type: Any) -> str:
        """
        Convert Python type to Firestore type string.
        
        Args:
            python_type: Python type
        
        Returns:
            Firestore type string
        """
        type_mapping = {
            str: 'str',
            int: 'int',
            float: 'float',
            bool: 'bool',
            list: 'list',
            dict: 'dict',
        }
        
        # Handle datetime
        if hasattr(python_type, '__name__') and python_type.__name__ == 'datetime':
            return 'datetime'
        
        return type_mapping.get(python_type, 'str')
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with given context.
        
        Args:
            template_name: Name of template to render
            context: Template context variables
        
        Returns:
            Rendered template string
        """
        if template_name not in self.templates:
            raise SchemaError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        
        # Simple template rendering (replace {{ variable }} with values)
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            template = template.replace(placeholder, str(value))
        
        return template
    
    def save_rules_to_file(self, 
                          output_path: str,
                          user_auth_field: str = "request.auth.uid",
                          admin_role_field: str = "request.auth.token.admin",
                          schema_version: str = "1.0") -> None:
        """
        Generate and save rules to a file.
        
        Args:
            output_path: Path to save the rules file
            user_auth_field: Field to check for user authentication
            admin_role_field: Field to check for admin role
            schema_version: Version string for the schema
        """
        rules = self.generate_rules(user_auth_field, admin_role_field, schema_version)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rules)
    
    def validate_generated_rules(self, rules: str) -> List[str]:
        """
        Validate generated rules for common issues.
        
        Args:
            rules: Rules string to validate
        
        Returns:
            List of validation warnings/errors
        """
        issues = []
        
        # Check for basic syntax
        if not rules.strip().startswith('rules_version'):
            issues.append("Rules should start with 'rules_version'")
        
        if 'service cloud.firestore' not in rules:
            issues.append("Missing 'service cloud.firestore' declaration")
        
        # Check for balanced braces
        open_braces = rules.count('{')
        close_braces = rules.count('}')
        if open_braces != close_braces:
            issues.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
        
        # Check for common permission patterns
        if 'allow read' not in rules:
            issues.append("No read permissions found")
        
        if 'allow write' not in rules:
            issues.append("No write permissions found")
        
        return issues


def create_rules_generator(schema: Optional['_FirestoreSchemaManager'] = None) -> 'FirestoreRulesGenerator':
    """
    Create a Firestore rules generator.
    
    Args:
        schema: FirestoreSchema instance (defaults to global instance)
    
    Returns:
        FirestoreRulesGenerator instance
    """
    return FirestoreRulesGenerator(schema)
