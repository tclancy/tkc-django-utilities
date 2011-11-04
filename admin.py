from django.conf import settings
from django.contrib import admin


class NameAndSlugAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ('name',)}


class TinyMCEAdmin(admin.ModelAdmin):
	class Media:
		js = ['%sjs/tiny_mce/tiny_mce.js' % settings.MEDIA_URL,
			  '%sjs/tinymce_setup.js' % settings.MEDIA_URL,]