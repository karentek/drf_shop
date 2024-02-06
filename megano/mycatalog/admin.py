from .models import Categories, CategoryImage, Product, ProductImage, Specification, Tag, Review, SaleDate
from django.contrib import admin


class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 1


@admin.register(Categories)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [CategoryImageInline]
    list_display = ('pk', 'title', 'parent_category',)


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1


class SaleDateInline(admin.TabularInline):
    model = SaleDate
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',)
    list_display_links = ('pk', 'name',)
    search_fields = ('name',)


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'value')
    list_display_links = ('pk', 'name',)

    search_fields = ('name', 'value')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'price', 'count', 'date', 'freeDelivery',)
    list_display_links = ('pk', 'title',)
    list_filter = ('freeDelivery', 'tags', 'specifications',)
    search_fields = ('title', 'description', 'fullDescription',)
    filter_horizontal = ('tags', 'specifications',)
    readonly_fields = ('date',)
    inlines = [ProductImageInline, ReviewInline, SaleDateInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'product', 'text', 'rate', 'date',)
    list_display_links = ('pk', 'author',)
    list_filter = ('product', 'rate',)
    search_fields = ('text',)
    readonly_fields = ('date',)

