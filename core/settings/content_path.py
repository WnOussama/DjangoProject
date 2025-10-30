
class UserContentPath:
    def __init__(self, subfolder, include_date=False, date_format='%Y/%m/%d'):
        self.subfolder = subfolder
        self.include_date = include_date
        self.date_format = date_format
    
    def __call__(self, instance, filename):
        from datetime import datetime
        
        user = None
        if hasattr(instance, 'user'):
            user = instance.user
        elif hasattr(instance, 'product') and hasattr(instance.product, 'user'):
            user = instance.product.user
        elif hasattr(instance, 'author'):
            user = instance.author.user if hasattr(instance.author, 'user') else None
            
        
        username = user.username if user else 'unknown'
        
        path = f"{username}/content/"
        
        if self.subfolder:
            subfolder = self.subfolder
            if not subfolder.endswith('/'):
                subfolder = f"{subfolder}/"
            path = f"{path}{subfolder}"
        
        if self.include_date:
            date_path = datetime.now().strftime(self.date_format).replace('/', '-')
            if not date_path.endswith('/'):
                date_path = f"{date_path}/"
            path = f"{path}{date_path}"
            
        return f"{path}{filename}"
    
    def __eq__(self, other):
        if isinstance(other, UserContentPath):
            return (
                self.subfolder == other.subfolder and
                self.include_date == other.include_date and
                self.date_format == other.date_format
            )
        return False
    
    def deconstruct(self):
        path = 'core.settings.content_path.UserContentPath'
        args = [self.subfolder]
        kwargs = {}
        
        if self.include_date:
            kwargs['include_date'] = self.include_date
        
        if self.date_format != '%Y/%m/%d':
            kwargs['date_format'] = self.date_format
        
        return path, args, kwargs