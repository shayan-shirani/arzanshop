import pytest

from apps.shop.tests.factories import (
    ParentCategoryFactory,
    CategoryFactory,
)

@pytest.mark.django_db()
def test_create_category():
    root_category = ParentCategoryFactory()
    category = CategoryFactory(parent=root_category)
    assert category.parent == root_category
    assert root_category.children.count() == 1
    assert root_category.name
    assert category.name