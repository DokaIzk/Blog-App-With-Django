from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from .models import Post, Comment
from django.views.generic import ListView, DetailView
from django.core.paginator import EmptyPage, PageNotAnInteger
from .forms import EmailForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.auth.decorators import login_required


# def login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)

#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request,
#                                 username= cd['username'],
#                                 password= cd['password'])

#             if user is not None:
#                 login(request)

#                 return HttpResponse('Works')
            
#     else:
#         form = LoginForm()

#     return render(request, 'blog/post/login.html', {'form':form})

# class PostList(ListView):
#     queryset = Post.publish.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'

class PostList(ListView):
    template_name = 'blog/post/list.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        tag_slug = self.kwargs.get('tag_slug')
        queryset = Post.publish.all()

        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[tag])

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs.get('tag_slug')

        if tag_slug:
            context['tag'] = get_object_or_404(Tag, slug=tag_slug)

        return context
     
            
class PostDetail(DetailView):
    template_name = 'blog/post/detail.html'
    queryset = Post.publish.all()

    
    def get(self, request, year, month, day, post):
        post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=post, 
                                published__year=year,
                                published__month=month,
                                published__day=day)
        
        comments = post.comments.filter(active=True)

        form = CommentForm()

        posts_tags = post.tags.values_list('id', flat=True)

        similar_posts = self.queryset.filter(tags__in=posts_tags).exclude(id=post.id)

        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published')[:4]
        
        context = {'post':post, 'comments':comments, 'form':form, 'similar_posts':similar_posts}
        return render(request, self.template_name, context)



def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} Recommends You Read {post.title}"
            message = f"Read {post.title} At {post_url}\n\n {cd['name']}'s Comments: {cd['comments']}"

            send_mail(subject, message, 'izk19851999@gmail.com', [cd['receiver_email']])

            sent = True

    else:
        form = EmailForm()

    return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    context = {'post':post, 'form':form, 'comment':comment}

    return render(request, 'blog/post/comment.html', context)