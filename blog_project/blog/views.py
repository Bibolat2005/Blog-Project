from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .forms import PostForm, CommentForm
from .models import Post
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 2 

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get('title')
        author = self.request.GET.get('author')
        posting_time = self.request.GET.get('posting_time')
        
        

        if title:
            queryset = queryset.filter(title__icontains=title)


        if author:
            queryset = queryset.filter(author__username__icontains=author)

        if posting_time:
            queryset = queryset.filter(created_at__gte=posting_time)
 
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if any([self.request.GET.get('title'), self.request.GET.get('author'), self.request.GET.get('posting_time')]):
            context['posts'] = self.get_paginated_queryset()
        else:
            context['posts'] = self.get_queryset() 

        return context

    def get_paginated_queryset(self):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj



def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})


def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.author:
        post.delete()
        return redirect('post_list')
    return HttpResponseForbidden("You are not allowed to delete this post.")


def comment_list(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all() 
    return render(request, 'blog/comment_list.html', {'post': post, 'comments': comments})


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post  
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=pk) 
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment.html', {'form': form, 'post': post})


