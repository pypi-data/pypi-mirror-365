"""
Schema visualization tools for generating diagrams and visual representations.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Type, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..schema_manager import _FirestoreSchemaManager
    FirestoreSchema = _FirestoreSchemaManager

from ..core.base import Document, Collection
from ..schema_manager import FirestoreSchema as _FirestoreSchema
from ..utils.introspection import SchemaIntrospector
from ..core.exceptions import SchemaError


class SchemaVisualizer:
    """
    Generate visual representations of Firestore schema structure.
    """
    
    def __init__(self, schema: Optional['_FirestoreSchemaManager'] = None):
        """
        Initialize the schema visualizer.
        
        Args:
            schema: FirestoreSchema instance (defaults to global instance)
        """
        self.schema: '_FirestoreSchemaManager' = schema or _FirestoreSchema
        self.introspector = SchemaIntrospector(schema)
    
    def generate_mermaid_diagram(self, 
                                include_fields: bool = True,
                                include_permissions: bool = False,
                                max_depth: int = 3) -> str:
        """
        Generate a Mermaid diagram of the schema structure.
        
        Args:
            include_fields: Whether to include field details
            include_permissions: Whether to include permission information
            max_depth: Maximum depth for subcollections
        
        Returns:
            Mermaid diagram as string
        """
        analysis = self.introspector.analyze_schema()
        
        mermaid_lines = [
            "graph TD",
            "    %% Firestore Schema Diagram",
            f"    %% Generated on: {datetime.now().isoformat()}",
            ""
        ]
        
        # Generate nodes and relationships
        for collection_name, collection_data in analysis['collections'].items():
            self._add_collection_to_mermaid(
                mermaid_lines, 
                collection_name, 
                collection_data,
                include_fields,
                include_permissions,
                max_depth,
                0
            )
        
        # Add styling
        mermaid_lines.extend([
            "",
            "    %% Styling",
            "    classDef collection fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
            "    classDef document fill:#f3e5f5,stroke:#4a148c,stroke-width:2px",
            "    classDef field fill:#e8f5e8,stroke:#2e7d32,stroke-width:1px",
            "    classDef readonly fill:#ffebee,stroke:#c62828,stroke-width:1px",
            ""
        ])
        
        return "\n".join(mermaid_lines)
    
    def generate_plantuml_diagram(self, 
                                 include_fields: bool = True,
                                 include_permissions: bool = False) -> str:
        """
        Generate a PlantUML diagram of the schema structure.
        
        Args:
            include_fields: Whether to include field details
            include_permissions: Whether to include permission information
        
        Returns:
            PlantUML diagram as string
        """
        analysis = self.introspector.analyze_schema()
        
        plantuml_lines = [
            "@startuml",
            "!theme plain",
            "title Firestore Schema Structure",
            f"note top : Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Generate classes for each collection
        for collection_name, collection_data in analysis['collections'].items():
            self._add_collection_to_plantuml(
                plantuml_lines,
                collection_name,
                collection_data,
                include_fields,
                include_permissions
            )
        
        plantuml_lines.append("@enduml")
        
        return "\n".join(plantuml_lines)
    
    def generate_html_documentation(self, 
                                   title: str = "Firestore Schema Documentation",
                                   include_css: bool = True) -> str:
        """
        Generate interactive HTML documentation.
        
        Args:
            title: Document title
            include_css: Whether to include embedded CSS
        
        Returns:
            HTML documentation as string
        """
        analysis = self.introspector.analyze_schema()
        issues = self.introspector.find_potential_issues()
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{title}</title>",
        ]
        
        if include_css:
            html_parts.extend(self._get_embedded_css())
        
        html_parts.extend([
            "</head>",
            "<body>",
            f"    <header><h1>{title}</h1></header>",
            "    <nav>",
            "        <ul>",
            "            <li><a href='#overview'>Overview</a></li>",
            "            <li><a href='#collections'>Collections</a></li>",
            "            <li><a href='#statistics'>Statistics</a></li>",
            "            <li><a href='#issues'>Issues</a></li>",
            "        </ul>",
            "    </nav>",
            "    <main>",
        ])
        
        # Overview section
        html_parts.extend(self._generate_overview_section(analysis))
        
        # Collections section
        html_parts.extend(self._generate_collections_section(analysis))
        
        # Statistics section
        html_parts.extend(self._generate_statistics_section(analysis))
        
        # Issues section
        html_parts.extend(self._generate_issues_section(issues))
        
        html_parts.extend([
            "    </main>",
            "    <footer>",
            f"        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            "    </footer>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _add_collection_to_mermaid(self,
                                  lines: List[str],
                                  collection_name: str,
                                  collection_data: Dict[str, Any],
                                  include_fields: bool,
                                  include_permissions: bool,
                                  max_depth: int,
                                  current_depth: int) -> None:
        """Add collection to Mermaid diagram."""
        if current_depth >= max_depth:
            return
        
        # Collection node
        collection_id = f"C_{collection_name}"
        lines.append(f"    {collection_id}[\"{collection_name}<br/>Collection\"]")
        lines.append(f"    class {collection_id} collection")
        
        # Document node
        if 'document_class' in collection_data:
            doc_id = f"D_{collection_name}"
            doc_name = collection_data['document_class']
            lines.append(f"    {doc_id}[\"{doc_name}<br/>Document\"]")
            lines.append(f"    class {doc_id} document")
            lines.append(f"    {collection_id} --> {doc_id}")
            
            # Fields
            if include_fields and 'fields' in collection_data:
                for field_name, field_data in collection_data['fields'].items():
                    field_id = f"F_{collection_name}_{field_name}"
                    field_type = field_data.get('type', 'unknown')
                    field_label = f"{field_name}<br/>{field_type}"
                    
                    if field_data.get('required'):
                        field_label += "<br/>*required*"
                    
                    if field_data.get('read_only'):
                        field_label += "<br/>*read-only*"
                        lines.append(f"    {field_id}[\"{field_label}\"]")
                        lines.append(f"    class {field_id} readonly")
                    else:
                        lines.append(f"    {field_id}[\"{field_label}\"]")
                        lines.append(f"    class {field_id} field")
                    
                    lines.append(f"    {doc_id} --> {field_id}")
            
            # Subcollections
            if 'subcollections' in collection_data:
                for subcoll_name, subcoll_data in collection_data['subcollections'].items():
                    self._add_collection_to_mermaid(
                        lines,
                        f"{collection_name}_{subcoll_name}",
                        subcoll_data,
                        include_fields,
                        include_permissions,
                        max_depth,
                        current_depth + 1
                    )
                    
                    # Connect parent document to subcollection
                    subcoll_id = f"C_{collection_name}_{subcoll_name}"
                    lines.append(f"    {doc_id} --> {subcoll_id}")
    
    def _add_collection_to_plantuml(self,
                                   lines: List[str],
                                   collection_name: str,
                                   collection_data: Dict[str, Any],
                                   include_fields: bool,
                                   include_permissions: bool) -> None:
        """Add collection to PlantUML diagram."""
        if 'document_class' not in collection_data:
            return
        
        doc_name = collection_data['document_class']
        lines.append(f"class {doc_name} {{")
        
        if include_fields and 'fields' in collection_data:
            for field_name, field_data in collection_data['fields'].items():
                field_type = field_data.get('type', 'unknown')
                field_line = f"  {field_name}: {field_type}"
                
                if field_data.get('required'):
                    field_line += " *"
                
                if field_data.get('read_only'):
                    field_line += " {readonly}"
                
                lines.append(field_line)
        
        lines.append("}")
        lines.append("")
        
        # Add relationships for subcollections
        if 'subcollections' in collection_data:
            for subcoll_name, subcoll_data in collection_data['subcollections'].items():
                if 'document_class' in subcoll_data:
                    subcoll_doc = subcoll_data['document_class']
                    lines.append(f"{doc_name} ||--o{{ {subcoll_doc} : {subcoll_name}")
    
    def _get_embedded_css(self) -> List[str]:
        """Get embedded CSS for HTML documentation."""
        return [
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }",
            "        header { background: #1976d2; color: white; padding: 1rem; }",
            "        nav { background: #f5f5f5; padding: 1rem; }",
            "        nav ul { list-style: none; margin: 0; padding: 0; }",
            "        nav li { display: inline; margin-right: 1rem; }",
            "        nav a { text-decoration: none; color: #1976d2; }",
            "        main { padding: 2rem; }",
            "        .collection { border: 1px solid #ddd; margin: 1rem 0; padding: 1rem; }",
            "        .field { background: #f9f9f9; margin: 0.5rem 0; padding: 0.5rem; }",
            "        .required { color: #d32f2f; font-weight: bold; }",
            "        .readonly { color: #ff9800; }",
            "        .deprecated { color: #757575; text-decoration: line-through; }",
            "        .issue-error { color: #d32f2f; }",
            "        .issue-warning { color: #ff9800; }",
            "        table { width: 100%; border-collapse: collapse; }",
            "        th, td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; }",
            "        th { background: #f5f5f5; }",
            "        footer { background: #f5f5f5; padding: 1rem; text-align: center; }",
            "    </style>"
        ]
    
    def _generate_overview_section(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate overview section for HTML documentation."""
        stats = analysis.get('statistics', {})
        
        return [
            "        <section id='overview'>",
            "            <h2>Schema Overview</h2>",
            f"            <p>Total Collections: {stats.get('total_collections', 0)}</p>",
            f"            <p>Total Fields: {stats.get('total_fields', 0)}</p>",
            f"            <p>Average Fields per Collection: {stats.get('avg_fields_per_collection', 0)}</p>",
            f"            <p>Analysis Date: {analysis['metadata'].get('analyzed_at', 'Unknown')}</p>",
            "        </section>",
        ]
    
    def _generate_collections_section(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate collections section for HTML documentation."""
        lines = [
            "        <section id='collections'>",
            "            <h2>Collections</h2>",
        ]
        
        for collection_name, collection_data in analysis['collections'].items():
            lines.extend([
                f"            <div class='collection'>",
                f"                <h3>{collection_name}</h3>",
                f"                <p>Document Class: {collection_data.get('document_class', 'Unknown')}</p>",
                f"                <p>Path Template: {collection_data.get('path_template', 'Unknown')}</p>",
                f"                <p>Field Count: {collection_data.get('field_count', 0)}</p>",
            ])
            
            if 'fields' in collection_data:
                lines.append("                <h4>Fields</h4>")
                for field_name, field_data in collection_data['fields'].items():
                    css_classes = ['field']
                    if field_data.get('required'):
                        css_classes.append('required')
                    if field_data.get('read_only'):
                        css_classes.append('readonly')
                    if field_data.get('deprecated'):
                        css_classes.append('deprecated')
                    
                    lines.extend([
                        f"                <div class='{' '.join(css_classes)}'>",
                        f"                    <strong>{field_name}</strong> ({field_data.get('type', 'unknown')})",
                        f"                    <br>Permissions: {', '.join(field_data.get('permissions', []))}",
                    ])
                    
                    if field_data.get('metadata', {}).get('description'):
                        lines.append(f"                    <br>Description: {field_data['metadata']['description']}")
                    
                    lines.append("                </div>")
            
            lines.append("            </div>")
        
        lines.append("        </section>")
        return lines
    
    def _generate_statistics_section(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate statistics section for HTML documentation."""
        return [
            "        <section id='statistics'>",
            "            <h2>Statistics</h2>",
            "            <p>Detailed statistics about the schema structure.</p>",
            "        </section>",
        ]
    
    def _generate_issues_section(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate issues section for HTML documentation."""
        lines = [
            "        <section id='issues'>",
            "            <h2>Potential Issues</h2>",
        ]
        
        if not issues:
            lines.append("            <p>No issues found in the schema.</p>")
        else:
            for issue in issues:
                severity_class = f"issue-{issue.get('severity', 'info')}"
                lines.extend([
                    f"            <div class='{severity_class}'>",
                    f"                <strong>{issue.get('type', 'Unknown')}</strong>: {issue.get('message', 'No message')}",
                    f"                <br>Collection: {issue.get('collection', 'Unknown')}",
                ])
                
                if 'field' in issue:
                    lines.append(f"                <br>Field: {issue['field']}")
                
                lines.append("            </div>")
        
        lines.append("        </section>")
        return lines
    
    def save_diagram_to_file(self, 
                           output_path: str,
                           format: str = 'mermaid',
                           **kwargs) -> None:
        """
        Generate and save diagram to file.
        
        Args:
            output_path: Path to save the diagram
            format: Diagram format ('mermaid', 'plantuml', 'html')
            **kwargs: Additional arguments for diagram generation
        """
        if format.lower() == 'mermaid':
            content = self.generate_mermaid_diagram(**kwargs)
        elif format.lower() == 'plantuml':
            content = self.generate_plantuml_diagram(**kwargs)
        elif format.lower() == 'html':
            content = self.generate_html_documentation(**kwargs)
        else:
            raise SchemaError(f"Unsupported diagram format: {format}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def create_schema_visualizer(schema: Optional['_FirestoreSchemaManager'] = None) -> 'SchemaVisualizer':
    """
    Create a schema visualizer.
    
    Args:
        schema: FirestoreSchema instance (defaults to global instance)
    
    Returns:
        SchemaVisualizer instance
    """
    return SchemaVisualizer(schema)
