from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin, EditorsConceptAdmin
from avocado.fields.models import Field
from avocado.fields.forms import FieldAdminForm

__all__ = ('FieldAdmin', 'EditorsFieldAdmin')

class FieldAdmin(ConceptAdmin):
    form = FieldAdminForm
    list_display = ('name', 'is_public', 'model_name', 'enable_choices')
    list_filter = ('is_public', 'model_name')
    list_editable = ('is_public', 'enable_choices')


class EditorsFieldAdmin(EditorsConceptAdmin):
    list_display = ('name', 'is_public')
    list_filter = ('is_public',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'keywords', 'is_public')
        }),
    )


admin.site.register(Field, FieldAdmin)
