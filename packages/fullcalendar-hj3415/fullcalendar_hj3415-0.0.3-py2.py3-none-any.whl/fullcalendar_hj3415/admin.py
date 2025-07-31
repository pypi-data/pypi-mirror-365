from django.contrib import admin

# ===================================== Calendar ================================
from .models import Calendar, Event, EventType


class CalendarAdmin(admin.ModelAdmin):
    list_display = ('modal_title', 'activate')

class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_of_event', 'calendar', 'event_type')


admin.site.register(Calendar, CalendarAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)