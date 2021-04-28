from collections import OrderedDict, namedtuple
from rest_framework.settings import api_settings
from rest_framework.routers import SimpleRouter, DynamicRoute

Route = namedtuple('Route', ['url', 'mapping', 'name', 'detail', 'initkwargs'])


class CustomRouter(SimpleRouter):

    routes = [
        # List route.
        Route(
            url=r'^{prefix}/list/$',
            mapping={
                'get': 'list'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        )
    ]

    def __init__(self, *args, **kwargs):
        if 'root_renderers' in kwargs:
            self.root_renderers = kwargs.pop('root_renderers')
        else:
            self.root_renderers = list(api_settings.DEFAULT_RENDERER_CLASSES)
        super().__init__(*args, **kwargs)

