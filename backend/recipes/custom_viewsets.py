from rest_framework import mixins, viewsets


class BaseModelViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin):
    pass


class RecipeModelViewSet(BaseModelViewSet,
                         mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.CreateModelMixin):
    pass
