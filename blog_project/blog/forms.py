from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class PostSearchForm(forms.Form):
    title = forms.CharField(required=False, label='Title')
    author = forms.CharField(required=False, label='Author')
    created_after = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Posting_time')
