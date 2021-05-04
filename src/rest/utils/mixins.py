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
            queryset = self._get_queryset_by_filter(**kwargs)
            serializer = self.get_serializer(queryset, many=kwargs.get("many", False))
            return Response(serializer.data)
        except (GetObjectException, FilterException) as ex:
            return Response(data={"detail": str(ex)}, status=status.HTTP_404_NOT_FOUND)

    def _get_queryset_by_filter(self, **kwargs):
        model_name = self.queryset.model._meta.object_name

        many = kwargs.pop("many", False)
        limit = kwargs.pop("limit", None)
        offset = kwargs.pop("offset", None)
        order = kwargs.pop("order", None)
        format = kwargs.pop("format", None)
        max_level = int(kwargs.pop("max_level", 1))
        level = kwargs.pop("level", None)

        # TODO Добавить нормальный парсинг параметров фильтрации
        # TODO в зависимости от уровня вложенности указывать select_related
        queryset = self.queryset
        if not many:
            if not kwargs:
                raise GetObjectException(model_name, "no_filter")
            try:
                queryset = queryset.get(**kwargs)
                return queryset
            except queryset.model.DoesNotExist:
                raise GetObjectException(model_name, "not_found")
            except queryset.model.MultipleObjectsReturned:
                raise GetObjectException(model_name, "many_found")

        if many:
            try:
                if kwargs:
                    queryset = queryset.filter(**kwargs)
                if max_level > 0 and not level:
                    select_related_list = [field.name for field in queryset.model._meta.get_fields() if field.many_to_one]
                    queryset = queryset.select_related(*select_related_list)
                return queryset
            except Exception as ex:
                raise FilterException(model_name, ex)
        return queryset

    def get_serializer_context(self):
        data = {key: self.request.query_params[key] for key in ["max_level", "level"] if key in self.request.query_params}
        data.update({'request': self.request, 'format': self.format_kwarg, 'view': self})
        return data