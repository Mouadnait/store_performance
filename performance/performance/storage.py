"""
Custom storage backend to filter duplicate jazzmin admin static files.
"""
from django.contrib.staticfiles.storage import StaticFilesStorage


class FilteredStaticFilesStorage(StaticFilesStorage):
    """Storage that ignores jazzmin's duplicate admin files."""
    
    IGNORED_PATTERNS = {
        'admin/js/cancel.js',
        'admin/js/popup_response.js',
    }
    
    def post_process(self, paths, **options):
        """Filter out duplicate files before processing."""
        # Remove jazzmin duplicates, keep Django's originals
        filtered_paths = {
            path: storage 
            for path, storage in paths.items() 
            if path not in self.IGNORED_PATTERNS or 'django/contrib/admin' in str(storage.location)
        }
        return super().post_process(filtered_paths, **options)
