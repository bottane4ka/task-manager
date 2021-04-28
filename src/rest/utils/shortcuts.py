from django.http import (
    Http404, )
from django.shortcuts import _get_queryset


def get_object_or_404(klass, *args, **kwargs):
    """
    Use get() to return an object, or raise a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    if not kwargs:
        raise Http404("Не указаны параметры фильтрации")
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404(f"Объект {queryset.model._meta.object_name} не найден")
    except queryset.model.MultipleObjectsReturned:
        raise Http404(f"Найдено больше одного объекта {queryset.model._meta.object_name}")