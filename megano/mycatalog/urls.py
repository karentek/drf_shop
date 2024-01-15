from django.urls import path

from .views import (
    CategoriesView,
    CatalogView,
    ProductsPopularView,
    ProductsLimitedView,
    SalesView,
    BannersView,
    ProductView,
    ReviewView,
    TagsView,
)

app_name = "mycatalog"

urlpatterns = [
    path("categories", CategoriesView.as_view(), name='categories'),
    path("catalog", CatalogView.as_view(), name='catalog'),
    path("products/popular", ProductsPopularView.as_view(), name='popular'),
    path("products/limited", ProductsLimitedView.as_view(), name='limited'),
    path("sales", SalesView.as_view(), name='sales'),
    path("banners/", BannersView.as_view(), name='banners'),
    path("product/<int:id>", ProductView.as_view(), name='product'),
    path("product/<int:id>/reviews", ReviewView.as_view(), name='reviews'),
    path("tags", TagsView.as_view(), name='tags')

]