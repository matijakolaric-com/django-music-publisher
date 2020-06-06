from django.contrib import admin, messages
from django.db import models
from django import forms
from django.conf import settings

from .models import WorkAcknowledgement, SOCIETY_DICT


class RoyaltyCalculation(models.Model):
    class Meta:
        managed = False
    in_file = models.FileField(verbose_name='Incoming statement')
    out_file = models.FileField(blank=True, null=True)


class RoyaltyCalculationForm(forms.ModelForm):
    class Meta:
        fields = ('in_file', )

    def get_id_sources():
        yield None, settings.PUBLISHER_NAME
        codes = WorkAcknowledgement.objects.values_list('society_code', flat=True)
        codes = [(code, SOCIETY_DICT.get(code, '') ) for code in codes]
        codes.sort(key=lambda code: code[1])
        for code in codes:
            yield code

    def get_right_types():
        yield 'p', 'Performance'
        yield 'm', 'Mechanical'
        yield 's', 'Sync'

    SPLITS = [
        ('cw', 'Controlled writers only'),
        ('cwp', 'Controlled writers and {}'.format(settings.PUBLISHER_NAME)),
    ]

    work_id_column = forms.ChoiceField(choices=[], label='Work ID', required=False)
    work_id_source = forms.ChoiceField(choices=get_id_sources, required=False)
    amount_column = forms.ChoiceField(choices=[], label='Amount', required=False)
    right_type_column = forms.ChoiceField(choices=get_right_types, label='Right Type')
    split = forms.ChoiceField(choices=SPLITS)
    apply_fees = forms.BooleanField(required=False)
    default_fee = forms.DecimalField(max_digits=5, decimal_places=2, initial=0)

    def clean(self):
        print('cleaning_form')
        super().clean()

    def save(self, commit=True):
        print('saving form')
        return super().save(commit)


@admin.register(RoyaltyCalculation)
class RoyaltyCalculationAdmin(admin.ModelAdmin):

    form = RoyaltyCalculationForm
    change_form_template = 'admin/royalty_calculation_form.html'

    fieldsets = (
        ('Incoming statement', {
            'fields': (
                'in_file',
            ),
        }),
        ('Columns', {
            'fields': (
                ('work_id_column', 'work_id_source'),
                'right_type_column',
                'amount_column'
            ),
        }),
        ('Algorithm', {
            'fields': (
                ('split', 'apply_fees'),
                'default_fee',
            ),
        }),
    )

    save_as = False

    def add_view(self, request, form_url='', extra_context=None):
        response = super().add_view(request, form_url='', extra_context=None)
        print(response)
        return response

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    def save_form(self, request, form, change):
        # returns object
        print('save form')
        r = super().save_form(request, form, change)
        print(type(r))
        return r

    def save_model(self, request, obj, form, change):
        print('save_model')
        pass
