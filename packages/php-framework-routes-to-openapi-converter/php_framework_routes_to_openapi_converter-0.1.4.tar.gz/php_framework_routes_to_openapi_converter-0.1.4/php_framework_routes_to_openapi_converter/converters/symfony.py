"""Symfony framework route converter."""
from typing import Dict, List, Any, Iterable
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter
from ..models import OpenAPIPathItem


class SymfonyConverter(RouteConverter):
    """Symfony framework route converter."""
    
    def _path_items_generator(self, routes: Iterable) -> Iterable[OpenAPIPathItem]:
        """Generate path items from Symfony routes."""
        for route_name, route_data in routes.items():
            route_data["name"] = route_name

            path = self._get_path(route_data)
            if not path:
                continue
                
            methods = self._get_methods(route_data)
            summary = self._get_summary(route_data)
            tags = self._get_tags(route_data)
            
            yield OpenAPIPathItem(
                path=path,
                methods=methods,
                summary=summary,
                tags=tags
            )
    
    def _get_path(self, route: Dict[str, Any]) -> str:
        return route.get("path", "")
    
    def _get_methods(self, route: Dict[str, Any]) -> List[str]:
        return [method.lower() for method in route.get("method", "").split("|") if method.strip()]
    
    def _get_summary(self, route: Dict[str, Any]) -> str:
        return route.get("name", "")
    
    def _get_tags(self, route: Dict[str, Any]) -> List[str]:
        return [route.get("name", "")]
