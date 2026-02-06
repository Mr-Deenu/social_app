from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "image", "video", "is_reel"]

    def clean(self):
        cleaned = super().clean()
        image = cleaned.get("image")
        video = cleaned.get("video")
        is_reel = cleaned.get("is_reel")

        
        if is_reel and not video:
            raise forms.ValidationError("Reel ke liye video upload karna zaroori hai.")

       
        if video and not is_reel:
            cleaned["is_reel"] = True

        if image and video:
            raise forms.ValidationError("Ek post me image ya video me se ek hi choose karo.")

        return cleaned
