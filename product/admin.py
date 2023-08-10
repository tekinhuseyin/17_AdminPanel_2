from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from .models import *
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from import_export import resources
from import_export.admin import ImportExportModelAdmin

admin.site.site_title = 'Clarusway Title' # <title>
admin.site.site_header = 'Clarusway Header' # Page Header
admin.site.index_title = 'Clarusway Index Page' # Index SubHeader


# ------------------------------
# Category
# ------------------------------
admin.site.register(Category)


# ------------------------------
# Product
# ------------------------------
class ReviewInline(admin.TabularInline):
    model = Review # ForeignKey ModelName
    extra = 1 # Yeni eklemek için kaç tane alan.
    classes = ['collapse']

# Import-Export ModelResource:
class ProductResource(resources.ModelResource):
    class Meta:
        model = Product


# class ProductAdmin(ModelAdmin):
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    # Tablo sutunları (model field names)
    list_display = ['id', 'name', 'is_in_stock', 'create_date', 'update_date']
    # Tablo üzerinde güncelleyebilme:
    list_editable = ['is_in_stock']
    # Kayda gitmek için linkleme:
    list_display_links = ['id', 'name']
    # Filtreleme (arama değil):
    list_filter = [('name', DropdownFilter), 'is_in_stock', ('create_date', DateRangeFilter), ('update_date', DateTimeRangeFilter)]
    # Arama:
    search_fields = ['id', 'name']
    # Arama bilgilendirme yazısı: 
    search_help_text = 'Arama yapmak için burayı kullanınız.'
    # Default Sıralama:
    ordering = ['id'] # 'id' -> ASC, '-id' -> DESC
    # Sayfa başına kayıt sayısı:
    list_per_page = 20
    # Tümünü göster yaparken max kayıt sayısı:
    list_max_show_all = 200
    # Tarihe göre filtreleme başlığı:
    date_hierarchy = 'create_date' # Tarih field olmak zorunda.
    # Otomatik kaıyıt oluştur:
    prepopulated_fields = {'slug' : ['name']}
    # Resim gösterme read_only olarak çağır:
    readonly_fields = ["view_image"]
    # Form liste görüntüleme:
    fields = (
        ('name', 'is_in_stock'),
        ('image', 'view_image'),
        ('slug'),
        ('categories'),
        ('description'),
    )
    # İlişkili tablo (many2many) nasıl görünsün:
    filter_horizontal = ['categories']
    # filter_vertical = ['categories']
    '''
    # Detaylı form liste görüntüleme:
    fieldsets = (
        ('General Settings', {
            # "classes": ['wide'],
            "fields": (
                ('name', 'is_in_stock'),
                ('slug'),
            )
        }),
        ('Optional Settings', {
            "classes": ['collapse'],
            "fields": (
                ('description'),
            ),
            'description': "You can use this section for optionals settings"
        }),
    )
    '''
    inlines = [ReviewInline]

    def set_stock_in(self, request, queryset):
        count = queryset.update(is_in_stock=True)
        self.message_user(request, f'{count} adet "Stokta Var" olarak işaretlendi.')

    def set_stock_out(self, request, queryset):
        count = queryset.update(is_in_stock=False)
        self.message_user(request, f'{count} adet "Stokta Yok" olarak işaretlendi.')

    actions = ('set_stock_in', 'set_stock_out')
    set_stock_in.short_description = 'İşaretli ürünleri stoğa ekle'
    set_stock_out.short_description = 'İşaretli ürünleri stoktan çıkar'

    def added_days_ago(self, object):
        from django.utils import timezone
        different = timezone.now() - object.create_date
        return different.days
    
    # list_display = ['id', 'name', 'is_in_stock', 'create_date', 'update_date', 'added_days_ago']
    added_days_ago.short_description = 'Days'
    list_display += ['added_days_ago']

    # Kaçtane yorum var:
    def how_many_reviews(self, object):
        count = object.reviews.count()
        return count
    
    how_many_reviews.short_description = 'Reviews'
    list_display += ['how_many_reviews']

    # Listede küçük resim göster:
    def view_image_in_list(self, obj):
        from django.utils.safestring import mark_safe
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} style="height:30px; width:30px;"></img>')
        return '-*-'

    view_image_in_list.short_description = 'Image'
    list_display = ['view_image_in_list'] + list_display

admin.site.register(Product, ProductAdmin)


# ------------------------------
# Review
# ------------------------------
class ReviewAdmin(ModelAdmin):
    list_display = ("__str__", 'created_date')
    raw_id_fields = ('product',)
    list_filter = [('product', RelatedDropdownFilter)]


admin.site.register(Review, ReviewAdmin)