from django.contrib import admin
from foodtruck.models import Hood, Truck

class TagInline(admin.StackedInline):
  model = Hood.tags.through

class HoodAdmin(admin.ModelAdmin):
  inlines = [TagInline]
  exclude = ('tags',)
  extra = 3

class TruckAdmin(admin.ModelAdmin):
  list_display = ('id','name', 'description','truck_url','id_str','real_name')

admin.site.register(Hood, HoodAdmin)
admin.site.register(Truck, TruckAdmin)