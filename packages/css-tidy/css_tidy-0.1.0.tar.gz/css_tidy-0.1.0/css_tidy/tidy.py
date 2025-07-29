"""
Core CSS processing functionality.

This module contains the main classes for formatting, minifying, and validating CSS.
"""

import re
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CSSRule:
    """Represents a CSS rule with selector and properties."""
    selector: str
    properties: List[Tuple[str, str]]
    line_number: int = 0
    
    def get_prefix(self) -> str:
        """Get the prefix of the selector for grouping."""
        # Remove pseudo-classes and pseudo-elements
        selector = re.sub(r':[^,\s]+', '', self.selector)
        # Remove attribute selectors
        selector = re.sub(r'\[[^\]]*\]', '', selector)
        # Remove combinators
        selector = re.sub(r'[>+~]\s*', '', selector)
        
        # Split by comma and get the first part
        parts = [part.strip() for part in selector.split(',')]
        if not parts:
            return ""
        
        first_part = parts[0]
        
        # Extract class or id prefix
        if first_part.startswith('.'):
            # Class selector
            class_name = first_part[1:]
            # Find the base class name (before any modifiers)
            # Look for common prefixes like button-, card-, nav-, etc.
            if class_name.startswith('button'):
                return ".button"
            elif class_name.startswith('card'):
                return ".card"
            elif class_name.startswith('nav'):
                return ".nav"
            elif class_name.startswith('form'):
                return ".form"
            elif class_name.startswith('certification-timeline'):
                return ".certification-timeline"
            elif class_name.startswith('text-'):
                return ".text"
            elif class_name.startswith('mt-'):
                return ".mt"
            elif class_name.startswith('mb-'):
                return ".mb"
            else:
                # For other classes, use the first word
                base_name = re.match(r'^([a-zA-Z][a-zA-Z0-9_-]*)', class_name)
                if base_name:
                    return f".{base_name.group(1)}"
        elif first_part.startswith('#'):
            # ID selector
            id_name = first_part[1:]
            base_name = re.match(r'^([a-zA-Z][a-zA-Z0-9_-]*)', id_name)
            if base_name:
                return f"#{base_name.group(1)}"
        elif re.match(r'^[a-zA-Z]', first_part):
            # Element selector
            element_name = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)', first_part)
            if element_name:
                return element_name.group(1)
        
        return ""


