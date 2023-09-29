from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Администрирование пользователей."""

    model = CustomUser
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_subcribed'
    ]
    list_filter = ['is_staff', 'is_superuser', 'email']
    search_fields = ['username', 'email']
    readonly_fields = ('last_login',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser',
        )}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    @admin.display(description='Подписчики')
    def is_subcribed(self, obj: Subscription) -> bool:
        """Счетчик подписчиков."""
        count = obj.subscribing.count()
        if count > 0:
            return f'{count} ❤️'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Администрирование подписок."""

    list_display = ['user', 'author', 'pub_date']
    list_filter = ['author', 'pub_date']
    search_fields = ['user__username', 'author__username']
