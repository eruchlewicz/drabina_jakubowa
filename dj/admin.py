from django.contrib import admin
from .models import *


class RoomAdmin(admin.ModelAdmin):
    ordering = ('floor_number', 'number',)
    list_display = ('number', 'floor_number', 'beds_number', 'has_bathroom')
    list_filter = ('floor_number',)


class PostAdmin(admin.ModelAdmin):
    ordering = ('-date',)
    list_display = ('title', 'date', 'content', 'video')
    list_filter = ('date',)


class PhotoAdmin(admin.ModelAdmin):
    ordering = ('-title',)
    list_display = ('title', 'image')


class CongregationAdmin(admin.ModelAdmin):
    ordering = ('congregation',)
    list_display = ('congregation', 'chief', 'community', 'director', 'main_institution')


class HomeAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'address', 'zip_code', 'city', 'phone_number', 'email_address', 'page_url', 'nip', 'regon')


class PriceAdmin(admin.ModelAdmin):
    ordering = ('service',)
    list_display = ('service', 'price')


class BookingAdmin(admin.ModelAdmin):
    ordering = ('-begin_date',)
    list_display = ('first_name', 'surname', 'phone_number', 'email_address', 'begin_date', 'end_date', 'adults', 'kids',
                    'meals', 'installment', 'is_part_paid', 'full_cost', 'is_paid')
    list_filter = ('begin_date', 'meals')


class FileAdmin(admin.ModelAdmin):
    ordering = ('title',)
    list_display = ('title', 'volunteers', 'coordinators')


admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Congregation, CongregationAdmin)
admin.site.register(Home, HomeAdmin)
admin.site.register(File, FileAdmin)
