import pytest

from apps.shop.serializers import CategorySerializer

from apps.shop.tests.factories import (
    ParentCategoryFactory,
    CategoryFactory,
)


@pytest.mark.django_db
def test_category_create_serializer():
    root_category = ParentCategoryFactory()
    child_category = CategoryFactory(parent=root_category)
    convert_to_dict = {
        'parent': {
            'name':child_category.parent.name
        },
        'name':child_category.name,
    }
    serializer = CategorySerializer(data=convert_to_dict)
    assert serializer.is_valid()
    category = serializer.save()
    assert child_category.parent.name == convert_to_dict['parent']['name']
    assert category.name == convert_to_dict['name']