class CSSFormatter:
    """Formats CSS code to make it more readable."""
    
    def __init__(self, 
                 indent_size: int = 2,
                 max_line_length: int = 80,
                 sort_properties: bool = False,
                 remove_comments: bool = False,
                 group_selectors: bool = False):
        """
        Initialize the CSS formatter.
        
        Args:
            indent_size: Number of spaces for indentation
            max_line_length: Maximum line length before wrapping
            sort_properties: Whether to sort CSS properties
            remove_comments: Whether to remove CSS comments
            group_selectors: Whether to group selectors by prefix
        """
        self.indent_size = indent_size
        self.max_line_length = max_line_length
        self.sort_properties = sort_properties
        self.remove_comments = remove_comments
        self.group_selectors = group_selectors
        self.indent = " " * indent_size
    
    def format(self, css_code: str) -> str:
        """
        Format CSS code.
        
        Args:
            css_code: Raw CSS code as string
            
        Returns:
            Formatted CSS code
        """
        if not css_code.strip():
            return ""
        
        # Remove comments if requested
        if self.remove_comments:
            css_code = self._remove_comments(css_code)
        
        # Parse CSS into rules
        rules = self._parse_css(css_code)
        
        # Group rules if requested
        if self.group_selectors:
            formatted_rules = self._format_grouped_rules(rules)
        else:
            # Format each rule individually
            formatted_rules = []
            for rule in rules:
                formatted_rule = self._format_rule(rule)
                formatted_rules.append(formatted_rule)
        
        return "\n\n".join(formatted_rules)
    
    def format_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Format a CSS file.
        
        Args:
            input_path: Path to input CSS file
            output_path: Path to output file (optional)
            
        Returns:
            Formatted CSS content
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            css_code = f.read()
        
        formatted_css = self.format(css_code)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_css)
        
        return formatted_css
    
    def _remove_comments(self, css_code: str) -> str:
        """Remove CSS comments from code."""
        # Remove /* ... */ comments
        css_code = re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)
        return css_code
    
    def _parse_css(self, css_code: str) -> List[CSSRule]:
        """Parse CSS code into a list of rules."""
        rules = []
        
        # Remove comments first for parsing
        css_code = re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)
        
        # Handle media queries and nested rules properly
        current_pos = 0
        brace_count = 0
        start_pos = 0
        
        for i, char in enumerate(css_code):
            if char == '{':
                if brace_count == 0:
                    start_pos = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Extract the complete rule
                    rule_text = css_code[start_pos:i+1]
                    selector_text = css_code[current_pos:start_pos].strip()
                    
                    if selector_text:
                        # Parse the rule
                        rule = self._parse_rule_block(selector_text, rule_text)
                        if rule:
                            rules.append(rule)
                    
                    current_pos = i + 1
        
        return rules
    
    def _parse_rule_block(self, selector_text: str, rule_text: str) -> Optional[CSSRule]:
        """Parse a single CSS rule block."""
        # Extract selector and properties
        brace_pos = rule_text.find('{')
        if brace_pos == -1:
            return None
        
        selector = selector_text
        properties_text = rule_text[brace_pos + 1:-1].strip()
        
        # Parse properties
        properties = self._parse_properties(properties_text)
        
        return CSSRule(selector=selector, properties=properties)
    
    def _parse_properties(self, properties_text: str) -> List[Tuple[str, str]]:
        """Parse CSS properties from text."""
        properties = []
        
        # Handle nested rules (like media queries)
        if '{' in properties_text:
            # This is a nested rule, not a property list
            return []
        
        # Split by semicolons
        prop_pairs = properties_text.split(';')
        
        for pair in prop_pairs:
            pair = pair.strip()
            if not pair:
                continue
            
            # Split by first colon
            colon_pos = pair.find(':')
            if colon_pos == -1:
                continue
            
            property_name = pair[:colon_pos].strip()
            property_value = pair[colon_pos + 1:].strip()
            
            properties.append((property_name, property_value))
        
        return properties
    
    def _format_rule(self, rule: CSSRule) -> str:
        """Format a single CSS rule."""
        # Format selector
        formatted_selector = rule.selector
        
        # Format properties
        if self.sort_properties:
            rule.properties.sort(key=lambda x: x[0])
        
        formatted_properties = []
        for name, value in rule.properties:
            # Check if property needs to be wrapped
            property_line = f"{self.indent}{name}: {value};"
            
            if len(property_line) > self.max_line_length:
                # Split long properties
                property_line = self._wrap_property(name, value)
            
            formatted_properties.append(property_line)
        
        # Combine selector and properties
        result = f"{formatted_selector} {{\n"
        result += "\n".join(formatted_properties)
        result += "\n}"
        
        return result
    
    def _wrap_property(self, name: str, value: str) -> str:
        """Wrap long CSS properties across multiple lines."""
        # Simple wrapping - split on spaces or commas
        if ',' in value:
            parts = value.split(',')
            wrapped_parts = []
            current_line = f"{self.indent}{name}: "
            
            for part in parts:
                part = part.strip()
                if len(current_line + part) > self.max_line_length:
                    wrapped_parts.append(current_line.rstrip())
                    current_line = f"{self.indent}  {part}, "
                else:
                    current_line += f"{part}, "
            
            wrapped_parts.append(current_line.rstrip() + ";")
            return "\n".join(wrapped_parts)
        else:
            return f"{self.indent}{name}: {value};"
    
    def _format_grouped_rules(self, rules: List[CSSRule]) -> List[str]:
        """Format CSS rules with grouping by selector prefix."""
        # Group rules by prefix
        groups: Dict[str, List[CSSRule]] = {}
        
        for rule in rules:
            prefix = rule.get_prefix()
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(rule)
        
        # Sort groups by prefix
        sorted_groups = sorted(groups.items())
        
        formatted_groups = []
        for prefix, group_rules in sorted_groups:
            if not prefix:
                # Handle rules without clear prefix
                for rule in group_rules:
                    formatted_rule = self._format_rule(rule)
                    formatted_groups.append(formatted_rule)
                continue
            
            # Add group header comment
            group_name = self._get_group_name(prefix)
            group_header = f"/**\n * {group_name}\n */"
            formatted_groups.append(group_header)
            
            # Sort rules within group by selector
            group_rules.sort(key=lambda r: r.selector)
            
            # Format rules in group
            for rule in group_rules:
                formatted_rule = self._format_rule(rule)
                formatted_groups.append(formatted_rule)
            
            # Add empty line after group
            formatted_groups.append("")
        
        return formatted_groups
    
    def _get_group_name(self, prefix: str) -> str:
        """Get a human-readable name for the group based on prefix."""
        if prefix.startswith('.'):
            # Class selector
            class_name = prefix[1:]
            # Convert kebab-case or snake_case to Title Case
            name = re.sub(r'[-_]', ' ', class_name)
            name = name.title()
            return f"{name} Components"
        elif prefix.startswith('#'):
            # ID selector
            id_name = prefix[1:]
            name = re.sub(r'[-_]', ' ', id_name)
            name = name.title()
            return f"{name} Element"
        else:
            # Element selector
            name = prefix.title()
            return f"{name} Elements"


