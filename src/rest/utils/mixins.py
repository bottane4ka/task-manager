from rest_framework import status
from rest_framework.response import Response
from rest.utils.exceptions import GetObjectException, FilterException


class CustomFilterModelMixin:

    def retrieve(self, request, *args, **kwargs):
        return self.get_response(**self.get_params())

    def list(self, request, *args, **kwargs):
        return self.get_response(many=True, **self.get_params())

    def get_params(self):
        params = {key: item for key, item in self.request.query_params.items()}
        return params

    def get_response(self, **kwargs):
        try:
            queryset = self.get_queryset_by_filter(**kwargs)
        except (GetObjectException, FilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=kwargs.get("many", False))
        return Response(serializer.data)

    def get_queryset_by_filter(self, **kwargs):
        model_name = self.queryset.model._meta.object_name

        many = kwargs.pop("many", False)
        limit = kwargs.pop("limit", None)
        offset = kwargs.pop("offset", None)
        order = kwargs.pop("order", None)

        # TODO Добавить нормальный парсинг параметров фильтрации
        # TODO в зависимости от уровня вложенности указывать select_related

        if not many:
            if not kwargs:
                raise GetObjectException(model_name, "no_filter")
            try:
                queryset = self.queryset.get(**kwargs)
                return queryset
            except self.queryset.model.DoesNotExist:
                raise GetObjectException(model_name, "not_found")
            except self.queryset.model.MultipleObjectsReturned:
                raise GetObjectException(model_name, "many_found")

        if kwargs and many:
            try:
                queryset = self.queryset.filter(**kwargs)
                return queryset
            except Exception as ex:
                raise FilterException(model_name, ex)
        return self.queryset
