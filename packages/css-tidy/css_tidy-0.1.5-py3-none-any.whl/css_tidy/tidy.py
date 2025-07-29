"""
Core CSS processing functionality.

This module contains the main classes for formatting, minifying, and validating CSS.
"""

import re
import os
import json
from typing import List, Dict, Optional, Tuple, Set
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


@dataclass
class DuplicateRule:
    """Represents a duplicate CSS rule."""
    selector: str
    properties: List[Tuple[str, str]]
    line_numbers: List[int]
    is_removable: bool = True


class CSSDuplicateDetector:
    """Detects and manages duplicate CSS rules."""
    
    def __init__(self):
        """Initialize the duplicate detector."""
        self.duplicates: List[DuplicateRule] = []
    
    def detect_duplicates(self, css_code: str) -> List[DuplicateRule]:
        """
        Detect duplicate CSS rules in the code.
        
        Args:
            css_code: The CSS code to analyze
            
        Returns:
            List of duplicate rules found
        """
        # Parse CSS into rules
        rules = self._parse_css_rules(css_code)
        
        # Group rules by their normalized content
        rule_groups: Dict[str, List[Tuple[str, List[Tuple[str, str]], int]]] = {}
        
        for rule in rules:
            selector, properties, line_number = rule
            # Create a normalized key for comparison
            normalized_key = self._normalize_rule(selector, properties)
            
            if normalized_key not in rule_groups:
                rule_groups[normalized_key] = []
            rule_groups[normalized_key].append((selector, properties, line_number))
        
        # Find duplicates
        self.duplicates = []
        for normalized_key, rule_list in rule_groups.items():
            if len(rule_list) > 1:
                # This is a duplicate
                selector, properties, _ = rule_list[0]
                line_numbers = [rule[2] for rule in rule_list]
                
                # Check if this duplicate is removable (all instances are identical)
                is_removable = self._is_duplicate_removable(rule_list)
                
                duplicate_rule = DuplicateRule(
                    selector=selector,
                    properties=properties,
                    line_numbers=line_numbers,
                    is_removable=is_removable
                )
                self.duplicates.append(duplicate_rule)
        
        return self.duplicates
    
    def _parse_css_rules(self, css_code: str) -> List[Tuple[str, List[Tuple[str, str]], int]]:
        """Parse CSS code into individual rules with line numbers."""
        rules = []
        lines = css_code.split('\n')
        
        current_selector = ""
        current_properties = []
        current_line_start = 0
        brace_level = 0
        in_rule = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if not stripped or stripped.startswith('/*'):
                continue
            
            # Check for selector (line ending with {)
            if '{' in stripped and not in_rule:
                current_selector = stripped.split('{')[0].strip()
                current_properties = []
                current_line_start = i
                in_rule = True
                brace_level = stripped.count('{')
                continue
            
            if in_rule:
                brace_level += stripped.count('{')
                brace_level -= stripped.count('}')
                
                # Check for property declarations
                if ':' in stripped and ';' in stripped:
                    colon_pos = stripped.find(':')
                    semicolon_pos = stripped.find(';')
                    if colon_pos < semicolon_pos:
                        prop_name = stripped[:colon_pos].strip()
                        prop_value = stripped[colon_pos+1:semicolon_pos].strip()
                        current_properties.append((prop_name, prop_value))
                
                # End of rule
                if brace_level == 0:
                    if current_selector and current_properties:
                        rules.append((current_selector, current_properties, current_line_start))
                    current_selector = ""
                    current_properties = []
                    in_rule = False
        
        return rules
    
    def _normalize_rule(self, selector: str, properties: List[Tuple[str, str]]) -> str:
        """Create a normalized string for rule comparison."""
        # Normalize selector (remove extra spaces)
        normalized_selector = re.sub(r'\s+', ' ', selector.strip())
        
        # Sort properties for consistent comparison
        sorted_properties = sorted(properties, key=lambda x: x[0])
        
        # Create normalized string
        props_str = ';'.join([f"{name}:{value}" for name, value in sorted_properties])
        return f"{normalized_selector}{{{props_str}}}"
    
    def _is_duplicate_removable(self, rule_list: List[Tuple[str, List[Tuple[str, str]], int]]) -> bool:
        """Check if a duplicate rule can be safely removed."""
        if len(rule_list) < 2:
            return False
        
        # All instances must be identical to be removable
        first_rule = rule_list[0]
        for rule in rule_list[1:]:
            if rule[0] != first_rule[0] or rule[1] != first_rule[1]:
                return False
        
        return True
    
    def remove_duplicates(self, css_code: str) -> str:
        """
        Remove duplicate CSS rules from the code.
        
        Args:
            css_code: The CSS code to clean
            
        Returns:
            CSS code with duplicates removed
        """
        if not self.duplicates:
            self.detect_duplicates(css_code)
        
        # Parse CSS into rules with line ranges
        rules_with_ranges = self._parse_css_with_ranges(css_code)
        
        # Find rules to remove
        rules_to_remove = set()
        for duplicate in self.duplicates:
            if duplicate.is_removable:
                # Keep the first occurrence, mark the rest for removal
                for line_num in duplicate.line_numbers[1:]:
                    # Find the rule that starts at this line
                    for rule_info in rules_with_ranges:
                        if rule_info['start_line'] == line_num:
                            rules_to_remove.add(rule_info['rule_id'])
                            break
        
        # Rebuild CSS without removed rules
        lines = css_code.split('\n')
        lines_to_keep = set(range(len(lines)))
        
        for rule_info in rules_with_ranges:
            if rule_info['rule_id'] in rules_to_remove:
                # Remove all lines in this rule
                for i in range(rule_info['start_line'] - 1, rule_info['end_line']):
                    if i in lines_to_keep:
                        lines_to_keep.remove(i)
        
        # Rebuild CSS
        cleaned_lines = [lines[i] for i in range(len(lines)) if i in lines_to_keep]
        
        return '\n'.join(cleaned_lines)
    
    def _parse_css_with_ranges(self, css_code: str) -> List[Dict]:
        """Parse CSS code into rules with line ranges."""
        rules = []
        lines = css_code.split('\n')
        
        current_selector = ""
        current_properties = []
        current_line_start = 0
        brace_level = 0
        in_rule = False
        rule_id = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if not stripped or stripped.startswith('/*'):
                continue
            
            # Check for selector (line ending with {)
            if '{' in stripped and not in_rule:
                current_selector = stripped.split('{')[0].strip()
                current_properties = []
                current_line_start = i
                in_rule = True
                brace_level = stripped.count('{')
                continue
            
            if in_rule:
                brace_level += stripped.count('{')
                brace_level -= stripped.count('}')
                
                # Check for property declarations
                if ':' in stripped and ';' in stripped:
                    colon_pos = stripped.find(':')
                    semicolon_pos = stripped.find(';')
                    if colon_pos < semicolon_pos:
                        prop_name = stripped[:colon_pos].strip()
                        prop_value = stripped[colon_pos+1:semicolon_pos].strip()
                        current_properties.append((prop_name, prop_value))
                
                # End of rule
                if brace_level == 0:
                    if current_selector and current_properties:
                        rules.append({
                            'rule_id': rule_id,
                            'selector': current_selector,
                            'properties': current_properties,
                            'start_line': current_line_start,
                            'end_line': i
                        })
                        rule_id += 1
                    current_selector = ""
                    current_properties = []
                    in_rule = False
        
        return rules
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a JSON report of duplicate rules.
        
        Args:
            output_path: Optional path to save the report
            
        Returns:
            JSON string of the report
        """
        report = {
            "summary": {
                "total_duplicates": len(self.duplicates),
                "removable_duplicates": len([d for d in self.duplicates if d.is_removable]),
                "non_removable_duplicates": len([d for d in self.duplicates if not d.is_removable])
            },
            "duplicates": []
        }
        
        for duplicate in self.duplicates:
            duplicate_info = {
                "selector": duplicate.selector,
                "properties": [{"name": name, "value": value} for name, value in duplicate.properties],
                "line_numbers": duplicate.line_numbers,
                "is_removable": duplicate.is_removable,
                "occurrences": len(duplicate.line_numbers)
            }
            report["duplicates"].append(duplicate_info)
        
        json_report = json.dumps(report, indent=2)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_report)
        
        return json_report


class CSSFormatter:
    """Formats CSS code to make it more readable."""
    
    def __init__(self, 
                 indent_size: int = 2,
                 max_line_length: int = 80,
                 sort_properties: bool = False,
                 remove_comments: bool = False,
                 group_selectors: bool = False,
                 remove_duplicates: bool = False):
        """
        Initialize the CSS formatter.
        
        Args:
            indent_size: Number of spaces for indentation
            max_line_length: Maximum line length before wrapping
            sort_properties: Whether to sort CSS properties
            remove_comments: Whether to remove CSS comments
            group_selectors: Whether to group selectors by prefix
            remove_duplicates: Whether to remove duplicate CSS rules
        """
        self.indent_size = indent_size
        self.max_line_length = max_line_length
        self.sort_properties = sort_properties
        self.remove_comments = remove_comments
        self.group_selectors = group_selectors
        self.remove_duplicates = remove_duplicates
        self.duplicate_detector = CSSDuplicateDetector() if remove_duplicates else None
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
        
        # Remove duplicates if requested
        if self.remove_duplicates and self.duplicate_detector:
            css_code = self.duplicate_detector.remove_duplicates(css_code)
        
        # Use conservative formatting that preserves all content
        if self.group_selectors:
            css_code = self._format_grouped_conservative(css_code)
        else:
            css_code = self._format_conservative(css_code)
        
        # Remove comments if requested (after formatting to catch group comments)
        if self.remove_comments:
            css_code = self._remove_comments(css_code)
        
        return css_code
    
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
        """Remove CSS comments from the code."""
        # First compress to one line using csscompressor logic
        def compress_to_one_line(css):
            import re
            # Remove comments first
            css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
            # Remove all whitespace and newlines
            css = re.sub(r'\s+', ' ', css)
            # Remove spaces around certain characters
            css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
            # Remove trailing spaces
            css = css.strip()
            return css
        
        # Compress to one line first
        compressed_css = compress_to_one_line(css_code)
        
        # Then completely reformat using proper CSS parsing
        def reformat_css(css):
            import re
            result = []
            i = 0
            indent_level = 0
            
            while i < len(css):
                char = css[i]
                
                if char == '{':
                    # Find the selector (everything before {)
                    selector_start = i - 1
                    while selector_start >= 0 and css[selector_start] not in ';}':
                        selector_start -= 1
                    selector = css[selector_start + 1:i].strip()
                    
                    result.append(self.indent * indent_level + selector + ' {')
                    indent_level += 1
                    i += 1
                    
                    # Find the closing brace
                    brace_count = 1
                    property_start = i
                    while i < len(css) and brace_count > 0:
                        if css[i] == '{':
                            brace_count += 1
                        elif css[i] == '}':
                            brace_count -= 1
                        i += 1
                    
                    # Process properties inside the block
                    properties_text = css[property_start:i-1]
                    if properties_text.strip():
                        # Split properties by semicolon
                        properties = properties_text.split(';')
                        for prop in properties:
                            prop = prop.strip()
                            if prop and ':' in prop:
                                result.append(self.indent * indent_level + prop + ';')
                    
                    indent_level -= 1
                    result.append(self.indent * indent_level + '}')
                    
                elif char == '@':
                    # Handle @media, @keyframes, etc.
                    at_rule_start = i
                    brace_count = 0
                    while i < len(css):
                        if css[i] == '{':
                            brace_count += 1
                        elif css[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                break
                        i += 1
                    
                    at_rule = css[at_rule_start:i+1]
                    result.append(self.indent * indent_level + at_rule)
                    i += 1
                    
                else:
                    i += 1
            
            return '\n'.join(result)
        
        return reformat_css(compressed_css)
    
    def _parse_css(self, css_code: str) -> List[CSSRule]:
        """Parse CSS code into a list of rules."""
        rules = []
        
        # Remove comments first for parsing
        css_code = re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)
        
        # Handle media queries and nested rules properly
        current_pos = 0
        brace_count = 0
        start_pos = 0
        in_string = False
        string_char = None
        
        for i, char in enumerate(css_code):
            # Handle string literals to avoid counting braces inside strings
            if char in ['"', "'"] and (i == 0 or css_code[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif string_char == char:
                    in_string = False
                    string_char = None
            
            if not in_string:
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
        
        # Normalize line breaks and remove extra whitespace
        properties_text = re.sub(r'\s+', ' ', properties_text)
        
        # Split by semicolons, but be careful with nested structures
        prop_pairs = []
        current_prop = ""
        paren_count = 0
        bracket_count = 0
        in_string = False
        string_char = None
        
        for char in properties_text:
            # Handle string literals
            if char in ['"', "'"] and (len(current_prop) == 0 or current_prop[-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif string_char == char:
                    in_string = False
                    string_char = None
            
            if not in_string:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                elif char == ';' and paren_count == 0 and bracket_count == 0:
                    if current_prop.strip():
                        prop_pairs.append(current_prop.strip())
                    current_prop = ""
                    continue
            
            current_prop += char
        
        # Add the last property if it exists
        if current_prop.strip():
            prop_pairs.append(current_prop.strip())
        
        for pair in prop_pairs:
            if not pair:
                continue
            
            # Split by first colon
            colon_pos = pair.find(':')
            if colon_pos == -1:
                continue
            
            property_name = pair[:colon_pos].strip()
            property_value = pair[colon_pos + 1:].strip()
            
            # Clean up the property value
            property_value = re.sub(r'\s+', ' ', property_value)
            
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
        # For CSS custom properties and complex values, keep them on one line
        complex_keywords = ['linear-gradient', 'radial-gradient', 'conic-gradient', 'var(', 'calc(', 'url(', 'hsla(', 'rgba(']
        if name.startswith('--') or any(keyword in value for keyword in complex_keywords):
            return f"{self.indent}{name}: {value};"
        
        # For properties that should not be wrapped (like box-shadow, transition, transform)
        no_wrap_properties = ['box-shadow', 'transition', 'transform', 'background', 'border', 'margin', 'padding']
        if name in no_wrap_properties:
            return f"{self.indent}{name}: {value};"
        
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
    
    def _format_conservative(self, css_code: str) -> str:
        """
        Format CSS conservatively, preserving all content but removing all empty lines inside rule blocks.
        """
        import re
        lines = css_code.split('\n')
        formatted_lines = []
        indent_level = 0
        in_block = False
        for line in lines:
            stripped = line.rstrip()
            # Detect block start
            if '{' in stripped:
                in_block = True
                formatted_lines.append(self.indent * indent_level + stripped)
                indent_level += 1
                continue
            # Detect block end
            if '}' in stripped:
                indent_level = max(0, indent_level - 1)
                in_block = False
                formatted_lines.append(self.indent * indent_level + stripped)
                continue
            # Inside block - skip all empty/whitespace-only lines
            if in_block:
                if not stripped.strip():
                    continue
                formatted_lines.append(self.indent * indent_level + stripped.lstrip())
            else:
                if not stripped.strip():
                    continue
                formatted_lines.append(stripped)
        # Join all lines
        result = '\n'.join(formatted_lines)
        # Remove any empty lines (even多個)在 { ... } 內部
        def remove_empty_in_blocks(css):
            def repl(match):
                block = match.group(1)
                # 移除所有空行
                block = re.sub(r'(^|\n)[ \t]*\n+', '\n', block)
                # 移除開頭空行
                block = re.sub(r'^\n+', '', block)
                # 移除結尾空行
                block = re.sub(r'\n+$', '', block)
                return '{\n' + block + '\n}'
            return re.sub(r'\{([\s\S]*?)\}', repl, css)
        result = remove_empty_in_blocks(result)
        # 移除檔案開頭結尾空行
        result = result.strip() + '\n'
        return result
    
    def _format_grouped_conservative(self, css_code: str) -> str:
        """Format CSS with grouping, preserving all content."""
        # For now, use conservative formatting without grouping
        # to ensure no content is lost, especially for @keyframes and @media
        return self._format_conservative(css_code)


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
                    # Skip CSS custom properties (variables)
                    if line.startswith('--'):
                        continue
                    # Skip lines that are part of multi-line properties
                    if line.endswith('(') or line.startswith(')'):
                        continue
                    # Skip selectors (lines ending with comma)
                    if line.endswith(','):
                        continue
                    # Skip lines that are clearly selectors
                    if re.match(r'^[.#]?[a-zA-Z-]+[,\s]*$', line):
                        continue
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
                # Skip CSS custom properties
                if property_name.startswith('--'):
                    continue
                if property_value and not property_value.endswith(';'):
                    self.warnings.append(f"Missing semicolon before closing brace: {property_name}: {property_value}")
    
    def _check_colons(self, css_code: str) -> None:
        """Check for proper colon usage in properties."""
        # Remove comments first
        css_code = re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)
        
        # Find lines with properties that don't have colons
        lines = css_code.split('\n')
        brace_level = 0
        in_multiline_property = False
        
        for i, line in enumerate(lines, 1):
            original_line = line.strip()
            line = original_line
            
            # Update brace level
            brace_level += line.count('{')
            brace_level -= line.count('}')
            
            # Skip empty lines, comments, and rule boundaries
            if not line or line.startswith('/*') or line.endswith('{') or line.endswith('}'):
                continue
                
            # Skip CSS custom properties (variables)
            if line.startswith('--'):
                continue
                
            # Skip selectors (lines ending with comma or containing selectors)
            if line.endswith(',') or re.match(r'^[.#]?[a-zA-Z0-9_-]+([:\[].*?)?[,>+~ ]*$', line):
                continue
                
            # Handle multi-line properties
            if ':' in line and not line.endswith(';') and not line.endswith('}'):
                # This might be the start of a multi-line property
                if not in_multiline_property:
                    in_multiline_property = True
                continue
            
            if in_multiline_property:
                if line.endswith(';') or line.endswith('}'):
                    # End of multi-line property
                    in_multiline_property = False
                continue
                
            # Skip lines that are part of multi-line values
            if '(' in line and ')' not in line:  # Start of a multi-line value
                continue
            if ')' in line and '(' not in line:  # End of a multi-line value
                continue
                
            # Skip lines that are just property values or function calls
            if re.match(r'^[0-9.\s-]+[a-zA-Z%()]+.*;', line) or \
               re.match(r'^[a-zA-Z-]+\s*\(', line) or \
               re.match(r'^[a-zA-Z-]+\s*[0-9.%]+', line) or \
               line.endswith('(') or line.startswith(')'):
                continue
                
            # Check for missing colons in property declarations
            if ';' in line and ':' not in line and not line.startswith('--'):
                # Make sure it's not a closing parenthesis or other syntax
                if not line.strip().startswith(')') and not line.strip().endswith('('):
                    # Additional check for multi-line property values
                    if not re.match(r'^[a-zA-Z-]+\s+[0-9.-]', line):
                        self.errors.append(f"Missing colon in property on line {i}: {original_line}")
            elif ':' not in line and brace_level > 0:  # If inside a rule and no colon, it's likely an error
                # Further check to ensure it's not a selector or at-rule
                if not re.match(r'^[a-zA-Z0-9_-]+(\s*[,>+~:]\s*[a-zA-Z0-9_-]+)*\s*\{?$', line) and \
                   not line.startswith('@'):
                    self.errors.append(f"Missing colon in property on line {i}: {original_line}")
    
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