class CSSMinifier:
    """Minifies CSS code to reduce file size."""
    
    def __init__(self, remove_comments: bool = True, remove_whitespace: bool = True):
        """
        Initialize the CSS minifier.
        
        Args:
            remove_comments: Whether to remove CSS comments
            remove_whitespace: Whether to remove unnecessary whitespace
        """
        self.remove_comments = remove_comments
        self.remove_whitespace = remove_whitespace
    
    def minify(self, css_code: str) -> str:
        """
        Minify CSS code.
        
        Args:
            css_code: Raw CSS code as string
            
        Returns:
            Minified CSS code
        """
        if not css_code.strip():
            return ""
        
        # Remove comments
        if self.remove_comments:
            css_code = self._remove_comments(css_code)
        
        # Remove unnecessary whitespace
        if self.remove_whitespace:
            css_code = self._remove_whitespace(css_code)
        
        return css_code
    
    def minify_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Minify a CSS file.
        
        Args:
            input_path: Path to input CSS file
            output_path: Path to output file (optional)
            
        Returns:
            Minified CSS content
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            css_code = f.read()
        
        minified_css = self.minify(css_code)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(minified_css)
        
        return minified_css
    
    def _remove_comments(self, css_code: str) -> str:
        """Remove CSS comments from code."""
        return re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)
    
    def _remove_whitespace(self, css_code: str) -> str:
        """Remove unnecessary whitespace from CSS."""
        # Remove newlines and tabs
        css_code = re.sub(r'[\n\t\r]', ' ', css_code)
        
        # Remove multiple spaces
        css_code = re.sub(r'\s+', ' ', css_code)
        
        # Remove spaces around certain characters
        css_code = re.sub(r'\s*([{}:;,>+])\s*', r'\1', css_code)
        
        # Remove trailing semicolons before closing braces
        css_code = re.sub(r';+}', '}', css_code)
        
        # Remove trailing spaces
        css_code = css_code.strip()
        
        return css_code


class CSSValidator:
    """Validates CSS code for syntax errors."""
    
    def __init__(self):
        """Initialize the CSS validator."""
        self.errors = []
        self.warnings = []
    
    def validate(self, css_code: str) -> bool:
        """
        Validate CSS code.
        
        Args:
            css_code: CSS code to validate
            
        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        if not css_code.strip():
            return True
        
        # Check for basic syntax errors
        self._check_braces(css_code)
        self._check_semicolons(css_code)
        self._check_colons(css_code)
        self._check_comments(css_code)
        
        return len(self.errors) == 0
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate a CSS file.
        
        Args:
            file_path: Path to CSS file
            
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(file_path):
            self.errors.append(f"File not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            css_code = f.read()
        
        return self.validate(css_code)
    
    def _check_braces(self, css_code: str) -> None:
        """Check for balanced braces."""
        open_braces = css_code.count('{')
        close_braces = css_code.count('}')
        
        if open_braces != close_braces:
            self.errors.append(f"Unbalanced braces: {open_braces} opening, {close_braces} closing")
    
    def _check_semicolons(self, css_code: str) -> None:
        """Check for proper semicolon usage."""
        # Remove comments first
        css_code = re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)
        
        # Find property declarations without semicolons
        lines = css_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            # Check if line contains a property declaration (has colon but no semicolon)
            if ':' in line and not line.endswith(';') and not line.endswith('{') and not line.endswith('}'):
                # Make sure it's actually a property declaration, not a selector
                if not line.startswith('@') and not line.endswith('{'):
                    self.warnings.append(f"Missing semicolon on line {i}: {line}")
        
        # Also check for missing semicolons in multi-line CSS
        # Look for patterns like "property: value }" (missing semicolon before closing brace)
        if '}' in css_code:
            # Find all property declarations that end with } without semicolon
            property_pattern = r'([a-zA-Z-]+)\s*:\s*([^;{}]+)\s*}'
            matches = re.finditer(property_pattern, css_code)
            for match in matches:
                property_name = match.group(1)
                property_value = match.group(2).strip()
                if property_value and not property_value.endswith(';'):
                    self.warnings.append(f"Missing semicolon before closing brace: {property_name}: {property_value}")
    
    def _check_colons(self, css_code: str) -> None:
        """Check for proper colon usage in properties."""
        # Remove comments first
        css_code = re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)
        
        # Find lines with properties that don't have colons
        lines = css_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('/*') and not line.endswith('{') and not line.endswith('}'):
                if ';' in line and ':' not in line:
                    self.errors.append(f"Missing colon in property on line {i}: {line}")
    
    def _check_comments(self, css_code: str) -> None:
        """Check for unclosed comments."""
        # Count /* and */ to check for unclosed comments
        open_comments = css_code.count('/*')
        close_comments = css_code.count('*/')
        
        if open_comments != close_comments:
            self.errors.append(f"Unclosed comments: {open_comments} opening, {close_comments} closing")
    
    def get_errors(self) -> List[str]:
        """Get list of validation errors."""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """Get list of validation warnings."""
        return self.warnings.copy() 