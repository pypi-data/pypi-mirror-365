"""Laravel framework route converter."""
from typing import Dict, List, Any, Iterable
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter
from ..models import OpenAPIPathItem


class LaravelConverter(RouteConverter):
    """Laravel framework route converter."""
    
    def _path_items_generator(self, routes: Iterable) -> Iterable[OpenAPIPathItem]:
        """Generate path items from Laravel routes."""
        for route in routes:
            path = self._get_path(route)
            if not path:
                continue

            methods = self._get_methods(route)
            summary = self._get_summary(route)
            tags = self._get_tags(route)
            
            yield OpenAPIPathItem(
                path=path,
                methods=methods,
                summary=summary,
                tags=tags
            )
    
    def _get_path(self, route: Dict[str, Any]) -> str:
        return route.get("uri", "")
    
    def _get_methods(self, route: Dict[str, Any]) -> List[str]:
        """
        >>> LaravelConverter().extract_methods({"method": "GET"})
        ['get']
        
        >>> LaravelConverter().extract_methods({"method": "GET|HEAD"})
        ['get', 'head']
        
        >>> LaravelConverter().extract_methods({"method": "HEAD"})
        ['head']
        
        >>> LaravelConverter().extract_methods({"method": "POST"})
        ['post']
        """
        
        method = route.get("method", "")
        if method:
            return [m.strip().lower() for m in method.split("|") if m.strip()]
        return []
    
    def _get_summary(self, route: Dict[str, Any]) -> str:
        return route.get("name") or route.get("action") or "Laravel Route"
    
    def _get_tags(self, route: Dict[str, Any]) -> List[str]:
        action = route.get("action")
        return [action] if action else [] 