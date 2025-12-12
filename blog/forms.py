from django import forms
from .models import Profile
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']  # title не обязателен (можно позже добавить)
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Напишите что-нибудь...',
                'style': 'width: 100%; font-size: 16px;'
            }),
        }
        labels = {
            'content': ''
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о себе...'}),
        }