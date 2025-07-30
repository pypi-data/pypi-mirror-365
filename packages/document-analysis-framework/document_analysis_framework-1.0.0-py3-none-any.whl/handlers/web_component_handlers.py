"""
Web component handlers for Vue and Svelte single file components

Handles analysis of modern frontend framework component files that
combine template, script, and style in a single file.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class VueHandler(DocumentHandler):
    """
    Handler for Vue Single File Components (.vue files).
    
    Analyzes Vue components including template, script, and style blocks,
    component options, composition API usage, and Vue-specific patterns.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the Vue file."""
        if file_path.endswith('.vue'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Vue SFC patterns
            if any(pattern in text for pattern in [
                '<template>', '<script>', '<style>',
                'export default', 'defineComponent',
                'v-if', 'v-for', 'v-model', '@click'
            ]):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Vue version and API style."""
        text = content.decode('utf-8', errors='ignore')
        
        # Detect Vue version and API style
        vue_version = "Vue 2"
        api_style = "Options API"
        
        if '<script setup>' in text or 'defineProps' in text or 'defineEmits' in text:
            vue_version = "Vue 3"
            api_style = "Composition API (Script Setup)"
        elif 'defineComponent' in text or 'ref(' in text or 'computed(' in text:
            vue_version = "Vue 3"
            api_style = "Composition API"
        
        return DocumentTypeInfo(
            type_name=f"{vue_version} Component ({api_style})",
            confidence=0.95,
            category="web",
            format="vue",
            framework="Vue.js"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed Vue component analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Vue Component",
            category="web",
            key_findings=findings,
            ai_use_cases=[
                "Component refactoring and optimization",
                "Props and events documentation",
                "Composition API migration",
                "Performance optimization",
                "Accessibility improvements",
                "Unit test generation"
            ],
            quality_metrics={
                "component_complexity": self._assess_complexity(findings),
                "code_organization": self._assess_organization(findings),
                "best_practices": self._assess_best_practices(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract Vue component structure and features."""
        text = content.decode('utf-8', errors='ignore')
        
        # Extract main blocks
        template_block = self._extract_block(text, 'template')
        script_block = self._extract_block(text, 'script')
        style_blocks = self._extract_style_blocks(text)
        
        return {
            "blocks": {
                "has_template": bool(template_block),
                "has_script": bool(script_block),
                "style_count": len(style_blocks),
                "script_setup": '<script setup>' in text
            },
            "template": self._analyze_template(template_block) if template_block else {},
            "script": self._analyze_script(script_block) if script_block else {},
            "styles": self._analyze_styles(style_blocks),
            "component_name": self._extract_component_name(script_block, file_path),
            "dependencies": self._extract_imports(script_block) if script_block else [],
            "api_features": self._detect_api_features(script_block) if script_block else {},
            "directives": self._extract_directives(template_block) if template_block else {},
            "custom_blocks": self._extract_custom_blocks(text)
        }
    
    def _extract_block(self, text: str, block_type: str) -> Optional[str]:
        """Extract a specific block from Vue SFC."""
        pattern = rf'<{block_type}[^>]*>(.*?)</{block_type}>'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1) if match else None
    
    def _extract_style_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Extract all style blocks with their attributes."""
        style_blocks = []
        for match in re.finditer(r'<style([^>]*)>(.*?)</style>', text, re.DOTALL):
            attrs = match.group(1)
            content = match.group(2)
            
            style_blocks.append({
                "content": content,
                "scoped": 'scoped' in attrs,
                "lang": self._extract_lang_attr(attrs),
                "module": 'module' in attrs
            })
        
        return style_blocks
    
    def _extract_lang_attr(self, attrs: str) -> str:
        """Extract lang attribute value."""
        match = re.search(r'lang=["\'](\w+)["\']', attrs)
        return match.group(1) if match else "css"
    
    def _analyze_template(self, template: str) -> Dict[str, Any]:
        """Analyze Vue template block."""
        return {
            "root_elements": len(re.findall(r'<\w+', template.split('\n')[0])),
            "interpolations": len(re.findall(r'\{\{[^}]+\}\}', template)),
            "v_if": len(re.findall(r'v-if=', template)),
            "v_for": len(re.findall(r'v-for=', template)),
            "v_model": len(re.findall(r'v-model', template)),
            "event_handlers": len(re.findall(r'@\w+|v-on:', template)),
            "slots": len(re.findall(r'<slot', template)),
            "components": self._extract_template_components(template),
            "dynamic_bindings": len(re.findall(r':[a-zA-Z-]+=|v-bind:', template))
        }
    
    def _extract_template_components(self, template: str) -> List[str]:
        """Extract custom components used in template."""
        # Look for PascalCase or kebab-case components
        pascal_case = re.findall(r'<([A-Z][a-zA-Z0-9]+)', template)
        kebab_case = re.findall(r'<([a-z]+(?:-[a-z]+)+)', template)
        
        # Filter out HTML elements
        html_elements = {'div', 'span', 'p', 'a', 'img', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
        components = [c for c in pascal_case + kebab_case if c.lower() not in html_elements]
        
        return list(set(components))
    
    def _analyze_script(self, script: str) -> Dict[str, Any]:
        """Analyze Vue script block."""
        is_typescript = 'lang="ts"' in script or 'lang=\'ts\'' in script
        
        return {
            "language": "typescript" if is_typescript else "javascript",
            "lines_of_code": len(script.split('\n')),
            "props": self._extract_props(script),
            "data_properties": self._extract_data_properties(script),
            "computed": self._extract_computed(script),
            "methods": self._extract_methods(script),
            "lifecycle_hooks": self._extract_lifecycle_hooks(script),
            "emits": self._extract_emits(script),
            "components": self._extract_registered_components(script),
            "mixins": len(re.findall(r'mixins:\s*\[', script)) > 0,
            "setup_function": 'setup(' in script or 'setup:' in script
        }
    
    def _extract_props(self, script: str) -> Dict[str, Any]:
        """Extract component props."""
        props_info = {
            "count": 0,
            "names": [],
            "has_types": False,
            "has_defaults": False
        }
        
        # Props array syntax
        array_match = re.search(r'props:\s*\[([^\]]+)\]', script)
        if array_match:
            props_str = array_match.group(1)
            props_info["names"] = [p.strip().strip("'\"") for p in props_str.split(',')]
            props_info["count"] = len(props_info["names"])
        
        # Props object syntax
        object_match = re.search(r'props:\s*\{([^}]+)\}', script, re.DOTALL)
        if object_match:
            props_block = object_match.group(1)
            props_info["names"] = re.findall(r'(\w+):', props_block)
            props_info["count"] = len(props_info["names"])
            props_info["has_types"] = 'type:' in props_block
            props_info["has_defaults"] = 'default:' in props_block
        
        # Composition API defineProps
        if 'defineProps' in script:
            props_info["count"] = len(re.findall(r'defineProps', script))
            props_info["has_types"] = True  # defineProps usually includes types
        
        return props_info
    
    def _extract_data_properties(self, script: str) -> List[str]:
        """Extract data properties."""
        properties = []
        
        # Options API data function
        data_match = re.search(r'data\s*\(\)\s*\{[^{]*return\s*\{([^}]+)\}', script, re.DOTALL)
        if data_match:
            data_block = data_match.group(1)
            properties = re.findall(r'(\w+):', data_block)
        
        # Composition API reactive/ref
        properties.extend(re.findall(r'const\s+(\w+)\s*=\s*ref\(', script))
        properties.extend(re.findall(r'const\s+(\w+)\s*=\s*reactive\(', script))
        
        return list(set(properties))
    
    def _extract_computed(self, script: str) -> List[str]:
        """Extract computed properties."""
        computed = []
        
        # Options API
        computed_match = re.search(r'computed:\s*\{([^}]+)\}', script, re.DOTALL)
        if computed_match:
            computed_block = computed_match.group(1)
            computed = re.findall(r'(\w+)\s*\(', computed_block)
        
        # Composition API
        computed.extend(re.findall(r'const\s+(\w+)\s*=\s*computed\(', script))
        
        return list(set(computed))
    
    def _extract_methods(self, script: str) -> List[str]:
        """Extract component methods."""
        methods = []
        
        # Options API
        methods_match = re.search(r'methods:\s*\{([^}]+)\}', script, re.DOTALL)
        if methods_match:
            methods_block = methods_match.group(1)
            methods = re.findall(r'(\w+)\s*\(', methods_block)
        
        # Also look for arrow functions in setup or script setup
        methods.extend(re.findall(r'const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>', script))
        
        return list(set(methods))
    
    def _extract_lifecycle_hooks(self, script: str) -> List[str]:
        """Extract lifecycle hooks used."""
        hooks = []
        
        # Options API hooks
        options_hooks = [
            'beforeCreate', 'created', 'beforeMount', 'mounted',
            'beforeUpdate', 'updated', 'beforeDestroy', 'destroyed',
            'beforeUnmount', 'unmounted', 'activated', 'deactivated'
        ]
        
        for hook in options_hooks:
            if re.search(rf'{hook}\s*\(', script):
                hooks.append(hook)
        
        # Composition API hooks
        composition_hooks = [
            'onBeforeMount', 'onMounted', 'onBeforeUpdate', 'onUpdated',
            'onBeforeUnmount', 'onUnmounted', 'onActivated', 'onDeactivated'
        ]
        
        for hook in composition_hooks:
            if hook in script:
                hooks.append(hook)
        
        return hooks
    
    def _extract_emits(self, script: str) -> List[str]:
        """Extract emitted events."""
        emits = []
        
        # Options API emits
        emits_match = re.search(r'emits:\s*\[([^\]]+)\]', script)
        if emits_match:
            emits_str = emits_match.group(1)
            emits = [e.strip().strip("'\"") for e in emits_str.split(',')]
        
        # Composition API defineEmits
        if 'defineEmits' in script:
            define_match = re.search(r'defineEmits\(\[([^\]]+)\]', script)
            if define_match:
                emits_str = define_match.group(1)
                emits.extend([e.strip().strip("'\"") for e in emits_str.split(',')])
        
        # $emit calls
        emits.extend(re.findall(r'\$emit\([\'"](\w+)[\'"]', script))
        
        return list(set(emits))
    
    def _extract_registered_components(self, script: str) -> List[str]:
        """Extract registered components."""
        components = []
        
        # Components object
        comp_match = re.search(r'components:\s*\{([^}]+)\}', script)
        if comp_match:
            comp_block = comp_match.group(1)
            components = re.findall(r'(\w+)[:,]', comp_block)
        
        return components
    
    def _extract_imports(self, script: str) -> List[Dict[str, str]]:
        """Extract import statements."""
        imports = []
        
        for match in re.finditer(r'import\s+(.+?)\s+from\s+[\'"]([^\'"]+)[\'"]', script):
            what = match.group(1).strip()
            from_where = match.group(2)
            
            imports.append({
                "what": what,
                "from": from_where,
                "is_vue": 'vue' in from_where.lower(),
                "is_component": '.vue' in from_where or '/components/' in from_where
            })
        
        return imports
    
    def _detect_api_features(self, script: str) -> Dict[str, bool]:
        """Detect Vue API features used."""
        return {
            "options_api": 'export default' in script and 'data()' in script,
            "composition_api": any(api in script for api in ['setup(', 'ref(', 'reactive(', 'computed(']),
            "script_setup": '<script setup>' in script,
            "typescript": 'lang="ts"' in script or 'lang=\'ts\'' in script,
            "jsx": 'jsx' in script.lower() or 'tsx' in script.lower(),
            "pinia": 'pinia' in script.lower() or 'defineStore' in script,
            "vuex": 'vuex' in script.lower() or '$store' in script,
            "vue_router": 'vue-router' in script or '$route' in script
        }
    
    def _analyze_styles(self, style_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze style blocks."""
        total_lines = 0
        languages = []
        
        for block in style_blocks:
            total_lines += len(block['content'].split('\n'))
            languages.append(block['lang'])
        
        return {
            "total_blocks": len(style_blocks),
            "total_lines": total_lines,
            "scoped_count": sum(1 for b in style_blocks if b['scoped']),
            "languages": list(set(languages)),
            "uses_css_modules": any(b['module'] for b in style_blocks)
        }
    
    def _extract_directives(self, template: str) -> Dict[str, int]:
        """Extract Vue directives usage."""
        directives = {
            "v-if": len(re.findall(r'v-if=', template)),
            "v-else-if": len(re.findall(r'v-else-if=', template)),
            "v-else": len(re.findall(r'v-else', template)),
            "v-for": len(re.findall(r'v-for=', template)),
            "v-model": len(re.findall(r'v-model', template)),
            "v-show": len(re.findall(r'v-show=', template)),
            "v-bind": len(re.findall(r'v-bind:|:', template)),
            "v-on": len(re.findall(r'v-on:|@', template)),
            "v-slot": len(re.findall(r'v-slot:|#', template)),
            "v-pre": len(re.findall(r'v-pre', template)),
            "v-once": len(re.findall(r'v-once', template)),
            "v-text": len(re.findall(r'v-text=', template)),
            "v-html": len(re.findall(r'v-html=', template))
        }
        
        # Remove directives with 0 usage
        return {k: v for k, v in directives.items() if v > 0}
    
    def _extract_custom_blocks(self, text: str) -> List[str]:
        """Extract custom blocks (non-standard blocks)."""
        standard_blocks = {'template', 'script', 'style'}
        all_blocks = re.findall(r'<(\w+)[^>]*>', text)
        custom_blocks = [b for b in all_blocks if b not in standard_blocks and not b.startswith('/')]
        return list(set(custom_blocks))
    
    def _extract_component_name(self, script: str, file_path: str) -> str:
        """Extract component name from script or filename."""
        if script:
            # Look for name property
            name_match = re.search(r'name:\s*[\'"](\w+)[\'"]', script)
            if name_match:
                return name_match.group(1)
        
        # Fallback to filename
        import os
        filename = os.path.basename(file_path)
        return filename.replace('.vue', '')
    
    def _assess_complexity(self, findings: Dict[str, Any]) -> float:
        """Assess component complexity."""
        score = 1.0
        
        # Template complexity
        template = findings.get('template', {})
        if template.get('v_for', 0) > 5:
            score -= 0.1
        if template.get('v_if', 0) > 10:
            score -= 0.1
        
        # Script complexity
        script = findings.get('script', {})
        if script.get('lines_of_code', 0) > 300:
            score -= 0.2
        elif script.get('lines_of_code', 0) > 200:
            score -= 0.1
        
        # Too many props
        props = script.get('props', {})
        if props.get('count', 0) > 10:
            score -= 0.1
        
        return max(score, 0.3)
    
    def _assess_organization(self, findings: Dict[str, Any]) -> float:
        """Assess code organization."""
        score = 0.5
        
        # Has all three blocks is good
        blocks = findings.get('blocks', {})
        if blocks.get('has_template') and blocks.get('has_script'):
            score += 0.2
        
        # Using TypeScript
        if findings.get('api_features', {}).get('typescript'):
            score += 0.1
        
        # Props have types
        if findings.get('script', {}).get('props', {}).get('has_types'):
            score += 0.1
        
        # Scoped styles
        styles = findings.get('styles', {})
        if styles.get('scoped_count', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_best_practices(self, findings: Dict[str, Any]) -> float:
        """Assess Vue best practices."""
        score = 0.5
        
        # Using Composition API or Script Setup (modern)
        api_features = findings.get('api_features', {})
        if api_features.get('script_setup') or api_features.get('composition_api'):
            score += 0.15
        
        # Emitting events properly
        if findings.get('script', {}).get('emits'):
            score += 0.1
        
        # No v-html (security risk)
        if findings.get('directives', {}).get('v-html', 0) == 0:
            score += 0.1
        
        # Component name defined
        if findings.get('component_name'):
            score += 0.05
        
        # Using key with v-for
        template = findings.get('template', {})
        if template.get('v_for', 0) > 0:
            # This is a simplified check
            score += 0.1
        
        return min(score, 1.0)


class SvelteHandler(DocumentHandler):
    """
    Handler for Svelte component files (.svelte).
    
    Analyzes Svelte components including script, style, and markup sections,
    reactive declarations, stores, and Svelte-specific features.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the Svelte file."""
        if file_path.endswith('.svelte'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Svelte patterns
            if any(pattern in text for pattern in [
                '<script>', '$:', '{#if', '{#each', '{@html',
                'export let', 'on:', 'bind:', 'use:'
            ]):
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Svelte component type."""
        text = content.decode('utf-8', errors='ignore')
        
        # Detect special Svelte files
        if '<script context="module">' in text:
            component_type = "Svelte Component with Module Context"
        elif file_path.endswith('.svelte') and '+' in os.path.basename(file_path):
            component_type = "SvelteKit Route Component"
        else:
            component_type = "Svelte Component"
        
        return DocumentTypeInfo(
            type_name=component_type,
            confidence=0.95,
            category="web",
            format="svelte",
            framework="Svelte"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed Svelte component analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Svelte Component",
            category="web",
            key_findings=findings,
            ai_use_cases=[
                "Component optimization",
                "Reactive statement analysis",
                "Store management improvements",
                "Accessibility enhancements",
                "Performance optimization",
                "TypeScript migration"
            ],
            quality_metrics={
                "reactivity_usage": self._assess_reactivity(findings),
                "component_structure": self._assess_structure(findings),
                "performance": self._assess_performance(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract Svelte component structure and features."""
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "scripts": self._extract_scripts(text),
            "markup": self._analyze_markup(text),
            "styles": self._extract_styles(text),
            "props": self._extract_props(text),
            "reactive_statements": self._extract_reactive_statements(text),
            "stores": self._extract_stores(text),
            "events": self._extract_events(text),
            "slots": self._extract_slots(text),
            "actions": self._extract_actions(text),
            "imports": self._extract_imports(text),
            "sveltekit_features": self._detect_sveltekit_features(text, file_path)
        }
    
    def _extract_scripts(self, text: str) -> Dict[str, Any]:
        """Extract script blocks and analyze them."""
        scripts = {
            "instance": None,
            "module": None,
            "has_typescript": False
        }
        
        # Instance script
        instance_match = re.search(r'<script(?:\s+lang="ts")?>(.*?)</script>', text, re.DOTALL)
        if instance_match:
            scripts["instance"] = instance_match.group(1)
            scripts["has_typescript"] = 'lang="ts"' in instance_match.group(0)
        
        # Module context script
        module_match = re.search(r'<script\s+context="module"[^>]*>(.*?)</script>', text, re.DOTALL)
        if module_match:
            scripts["module"] = module_match.group(1)
        
        return scripts
    
    def _analyze_markup(self, text: str) -> Dict[str, Any]:
        """Analyze Svelte markup/template."""
        # Remove script and style blocks for markup analysis
        markup = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        markup = re.sub(r'<style[^>]*>.*?</style>', '', markup, flags=re.DOTALL)
        
        return {
            "interpolations": len(re.findall(r'\{[^{}]+\}', markup)),
            "if_blocks": len(re.findall(r'\{#if', markup)),
            "each_blocks": len(re.findall(r'\{#each', markup)),
            "await_blocks": len(re.findall(r'\{#await', markup)),
            "key_blocks": len(re.findall(r'\{#key', markup)),
            "html_directive": len(re.findall(r'\{@html', markup)),
            "debug_tags": len(re.findall(r'\{@debug', markup)),
            "component_bindings": len(re.findall(r'bind:', markup)),
            "event_handlers": len(re.findall(r'on:', markup)),
            "use_directives": len(re.findall(r'use:', markup)),
            "class_directives": len(re.findall(r'class:', markup)),
            "transition_directives": len(re.findall(r'transition:|in:|out:', markup))
        }
    
    def _extract_styles(self, text: str) -> Dict[str, Any]:
        """Extract and analyze style blocks."""
        styles = []
        
        for match in re.finditer(r'<style([^>]*)>(.*?)</style>', text, re.DOTALL):
            attrs = match.group(1)
            content = match.group(2)
            
            styles.append({
                "lang": self._extract_lang_attr(attrs),
                "global": 'global' in attrs,
                "lines": len(content.split('\n'))
            })
        
        return {
            "blocks": styles,
            "total_blocks": len(styles),
            "has_global_styles": any(s['global'] for s in styles),
            "preprocessors": list(set(s['lang'] for s in styles if s['lang'] != 'css'))
        }
    
    def _extract_lang_attr(self, attrs: str) -> str:
        """Extract lang attribute from element attributes."""
        match = re.search(r'lang=["\'](\w+)["\']', attrs)
        return match.group(1) if match else "css"
    
    def _extract_props(self, text: str) -> List[Dict[str, Any]]:
        """Extract component props (exported variables)."""
        props = []
        
        # Extract exported let declarations
        for match in re.finditer(r'export\s+let\s+(\w+)(?:\s*[:=]\s*([^;\n]+))?', text):
            prop_name = match.group(1)
            default_value = match.group(2) if match.group(2) else None
            
            props.append({
                "name": prop_name,
                "has_default": default_value is not None,
                "default_value": default_value[:20] if default_value else None  # Truncate
            })
        
        return props
    
    def _extract_reactive_statements(self, text: str) -> Dict[str, Any]:
        """Extract reactive declarations and statements."""
        # Count $: reactive statements
        reactive_count = len(re.findall(r'\$:', text))
        
        # Extract reactive variables
        reactive_vars = re.findall(r'\$:\s*(?:let\s+)?(\w+)\s*=', text)
        
        return {
            "count": reactive_count,
            "variables": list(set(reactive_vars)),
            "has_reactive_statements": reactive_count > 0
        }
    
    def _extract_stores(self, text: str) -> Dict[str, Any]:
        """Extract Svelte store usage."""
        stores = {
            "imported_stores": [],
            "store_subscriptions": [],
            "auto_subscriptions": []
        }
        
        # Find store imports
        for match in re.finditer(r'import\s*\{([^}]+)\}\s*from\s*[\'"][^\'"]*stores?[^\'"]*[\'"]', text):
            imported = match.group(1)
            stores["imported_stores"].extend([s.strip() for s in imported.split(',')])
        
        # Find manual subscriptions
        stores["store_subscriptions"] = re.findall(r'(\w+)\.subscribe\(', text)
        
        # Find auto-subscriptions ($store)
        stores["auto_subscriptions"] = re.findall(r'\$(\w+)', text)
        
        return stores
    
    def _extract_events(self, text: str) -> Dict[str, Any]:
        """Extract event handling and dispatching."""
        return {
            "dispatched_events": re.findall(r'dispatch\([\'"](\w+)[\'"]', text),
            "event_handlers": re.findall(r'on:(\w+)', text),
            "event_forwarding": len(re.findall(r'on:\w+(?:\s*=\s*\{[^}]*\})?', text)),
            "createEventDispatcher": 'createEventDispatcher' in text
        }
    
    def _extract_slots(self, text: str) -> Dict[str, Any]:
        """Extract slot usage."""
        return {
            "default_slots": len(re.findall(r'<slot\s*/?>', text)),
            "named_slots": re.findall(r'<slot\s+name=["\'](\w+)["\']', text),
            "slot_props": len(re.findall(r'<slot[^>]+\s+\w+=["\'][^"\']*["\']', text)) > 0
        }
    
    def _extract_actions(self, text: str) -> List[str]:
        """Extract use:action directives."""
        return re.findall(r'use:(\w+)', text)
    
    def _extract_imports(self, text: str) -> List[Dict[str, str]]:
        """Extract import statements."""
        imports = []
        
        for match in re.finditer(r'import\s+(.+?)\s+from\s+[\'"]([^\'"]+)[\'"]', text):
            what = match.group(1).strip()
            from_where = match.group(2)
            
            imports.append({
                "what": what,
                "from": from_where,
                "is_svelte": 'svelte' in from_where,
                "is_component": '.svelte' in from_where,
                "is_store": 'store' in from_where.lower()
            })
        
        return imports
    
    def _detect_sveltekit_features(self, text: str, file_path: str) -> Dict[str, bool]:
        """Detect SvelteKit-specific features."""
        filename = os.path.basename(file_path)
        
        return {
            "is_route": '+page.svelte' in filename or '+layout.svelte' in filename,
            "is_error_page": '+error.svelte' in filename,
            "is_server_page": '+page.server.' in filename,
            "uses_load_function": 'export const load' in text or 'export async function load' in text,
            "uses_actions": 'export const actions' in text,
            "uses_page_store": '$page' in text,
            "uses_navigation": 'goto(' in text or 'prefetch(' in text,
            "form_actions": '<form' in text and 'method="POST"' in text
        }
    
    def _assess_reactivity(self, findings: Dict[str, Any]) -> float:
        """Assess reactivity usage and patterns."""
        score = 0.5
        
        # Using reactive statements
        if findings.get('reactive_statements', {}).get('has_reactive_statements'):
            score += 0.2
        
        # Using stores appropriately
        stores = findings.get('stores', {})
        if stores.get('auto_subscriptions'):
            score += 0.15
        
        # Not overusing reactivity
        reactive_count = findings.get('reactive_statements', {}).get('count', 0)
        if reactive_count > 0 and reactive_count < 10:
            score += 0.15
        elif reactive_count >= 10:
            score += 0.05  # Too many might indicate complexity
        
        return min(score, 1.0)
    
    def _assess_structure(self, findings: Dict[str, Any]) -> float:
        """Assess component structure and organization."""
        score = 0.5
        
        # Has TypeScript
        if findings.get('scripts', {}).get('has_typescript'):
            score += 0.15
        
        # Props are well-defined
        props = findings.get('props', [])
        if props and all(p.get('has_default') for p in props):
            score += 0.1
        
        # Uses slots for composition
        if findings.get('slots', {}).get('named_slots'):
            score += 0.1
        
        # Moderate file size (scripts)
        scripts = findings.get('scripts', {})
        if scripts.get('instance'):
            lines = len(scripts['instance'].split('\n'))
            if lines < 200:
                score += 0.15
            elif lines < 400:
                score += 0.05
        
        return min(score, 1.0)
    
    def _assess_performance(self, findings: Dict[str, Any]) -> float:
        """Assess performance considerations."""
        score = 0.7  # Svelte is generally performant
        
        # Avoid {@html} directive (can be slow and unsafe)
        markup = findings.get('markup', {})
        if markup.get('html_directive', 0) > 0:
            score -= 0.1
        
        # Too many each blocks might indicate performance issues
        if markup.get('each_blocks', 0) > 10:
            score -= 0.1
        
        # Using key blocks appropriately
        if markup.get('key_blocks', 0) > 0:
            score += 0.1
        
        # Transitions can impact performance
        if markup.get('transition_directives', 0) > 5:
            score -= 0.05
        
        return max(score, 0.3) 