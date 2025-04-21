from django import forms
from shop.models.product import ProductReview

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={'class': 'form-select mb-3', 'aria-label': 'Rating'}
            ),
            'comment': forms.Textarea(
                attrs={
                    'placeholder': 'Write your review here...',
                    'class': 'form-control mb-3',
                    'rows': 4,
                    'style': 'resize: none;'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # เพิ่มการตั้งค่า CSS ให้กับฟิลด์
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})