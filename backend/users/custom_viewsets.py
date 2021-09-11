from rest_framework import mixins, viewsets


class BaseModelViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    pass
