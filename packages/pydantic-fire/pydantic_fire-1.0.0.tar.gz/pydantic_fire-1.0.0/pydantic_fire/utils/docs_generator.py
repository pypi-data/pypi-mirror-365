"""
Auto-documentation generator for Firestore schema.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Type, TYPE_CHECKING
from datetime import datetime
import json

if TYPE_CHECKING:
    from ..schema_manager import _FirestoreSchemaManager
    FirestoreSchema = _FirestoreSchemaManager

from ..core.base import Document, Collection
from ..schema_manager import FirestoreSchema as _FirestoreSchema
from ..utils.introspection import SchemaIntrospector
from ..core.exceptions import SchemaError


class DocsGenerator:
    """
    Generate comprehensive documentation for Firestore schema.
    """
    
    def __init__(self, schema: Optional['_FirestoreSchemaManager'] = None):
        """
        Initialize the documentation generator.
        
        Args:
            schema: FirestoreSchema instance (defaults to global instance)
        """
        self.schema: '_FirestoreSchemaManager' = schema or _FirestoreSchema
        self.introspector = SchemaIntrospector(schema)
    
    def generate_markdown_docs(self, 
                              title: str = "Firestore Schema Documentation",
                              include_toc: bool = True,
                              include_examples: bool = True) -> str:
        """
        Generate comprehensive Markdown documentation.
        
        Args:
            title: Document title
            include_toc: Whether to include table of contents
            include_examples: Whether to include usage examples
        
        Returns:
            Markdown documentation as string
        """
        analysis = self.introspector.analyze_schema()
        issues = self.introspector.find_potential_issues()
        
        md_lines = [
            f"# {title}",
            "",
            f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
        ]
        
        if include_toc:
            md_lines.extend(self._generate_table_of_contents(analysis))
        
        # Overview section
        md_lines.extend(self._generate_overview_markdown(analysis))
        
        # Collections section
        md_lines.extend(self._generate_collections_markdown(analysis, include_examples))
        
        # Statistics section
        md_lines.extend(self._generate_statistics_markdown(analysis))
        
        # Issues section
        if issues:
            md_lines.extend(self._generate_issues_markdown(issues))
        
        return "\n".join(md_lines)
    
    def generate_api_reference(self, format: str = 'markdown') -> str:
        """
        Generate API reference documentation.
        
        Args:
            format: Output format ('markdown' or 'json')
        
        Returns:
            API reference documentation
        """
        analysis = self.introspector.analyze_schema()
        
        if format.lower() == 'markdown':
            return self._generate_api_reference_markdown(analysis)
        elif format.lower() == 'json':
            return json.dumps(analysis, indent=2, ensure_ascii=False)
        else:
            raise SchemaError(f"Unsupported API reference format: {format}")
    
    def generate_field_reference(self) -> str:
        """
        Generate field reference documentation.
        
        Returns:
            Field reference as Markdown
        """
        analysis = self.introspector.analyze_schema()
        
        md_lines = [
            "# Field Reference",
            "",
            "Complete reference of all fields across collections.",
            "",
        ]
        
        # Group fields by type
        fields_by_type = {}
        for collection_name, collection_data in analysis['collections'].items():
            if 'fields' not in collection_data:
                continue
            
            for field_name, field_data in collection_data['fields'].items():
                field_type = field_data.get('type', 'unknown')
                if field_type not in fields_by_type:
                    fields_by_type[field_type] = []
                
                fields_by_type[field_type].append({
                    'collection': collection_name,
                    'name': field_name,
                    'data': field_data
                })
        
        # Generate documentation for each type
        for field_type, fields in sorted(fields_by_type.items()):
            md_lines.extend([
                f"## {field_type} Fields",
                "",
            ])
            
            for field_info in fields:
                field_data = field_info['data']
                md_lines.extend([
                    f"### {field_info['collection']}.{field_info['name']}",
                    "",
                    f"**Type:** `{field_type}`",
                    f"**Required:** {'Yes' if field_data.get('required') else 'No'}",
                    f"**Read-only:** {'Yes' if field_data.get('read_only') else 'No'}",
                    f"**Permissions:** {', '.join(field_data.get('permissions', []))}",
                ])
                
                if field_data.get('metadata', {}).get('description'):
                    md_lines.extend([
                        "",
                        f"**Description:** {field_data['metadata']['description']}",
                    ])
                
                if field_data.get('firestore_alias'):
                    md_lines.extend([
                        "",
                        f"**Firestore Alias:** `{field_data['firestore_alias']}`",
                    ])
                
                ui_hints = field_data.get('ui_hints', {})
                if ui_hints:
                    md_lines.extend([
                        "",
                        "**UI Hints:**",
                    ])
                    for hint_key, hint_value in ui_hints.items():
                        md_lines.append(f"- {hint_key}: {hint_value}")
                
                md_lines.append("")
        
        return "\n".join(md_lines)
    
    def generate_permissions_guide(self) -> str:
        """
        Generate permissions guide documentation.
        
        Returns:
            Permissions guide as Markdown
        """
        analysis = self.introspector.analyze_schema()
        
        md_lines = [
            "# Permissions Guide",
            "",
            "Guide to understanding and using field-level permissions.",
            "",
            "## Permission Types",
            "",
            "- **read**: Field can be read by users with this permission",
            "- **write**: Field can be written/updated by users with this permission",
            "- **admin**: Field requires admin privileges",
            "- **create**: Field can be set during document creation",
            "- **update**: Field can be modified in existing documents",
            "- **delete**: Field affects document deletion permissions",
            "",
            "## Collections by Permission",
            "",
        ]
        
        # Group collections by permissions used
        permissions_summary = analysis.get('permissions_summary', {})
        
        for permission, count in sorted(permissions_summary.items()):
            md_lines.extend([
                f"### {permission.title()} Permission",
                "",
                f"Used in {count} collection(s).",
                "",
                "**Collections:**",
                "",
            ])
            
            for collection_name, collection_data in analysis['collections'].items():
                if permission in collection_data.get('permissions_used', []):
                    fields_with_permission = []
                    for field_name, field_data in collection_data.get('fields', {}).items():
                        if permission in field_data.get('permissions', []):
                            fields_with_permission.append(field_name)
                    
                    if fields_with_permission:
                        md_lines.extend([
                            f"- **{collection_name}**: {', '.join(fields_with_permission)}",
                        ])
            
            md_lines.append("")
        
        return "\n".join(md_lines)
    
    def _generate_table_of_contents(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate table of contents."""
        return [
            "## Table of Contents",
            "",
            "1. [Overview](#overview)",
            "2. [Collections](#collections)",
        ] + [
            f"   - [{name}](#{name.lower().replace(' ', '-')})"
            for name in analysis['collections'].keys()
        ] + [
            "3. [Statistics](#statistics)",
            "4. [Issues](#issues)",
            "",
        ]
    
    def _generate_overview_markdown(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate overview section in Markdown."""
        stats = analysis.get('statistics', {})
        
        return [
            "## Overview",
            "",
            f"This schema contains {stats.get('total_collections', 0)} collections with a total of {stats.get('total_fields', 0)} fields.",
            f"On average, each collection has {stats.get('avg_fields_per_collection', 0)} fields.",
            "",
            "### Quick Stats",
            "",
            f"- **Collections:** {stats.get('total_collections', 0)}",
            f"- **Total Fields:** {stats.get('total_fields', 0)}",
            f"- **Subcollections:** {stats.get('total_subcollections', 0)}",
            "",
        ]
    
    def _generate_collections_markdown(self, analysis: Dict[str, Any], include_examples: bool) -> List[str]:
        """Generate collections section in Markdown."""
        lines = [
            "## Collections",
            "",
        ]
        
        for collection_name, collection_data in analysis['collections'].items():
            lines.extend([
                f"### {collection_name}",
                "",
                f"**Document Class:** `{collection_data.get('document_class', 'Unknown')}`",
                f"**Path Template:** `{collection_data.get('path_template', 'Unknown')}`",
                f"**Field Count:** {collection_data.get('field_count', 0)}",
                "",
            ])
            
            # Required fields
            required_fields = collection_data.get('required_fields', [])
            if required_fields:
                lines.extend([
                    "**Required Fields:** " + ", ".join(f"`{field}`" for field in required_fields),
                    "",
                ])
            
            # Optional fields
            optional_fields = collection_data.get('optional_fields', [])
            if optional_fields:
                lines.extend([
                    "**Optional Fields:** " + ", ".join(f"`{field}`" for field in optional_fields),
                    "",
                ])
            
            # Read-only fields
            readonly_fields = collection_data.get('read_only_fields', [])
            if readonly_fields:
                lines.extend([
                    "**Read-only Fields:** " + ", ".join(f"`{field}`" for field in readonly_fields),
                    "",
                ])
            
            # Field details
            if 'fields' in collection_data:
                lines.extend([
                    "#### Fields",
                    "",
                    "| Field | Type | Required | Permissions | Description |",
                    "|-------|------|----------|-------------|-------------|",
                ])
                
                for field_name, field_data in collection_data['fields'].items():
                    field_type = field_data.get('type', 'unknown')
                    required = "✓" if field_data.get('required') else "✗"
                    permissions = ", ".join(field_data.get('permissions', []))
                    description = field_data.get('metadata', {}).get('description', '')
                    
                    lines.append(f"| `{field_name}` | `{field_type}` | {required} | {permissions} | {description} |")
                
                lines.append("")
            
            # Usage examples
            if include_examples:
                lines.extend(self._generate_usage_examples(collection_name, collection_data))
            
            # Subcollections
            if 'subcollections' in collection_data and collection_data['subcollections']:
                lines.extend([
                    "#### Subcollections",
                    "",
                ])
                for subcoll_name in collection_data['subcollections'].keys():
                    lines.append(f"- `{subcoll_name}`")
                lines.append("")
        
        return lines
    
    def _generate_usage_examples(self, collection_name: str, collection_data: Dict[str, Any]) -> List[str]:
        """Generate usage examples for a collection."""
        lines = [
            "#### Usage Examples",
            "",
            "**Creating a document:**",
            "",
            "```python",
            f"# Define the document",
            f"data = {{",
        ]
        
        # Generate example data
        if 'fields' in collection_data:
            for field_name, field_data in collection_data['fields'].items():
                if field_data.get('required') and not field_data.get('read_only'):
                    field_type = field_data.get('type', 'str')
                    example_value = self._get_example_value(field_type)
                    lines.append(f"    '{field_name}': {example_value},")
        
        lines.extend([
            "}",
            "",
            f"# Validate and serialize",
            f"validated_data = {collection_data.get('document_class', 'Document')}.serialize(data)",
            "```",
            "",
            "**Reading and parsing:**",
            "",
            "```python",
            f"# Parse data from Firestore",
            f"document = {collection_data.get('document_class', 'Document')}.parse(firestore_data)",
            "```",
            "",
        ])
        
        return lines
    
    def _get_example_value(self, field_type: str) -> str:
        """Get example value for a field type."""
        examples = {
            'str': "'example_value'",
            'int': "42",
            'float': "3.14",
            'bool': "True",
            'list': "[]",
            'dict': "{}",
            'datetime': "datetime.now()"
        }
        return examples.get(field_type, "'example_value'")
    
    def _generate_statistics_markdown(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate statistics section in Markdown."""
        stats = analysis.get('statistics', {})
        field_types = analysis.get('field_types_summary', {})
        permissions = analysis.get('permissions_summary', {})
        
        lines = [
            "## Statistics",
            "",
            "### Field Types Distribution",
            "",
        ]
        
        if field_types:
            for field_type, count in sorted(field_types.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- **{field_type}**: {count} fields")
            lines.append("")
        
        lines.extend([
            "### Permissions Usage",
            "",
        ])
        
        if permissions:
            for permission, count in sorted(permissions.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- **{permission}**: {count} collections")
            lines.append("")
        
        return lines
    
    def _generate_issues_markdown(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate issues section in Markdown."""
        lines = [
            "## Issues",
            "",
            f"Found {len(issues)} potential issue(s) in the schema:",
            "",
        ]
        
        # Group issues by severity
        issues_by_severity = {}
        for issue in issues:
            severity = issue.get('severity', 'info')
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        for severity in ['error', 'warning', 'info']:
            if severity in issues_by_severity:
                lines.extend([
                    f"### {severity.title()} Issues",
                    "",
                ])
                
                for issue in issues_by_severity[severity]:
                    lines.extend([
                        f"**{issue.get('type', 'Unknown')}**",
                        f"- Collection: `{issue.get('collection', 'Unknown')}`",
                    ])
                    
                    if 'field' in issue:
                        lines.append(f"- Field: `{issue['field']}`")
                    
                    lines.extend([
                        f"- Message: {issue.get('message', 'No message')}",
                        "",
                    ])
        
        return lines
    
    def _generate_api_reference_markdown(self, analysis: Dict[str, Any]) -> str:
        """Generate API reference in Markdown format."""
        md_lines = [
            "# API Reference",
            "",
            "Complete API reference for all collections and their methods.",
            "",
        ]
        
        for collection_name, collection_data in analysis['collections'].items():
            doc_class = collection_data.get('document_class', 'Unknown')
            
            md_lines.extend([
                f"## {doc_class}",
                "",
                f"Document class for the `{collection_name}` collection.",
                "",
                "### Methods",
                "",
                "#### `parse(data: Dict[str, Any]) -> BaseModel`",
                "",
                "Parse and validate raw data from Firestore.",
                "",
                "**Parameters:**",
                "- `data`: Raw data dictionary from Firestore",
                "",
                "**Returns:** Validated Pydantic model instance",
                "",
                "#### `serialize(data: Dict[str, Any]) -> Dict[str, Any]`",
                "",
                "Validate and serialize data for Firestore storage.",
                "",
                "**Parameters:**",
                "- `data`: Data dictionary to validate and serialize",
                "",
                "**Returns:** Firestore-compatible data dictionary",
                "",
                "#### `validate_partial(data: Dict[str, Any], fields_to_update: List[str] = None, user_permissions: List[str] = None) -> Dict[str, Any]`",
                "",
                "Validate partial update data.",
                "",
                "**Parameters:**",
                "- `data`: Partial data to validate",
                "- `fields_to_update`: Specific fields to update",
                "- `user_permissions`: User permissions for validation",
                "",
                "**Returns:** Validated partial data",
                "",
            ])
        
        return "\n".join(md_lines)
    
    def save_docs_to_file(self, 
                         output_path: str,
                         format: str = 'markdown',
                         **kwargs) -> None:
        """
        Generate and save documentation to file.
        
        Args:
            output_path: Path to save the documentation
            format: Documentation format ('markdown', 'api', 'fields', 'permissions')
            **kwargs: Additional arguments for documentation generation
        """
        if format.lower() == 'markdown':
            content = self.generate_markdown_docs(**kwargs)
        elif format.lower() == 'api':
            content = self.generate_api_reference('markdown')
        elif format.lower() == 'fields':
            content = self.generate_field_reference()
        elif format.lower() == 'permissions':
            content = self.generate_permissions_guide()
        else:
            raise SchemaError(f"Unsupported documentation format: {format}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def create_docs_generator(schema: Optional['_FirestoreSchemaManager'] = None) -> DocsGenerator:
    """
    Create a documentation generator.
    
    Args:
        schema: FirestoreSchema instance (defaults to global instance)
    
    Returns:
        DocsGenerator instance
    """
    return DocsGenerator(schema)
