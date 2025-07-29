"""
TODO YAML Generator

YAML variant of TODO JSON generator that creates .brass/todos.yaml
with structured data optimized for AI consumption while preserving all TODO intelligence.

Key Features:
- Structured YAML format for direct programmatic access
- Location-based consolidation to prevent duplicate entries
- Type-safe data (native integers, floats, booleans, arrays)  
- AI-optimized schema with consistent data access patterns
- Inherits data collection logic from existing TODO system

Follows the exact same proven pattern as PrivacyYamlGenerator.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class TodoYamlGenerator:
    """
    YAML variant of TODO generator for AI consumption.
    
    Creates structured YAML format optimized for programmatic access by AI agents.
    
    Follows evidence-based consolidation patterns from OutputGenerator
    to prevent duplicate entries and group similar issues by location.
    """
    
    def __init__(self, project_path: str, storage):
        """
        Initialize YAML TODO generator.
        
        Args:
            project_path: Root path of project to analyze
            storage: BrassStorage instance for data access
        """
        self.project_path = Path(project_path)
        self.storage = storage
        self.brass_dir = self.project_path / '.brass'
        self.yaml_output_path = self.brass_dir / 'todos.yaml'
        
        logger.info(f"YAML TODO generator initialized for project: {self.project_path}")
    
    def generate_yaml_report(self) -> str:
        """
        Generate structured YAML TODO report for AI consumption.
        
        Returns:
            Path to generated .brass/todos.yaml file
        """
        start_time = datetime.now()
        
        logger.info("Starting YAML TODO report generation")
        
        # Ensure .brass directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        # Phase 1: Get TODO data using existing logic from OutputGenerator
        logger.info("Phase 1: Collecting TODO data")
        todo_data = self._collect_todo_data()
        
        # Phase 2: Process and structure TODO data
        logger.info("Phase 2: Processing and structuring TODO data")
        structured_todos = self._structure_todo_data(todo_data)
        
        # Phase 3: Generate YAML structure
        logger.info("Phase 3: Generating YAML structure")
        yaml_data = self._build_yaml_structure(structured_todos, start_time)
        
        # Phase 4: Write YAML file
        logger.info("Phase 4: Writing YAML file")
        with open(self.yaml_output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"TODO YAML report generated successfully in {generation_time:.2f}s: {self.yaml_output_path}")
        
        return str(self.yaml_output_path)
    
    def _collect_todo_data(self) -> List[Dict[str, Any]]:
        """
        Collect TODO data using existing logic from OutputGenerator.
        
        Replicates the 24-hour window filtering and deduplication logic.
        
        Returns:
            List of processed TODO data
        """
        try:
            # Get TODO observations (mimicking OutputGenerator logic)
            all_todos = self.storage.get_observations_by_type('todo')
            
            # Apply 24-hour window filtering (from OutputGenerator.generate_todo_list)
            from datetime import timezone
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
            recent_todos = []
            
            for todo in all_todos:
                try:
                    created_at_str = todo['created_at']
                    # Handle both timezone-aware and naive datetime strings
                    if 'Z' in created_at_str or '+' in created_at_str:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    else:
                        # Make naive datetime timezone-aware (assume UTC)
                        created_at = datetime.fromisoformat(created_at_str).replace(tzinfo=timezone.utc)
                    
                    if created_at >= cutoff_time:
                        recent_todos.append(todo)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Failed to parse TODO created_at: {e}")
                    # Include TODO even if timestamp parsing fails
                    recent_todos.append(todo)
            
            # Deduplicate by file path, line number, and content (from OutputGenerator logic)
            seen_combinations = set()
            deduplicated_todos = []
            
            for todo in recent_todos:
                try:
                    data = todo.get('data', {})
                    if isinstance(data, str):
                        import json
                        data = json.loads(data)
                    
                    file_path = data.get('file_path', '')
                    line_number = data.get('line_number', 0)
                    content = data.get('content', '')
                    
                    # Create deduplication key
                    dedup_key = (file_path, line_number, content.strip())
                    
                    if dedup_key not in seen_combinations:
                        seen_combinations.add(dedup_key)
                        deduplicated_todos.append({
                            'id': todo.get('id'),
                            'content': content,
                            'file_path': file_path,
                            'line_number': line_number,
                            'priority': todo.get('priority', 0),
                            'category': data.get('category', 'general'),
                            'created_at': todo.get('created_at', ''),
                            'metadata': data.get('metadata', {})
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to process TODO data: {e}")
                    continue
            
            logger.info(f"Collected {len(deduplicated_todos)} TODOs from {len(all_todos)} total observations")
            return deduplicated_todos
            
        except Exception as e:
            logger.error(f"Failed to collect TODO data: {e}")
            return []
    
    def _structure_todo_data(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Structure TODO data for YAML output with location-based grouping.
        
        Args:
            todos: Raw TODO data
            
        Returns:
            Structured TODO data organized by priority, location, and category
        """
        # Priority-based grouping
        priority_groups = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Location-based grouping (following PrivacyYamlGenerator pattern)
        location_groups = defaultdict(list)
        
        # Category-based grouping
        category_groups = defaultdict(list)
        
        # Priority mapping
        def get_priority_level(priority_score):
            if priority_score >= 80:
                return 'critical'
            elif priority_score >= 60:
                return 'high'
            elif priority_score >= 40:
                return 'medium'
            else:
                return 'low'
        
        for todo in todos:
            priority_level = get_priority_level(todo.get('priority', 0))
            
            # Format for YAML output
            yaml_todo = {
                'content': todo['content'],
                'location': f"{todo['file_path']}:{todo['line_number']}",
                'priority_score': int(todo.get('priority', 0)),
                'priority_level': priority_level,
                'category': todo.get('category', 'general'),
                'created_at': todo.get('created_at', ''),
                'id': todo.get('id')
            }
            
            # Add metadata if available
            if todo.get('metadata'):
                yaml_todo['metadata'] = todo['metadata']
            
            # Group by priority
            priority_groups[priority_level].append(yaml_todo)
            
            # Group by location
            location_key = yaml_todo['location']
            location_groups[location_key].append({
                'content': yaml_todo['content'],
                'priority_level': priority_level,
                'priority_score': yaml_todo['priority_score'],
                'category': yaml_todo['category'],
                'id': yaml_todo['id']
            })
            
            # Group by category
            category_groups[yaml_todo['category']].append(yaml_todo)
        
        # Sort within each priority group by priority score (descending)
        for priority_level in priority_groups:
            priority_groups[priority_level].sort(key=lambda x: x['priority_score'], reverse=True)
        
        return {
            'todos': todos,
            'priority_groups': priority_groups,
            'location_groups': dict(location_groups),
            'category_groups': dict(category_groups)
        }
    
    def _build_yaml_structure(
        self, 
        structured_data: Dict[str, Any], 
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build structured YAML data optimized for AI consumption.
        
        Args:
            structured_data: Structured TODO data
            start_time: Report generation start time
            
        Returns:
            Complete YAML data structure
        """
        todos = structured_data['todos']
        priority_groups = structured_data['priority_groups']
        location_groups = structured_data['location_groups']
        category_groups = structured_data['category_groups']
        
        # Calculate summary statistics
        total_todos = len(todos)
        priority_counts = {
            level: len(group) for level, group in priority_groups.items()
        }
        
        # Calculate location statistics
        location_stats = {}
        for location, location_todos in location_groups.items():
            priorities = [t['priority_level'] for t in location_todos]
            location_stats[location] = {
                'todo_count': len(location_todos),
                'primary_priority': max(priorities, key=['critical', 'high', 'medium', 'low'].index) if priorities else 'low',
                'todos': location_todos,
                'categories_present': list(set(t['category'] for t in location_todos))
            }
        
        return {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'generator_version': '2.3.30',
                'format_version': '1.0',
                'schema_description': 'TODO analysis data optimized for AI consumption',
                'project_name': self.project_path.name,
                'window_hours': 24,
                'deduplication_applied': True
            },
            
            'todo_summary': {
                'total_todos': total_todos,
                'active_todos': total_todos,  # All collected TODOs are active (resolution detection already applied)
                'window_description': 'TODOs from last 24 hours with deduplication',
                'priority_breakdown': priority_counts,
                'locations_with_todos': len(location_groups),
                'categories_detected': len(category_groups)
            },
            
            'todos_by_priority': {
                'critical': self._format_todos_for_yaml(priority_groups['critical']),
                'high': self._format_todos_for_yaml(priority_groups['high']),
                'medium': self._format_todos_for_yaml(priority_groups['medium']),
                'low': self._format_todos_for_yaml(priority_groups['low'])
            },
            
            'todos_by_location': location_stats,
            
            'todos_by_category': {
                category: self._format_todos_for_yaml(category_todos)
                for category, category_todos in category_groups.items()
            },
            
            'priority_analysis': {
                'critical_ratio': priority_counts['critical'] / total_todos if total_todos > 0 else 0.0,
                'high_priority_ratio': (priority_counts['critical'] + priority_counts['high']) / total_todos if total_todos > 0 else 0.0,
                'most_common_priority': max(priority_counts.items(), key=lambda x: x[1])[0] if priority_counts else 'low',
                'average_priority_score': sum(t.get('priority', 0) for t in todos) / len(todos) if todos else 0.0
            },
            
            'performance_metrics': {
                'generation_time_seconds': (datetime.now() - start_time).total_seconds(),
                'total_todos_processed': total_todos,
                'deduplication_applied': True,
                'time_window_hours': 24
            },
            
            'ai_consumption_metadata': {
                'parsing_instruction': 'Use yaml.safe_load() for secure parsing',
                'data_access_examples': {
                    'total_todos': "data['todo_summary']['total_todos']",
                    'critical_count': "len(data['todos_by_priority']['critical'])",
                    'todos_at_location': "data['todos_by_location']['file.py:line']['todos']",
                    'category_todos': "data['todos_by_category']['bug_fixes']"
                },
                'recommended_libraries': ['PyYAML', 'ruamel.yaml'],
                'schema_stability': 'format_version tracks breaking changes',
                'integration_note': 'Replaces todos.json with enhanced AI-optimized structure'
            }
        }
    
    def _format_todos_for_yaml(self, todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format TODOs list for YAML output with type-safe data.
        
        Args:
            todos: TODOs to format
            
        Returns:
            List of TODO dictionaries optimized for YAML
        """
        yaml_todos = []
        
        for todo in todos:
            yaml_todo = {
                'content': todo['content'],
                'location': todo['location'],
                'priority_score': int(todo['priority_score']),  # Ensure numeric type
                'priority_level': todo['priority_level'],
                'category': todo['category'],
                'created_at': todo['created_at']
            }
            
            # Add metadata if available
            if todo.get('metadata'):
                yaml_todo['metadata'] = todo['metadata']
            
            # Add ID for tracking
            if todo.get('id'):
                yaml_todo['id'] = todo['id']
            
            yaml_todos.append(yaml_todo)
        
        return yaml_todos


# Standalone execution capability (matching PrivacyYamlGenerator pattern)
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python todo_yaml_generator.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    # Mock storage for standalone testing
    class MockStorage:
        def get_observations_by_type(self, obs_type):
            return []
    
    storage = MockStorage()
    generator = TodoYamlGenerator(project_path, storage)
    report_path = generator.generate_yaml_report()
    print(f"TODO YAML report generated: {report_path}")