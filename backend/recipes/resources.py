  
from import_export import resources

from .models import Ingredient


class IngredientResource(resources.ModelResource):
    """
    Класс для загрузки ингредиентов через .json
    с помощью import_export
    """

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit',
        ]
