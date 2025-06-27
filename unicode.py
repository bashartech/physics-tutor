"""
Helper functions to convert LaTeX-style math to Unicode format
"""

def format_physics_response(text: str) -> str:
    """
    Convert LaTeX-style mathematical notation to Unicode format
    """
    replacements = {
        # Fractions
        r'\frac{dv}{dt}': 'dv/dt',
        r'\frac{d}{dt}': 'd/dt',
        r'\frac{1}{2}': '½',
        r'\frac{1}{3}': '⅓',
        r'\frac{1}{4}': '¼',
        r'\frac{3}{4}': '¾',
        
        # Mathematical symbols
        r'\int': '∫',
        r'\partial': '∂',
        r'\approx': '≈',
        r'\leq': '≤',
        r'\geq': '≥',
        r'\infty': '∞',
        r'\pi': 'π',
        r'\theta': 'θ',
        r'\alpha': 'α',
        r'\beta': 'β',
        r'\gamma': 'γ',
        r'\delta': 'δ',
        r'\omega': 'ω',
        
        # Functions
        r'\ln': 'ln',
        r'\log': 'log',
        r'\sin': 'sin',
        r'\cos': 'cos',
        r'\tan': 'tan',
        
        # Remove LaTeX math delimiters
        r'\(': '',
        r'\)': '',
        r'$$': '',
        
        # Subscripts (basic ones)
        '_0': '₀',
        '_1': '₁',
        '_2': '₂',
        '_3': '₃',
        '_4': '₄',
        '_5': '₅',
        
        # Superscripts (basic ones)
        '^2': '²',
        '^3': '³',
        '^{-1}': '⁻¹',
    }
    
    result = text
    for latex, unicode_char in replacements.items():
        result = result.replace(latex, unicode_char)
    
    return result

# Example usage for testing
if __name__ == "__main__":
    sample_text = r"""
    From Newton's 2nd law: $$m\frac{dv}{dt} = mg - kv$$
    The solution is: $$v(t) = \frac{mg}{k}(1 - e^{-kt/m})$$
    """
    
    formatted = format_physics_response(sample_text)
    print("Original:", sample_text)
    print("Formatted:", formatted)
