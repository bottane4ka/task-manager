from rest_framework import viewsets, mixins

from manager.models import TaskStatusModel
from manager.serializer import TaskStatusSerializer
from rest_framework import decorators
from rest_framework.response import Response
from rest.utils.shortcuts import get_object_or_404


class TaskStatusViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = TaskStatusModel.objects.all()
    serializer_class = TaskStatusSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception as ex:
            return Response(data={"detail": str(ex)}, status=404)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {key: item for key, item in self.request.query_params.items()}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj