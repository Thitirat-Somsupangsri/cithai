from django import forms

from ..models import SongParameters


class SongParametersInlineForm(forms.ModelForm):
    class Meta:
        model = SongParameters
        fields = ('title', 'occasion', 'genre', 'voice_type', 'custom_text')

    def clean(self):
        cleaned = super().clean()
        if not self.cleaned_data.get('DELETE', False):
            required_fields = ['title', 'occasion', 'genre', 'voice_type']
            for field in required_fields:
                if not cleaned.get(field):
                    self.add_error(field, f'{field.replace("_", " ").title()} is required.')
        return cleaned
