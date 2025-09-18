from django.contrib import admin
from django.utils.html import format_html
from .models import Socket, Bag, SortedBag, SortingPerson, BagType, BagSubtype


@admin.register(BagType)
class BagTypeAdmin(admin.ModelAdmin):
    list_display = ('socket', 'name', 'code', 'order', 'bag_source', 'parameter', 'color', 'is_active', 'created_at')
    list_filter = ('bag_source', 'is_active', 'created_at', 'socket')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at',)
    actions = ['change_source_to_in', 'change_source_to_out']
    
    def change_source_to_in(self, request, queryset):
        """Change selected BagType objects' bag_source to IN"""
        updated = queryset.update(bag_source='IN')
        self.message_user(
            request,
            f'Pomyślnie zmieniono źródło {updated} typów worków na WEJŚCIE.'
        )
    change_source_to_in.short_description = "Zmień źródło worka na WEJŚCIE"
    
    def change_source_to_out(self, request, queryset):
        """Change selected BagType objects' bag_source to OUT"""
        updated = queryset.update(bag_source='OUT')
        self.message_user(
            request,
            f'Pomyślnie zmieniono źródło {updated} typów worków na WYJŚCIE.'
        )
    change_source_to_out.short_description = "Zmień źródło worka na WYJŚCIE"


@admin.register(BagSubtype)
class BagSubtypeAdmin(admin.ModelAdmin):
    list_display = ('bag_type', 'name', 'code', 'order', 'color', 'is_active', 'created_at')
    list_filter = ('bag_type', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at',)
    raw_id_fields = ('bag_type',)
    
    fieldsets = (
        ('Informacje Podstawowe', {
            'fields': ('bag_type', 'name', 'code', 'order')
        }),
        ('Wyświetlanie', {
            'fields': ('color', 'description', 'is_active')
        }),
        ('Znaczniki Czasu', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Socket)
class SocketAdmin(admin.ModelAdmin):
    list_display = ('socket_id', 'socket_name', 'color_box', 'location', 'is_active', 'order', 'user_count')
    list_filter = ('is_active', 'users')
    search_fields = ('socket_id', 'socket_name', 'location')
    filter_horizontal = ('users',)

    def color_box(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {};"></div>',
            obj.socket_color
        )

    def user_count(self, obj):
        return obj.users.count()

    color_box.short_description = "Kolor"
    user_count.short_description = "Liczba użytkowników"


@admin.register(SortingPerson)
class SortingPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'person_id', 'person_color', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'person_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Bag)
class BagAdmin(admin.ModelAdmin):
    list_display = ('bag_id', 'socket', 'bag_type', 'bag_subtype', 'quality_grade', 'item_count', 'weight_kg', 'extra', 'is_processed', 'sorting_person', 'received_at')
    list_filter = ('bag_type', 'bag_subtype', 'quality_grade', 'extra', 'is_processed', 'received_at', 'socket')
    search_fields = ('bag_id', 'notes')
    readonly_fields = ('received_at', 'processed_at', 'updated_at')
    raw_id_fields = ('socket', 'sorting_person', 'bag_type', 'bag_subtype')
    actions = ['mark_as_extra', 'mark_as_standard']
    
    fieldsets = (
        ('Informacje Podstawowe', {
            'fields': ('bag_id', 'socket', 'bag_type', 'bag_subtype', 'quality_grade')
        }),
        ('Szczegóły Zawartości', {
            'fields': ('item_count', 'weight_kg', 'extra', 'notes')
        }),
        ('Przetwarzanie', {
            'fields': ('sorting_person', 'is_processed')
        }),
        ('Znaczniki Czasu', {
            'fields': ('received_at', 'processed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def mark_as_extra(self, request, queryset):
        """Mark selected bags as extra"""
        updated = queryset.update(extra=True)
        self.message_user(
            request,
            f'Pomyślnie oznaczono {updated} worków jako Dodatkowe.'
        )
    mark_as_extra.short_description = "Oznacz wybrane worki jako Dodatkowe"
    
    def mark_as_standard(self, request, queryset):
        """Mark selected bags as standard (not extra)"""
        updated = queryset.update(extra=False)
        self.message_user(
            request,
            f'Pomyślnie oznaczono {updated} worków jako Standardowe (nie dodatkowe).'
        )
    mark_as_standard.short_description = "Oznacz wybrane worki jako Standardowe"



@admin.register(SortedBag)
class SortedBagAdmin(admin.ModelAdmin):
    list_display = ('original_bag', 'destination', 'status', 'final_quality_check', 'tracking_number', 'created_at', 'shipped_at')
    list_filter = ('destination', 'status', 'final_quality_check', 'created_at')
    search_fields = ('original_bag__bag_id', 'tracking_number', 'packaging_notes')
    readonly_fields = ('created_at', 'updated_at', 'shipped_at', 'delivered_at')
    raw_id_fields = ('original_bag',)
    
    fieldsets = (
        ('Informacje Podstawowe', {
            'fields': ('original_bag', 'destination', 'status')
        }),
        ('Jakość i Pakowanie', {
            'fields': ('final_quality_check', 'packaging_notes')
        }),
        ('Wysyłka', {
            'fields': ('tracking_number',)
        }),
        ('Znaczniki Czasu', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
