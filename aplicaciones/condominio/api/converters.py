
class ValidaAnios:
    regex = r'([2-9]\d{3,}|[3-9]\d{2}|199\d)'
    
    def to_python(self, value):
        return value
            
    def to_url(sel, value):
        return value