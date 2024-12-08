from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm
from .models import Post

@login_required
def post_list(request):
    posts = Post.objects.all().order_by('created_date')
    return render(request, 'tg/post_list.html', {'posts': posts})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'tg/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_date = timezone.now()
            post.save()
            messages.success(request, f"Ура! Пост '{post.title}' успешно добавлен! 🌸")
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'tg/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_date = timezone.now()
            post.save()
            messages.success(request, f"Пост '{post.title}' успешно обновлен! ✨")
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'tg/post_edit.html', {'form': form})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        messages.success(request, f"Пост '{post.title}' успешно удален. 🗑️ Спасибо за воспоминания!")
        return redirect('post_list')
    return render(request, 'tg/post_confirm_delete.html', {'post': post})