import re

class css(str):
    def __new__(cls, css_text):
        cleaned_css = cls.remove_comments(css_text)
        media_blocks, cleaned_css = cls.extract_media_blocks(cleaned_css)
        rules = cls.parse_rules(cleaned_css)
        merged = cls.merge_rules(rules)
        optimized = ''.join(f'{selector}{{{cls.clean_properties(props)}}}' for selector, props in merged.items())
        full_css = optimized + ''.join(media_blocks)
        return str.__new__(cls, full_css)

    @staticmethod
    def clean_properties(props):
        parts = []
        for prop in props.split(';'):
            if ':' in prop:
                k, v = prop.split(':', 1)
                parts.append(f'{k.strip()}:{v.strip()}')
        return ';'.join(parts) + ';'


    @staticmethod
    def remove_comments(css):
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        return css.replace("\n", "")

    @staticmethod
    def extract_media_blocks(css):
        media_blocks = []
        pattern = re.compile(r'@media[^{]+\{')
        while True:
            match = pattern.search(css)
            if not match:
                break
            start = match.start()
            brace_count = 0
            i = match.end()
            while i < len(css):
                if css[i] == '{':
                    brace_count += 1
                elif css[i] == '}':
                    if brace_count == 0:
                        break
                    brace_count -= 1
                i += 1
            block = css[start:i+1]
            media_blocks.append(block)
            css = css[:start] + css[i+1:]
        return media_blocks, css

    @staticmethod
    def parse_rules(css):
        pattern = re.compile(r'([^{]+)\{([^}]+)\}')
        rules = pattern.findall(css)
        return [(selector.strip(), properties.strip()) for selector, properties in rules]

    @staticmethod
    def merge_properties(props1, props2):
        props_dict = {}
        for prop in props1.split(';'):
            if ':' in prop:
                k, v = prop.split(':', 1)
                props_dict[k.strip()] = v.strip()
        for prop in props2.split(';'):
            if ':' in prop:
                k, v = prop.split(':', 1)
                props_dict[k.strip()] = v.strip()
        return '; '.join(f'{k}: {v}' for k, v in props_dict.items() if k) + ';'

    @classmethod
    def merge_rules(cls, rules):
        merged = {}
        for selector, props in rules:
            if not props.strip():
                continue
            selectors = [s.strip() for s in selector.split(',')]
            for sel in selectors:
                if sel in merged:
                    merged[sel] = cls.merge_properties(merged[sel], props)
                else:
                    merged[sel] = props
        return merged
