from beckett.finance.models import *
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib import admin

class ZipcodeAdmin(OSMGeoAdmin):
    search_fields = ('code',)
class DonationAdmin(admin.ModelAdmin):
    date_hierarchy = ('mtime')
    list_filter = ('approved', 'operation')
    search_fields = ('ceo',)
    ordering = ('approved', 'mtime')
    list_display = ('ceo', 'candidate_name', 'donation_amount', 'mtime', 'approved', 'operation',)
class DonorAdmin(admin.ModelAdmin):
    date_hierarchy = ('mtime')
    list_filter = ('approved', 'operation')
    search_fields = ('ceo',)
    ordering = ('approved', 'mtime')
    list_display = ('ceo',  'mtime', 'approved', 'operation',)
admin.site.register(Ceo)
admin.site.register(Zip, ZipcodeAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(Donor, DonorAdmin)

