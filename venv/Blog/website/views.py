from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.generic import CreateView
from django.contrib.auth import views as auth_views
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import authenticate, login, logout
from .models import Custom_Users, registered_users, journalist_users, article,comment
from .forms import UsersSignupForm, JournalistSignupForm, LoginForm, ArticleForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic.edit import UpdateView, DeleteView
from django.views.decorators.http import require_POST
from .decorators import ruser_required, journalist_required
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm
from taggit.models import Tag
from django.db.models import Q
import json

Dislike_LIMIT = 50

class UserSignUpView(CreateView):
    model = Custom_Users
    form_class = UsersSignupForm
    template_name = 'usersignup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'registered_user'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('login')

    
class JournalistSignUpView(CreateView):
    model = Custom_Users
    form_class = JournalistSignupForm
    template_name = 'journalistsignup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'journalist'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        if user.is_approved:
            login(self.request, user)
        else:
            return HttpResponse('thank you for applying your application is under review')

def get_top_articles():
    last_month = datetime.now() - timedelta(days=30)
    articles = article.objects.filter(created_at__gte=last_month, admin_approved=True).order_by('-like_count')[:10]
    tags = Tag.objects.all()
    return articles, tags

class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'login.html'

     


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        popular, tags = get_top_articles()
        context['popular'] = popular
        context['tags'] = tags
        
        articles = article.objects.filter(admin_approved=True).order_by('-created_at')
        paginator = Paginator(articles, 6)
        page_number = self.request.GET.get('page')
        paginated_articles = paginator.get_page(page_number)
        
        context['articles'] = paginated_articles
        return context
    



    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_registered_user:
                return reverse('login')
            elif user.is_journalist_user:
                return reverse('journalist-home')
        else:
            return reverse('login')
        
@login_required
@ruser_required
def user_home(request):
    articles = article.objects.filter(admin_approved=True)
    tagged = article.tags.most_common()[:4]
    tags = Tag.objects.all() 
    context = {
        'articles': articles,
        'tags': tags,
  
        
    }
    return render(request, 'user_home.html', context)

@login_required
@journalist_required
def journalist_home(request):
    articles = article.objects.filter(journalist_users=request.user.journalist_user, admin_approved=True)
    pending = article.objects.filter(journalist_users=request.user.journalist_user , admin_approved=False)
    for i in articles:
        total_count = i.like_count + i.dislike_count
        if total_count > 0:
            i.like_ratio = round(i.like_count / total_count, 2)
        else:
            i.like_ratio = None
    tags = Tag.objects.all() 

    context = {
        'articles': articles,
        'tags': tags,
        'pending': pending,
    }
    return render(request, 'journalist_home.html', context)

@login_required
@journalist_required
def create_article(request):
    tags = Tag.objects.all() 
    if request.method == 'POST':
        form = ArticleForm(request.POST,request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist_users = request.user.journalist_user
            article.save()
            form.save_m2m()
            if article.admin_approved:
                messages.success(request, f'Your article "{article.title}" has been successfully submitted.')
            else:
                messages.success(request, f'Your article "{article.title}" is under review by an admin.')
            return redirect('journalist-home')
    else:
        form = ArticleForm()
    return render(request, 'create_article.html', {'form': form, 'tags':tags})



class ArticleUpdateView(UpdateView):
    model = article
    form_class = ArticleForm
    template_name = 'update_article.html'
    
    def get_queryset(self):
        return self.model.objects.filter(journalist_users=self.request.user.journalist_user)

    def get_success_url(self):
        messages.success(self.request, f'Your article "{self.object.title}" has been successfully updated.')
        return reverse('journalist-home')
    def form_valid(self, form):
        form.instance.admin_approved = False  
        return super().form_valid(form)




def request_delete(request, pk):
    article_instance = get_object_or_404(article, pk=pk)

    if request.method == 'POST':
        # If the confirmation form is submitted, set admin_approved to False
        article_instance.admin_approved = False
        article_instance.save()

        messages.success(request, f'Your article "{article_instance.title}" has been successfully requested for deletion.')
        return redirect(reverse('journalist-home'))
    else:
        # Render the confirmation template
        return render(request, 'confirm_delete.html', {'article': article_instance})


@login_required
def like_view(request, pk):
    article_id = request.POST.get('article_id')
    the_article = get_object_or_404(article, id=request.POST.get('article_id'))
    user = request.user

    if user in the_article.likes.all():
        the_article.likes.remove(user)
        the_article.like_count -= 1
        print("Like removed")
    elif user in the_article.dislikes.all():
        the_article.dislikes.remove(user)
        the_article.likes.add(user)
        the_article.dislike_count -= 1
        the_article.like_count += 1
        print("Like added")
    else:
        the_article.likes.add(user)
        the_article.like_count += 1

        print("Like added")


    the_article.save()

    return JsonResponse({'result1': the_article.like_count, 'result2': the_article.dislike_count})

@login_required
def dislike_view(request, pk):
    article_id = request.POST.get('article_id')
    the_article = get_object_or_404(article, id=request.POST.get('article_id'))
    user = request.user

    if user in the_article.likes.all():
        the_article.likes.remove(user)
        the_article.dislikes.add(user)
        the_article.like_count -= 1
        the_article.dislike_count += 1
        print("Dislike added")
    elif user in the_article.dislikes.all():
        the_article.dislikes.remove(user)
        the_article.dislike_count -= 1
        print("Dislike removed")
    else:
        the_article.dislikes.add(user)
        the_article.dislike_count += 1
        print("Dislike added")

    if the_article.dislike_count >= Dislike_LIMIT:
        the_article.delete()
        return redirect('user_home')    
    the_article.save()

    return JsonResponse({'result1': the_article.like_count, 'result2': the_article.dislike_count})

def article_view( request, slug):
    article_instance = get_object_or_404(article, slug = slug)
    total_likes= article_instance.total_likes()
    popular = article.objects.filter(admin_approved=True).order_by('-created_at')[:10]
    tags = Tag.objects.all() 
    login_form = LoginForm()
    comment_form = CommentForm()
    comments = comment.objects.filter(article=article_instance)
    context = {
        'article': article_instance, 
        'total_likes':total_likes,
        'tags':  tags,
        'login_form': login_form,
        'comment_form': comment_form,
        'comments': comments,
        'popular': popular
    }
    return render(request, 'article_view.html', context)


@login_required
def add_comment_ajax(request, slug):
    article_instance = get_object_or_404(article, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article_instance
            comment.name = request.user.username
            comment.save()
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'name': comment.name,
                    'body': comment.body,
                }
            })
    return JsonResponse({'status': 'error'})

def tagged_articles(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    articles = article.objects.filter(tags=tag, admin_approved=True)
    tags = Tag.objects.all()

    paginator = Paginator(articles, 5) 
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)


    context = {
        'tag': tag,
        'articles': articles,
        'tags': tags,
    }
    return render(request, 'tagged_articles.html', context)

def top_articles(request):
    from datetime import datetime, timedelta
    last_month = datetime.now() - timedelta(days=30)
    articles = article.objects.filter(created_at__gte=last_month, admin_approved=True).order_by('-like_count')[:10]
    tags = Tag.objects.all() 

    paginator = Paginator(articles, 5) 
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)

    context = {
        'articles': articles,
        'tags':  tags,
    }

    return render(request, 'top_articles.html', context)

def newest_articles(request):
    articles = article.objects.filter(admin_approved=True).order_by('-created_at')[:10]
    tags = Tag.objects.all() 

    paginator = Paginator(articles, 5) 
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)


    context = {
        'articles': articles,
        'tags':  tags,
    }
    return render(request, 'newest_articles.html', context)



def search_results(request):
    query = request.GET.get('q')
    tags = Tag.objects.all() 

    if query:
        articles = article.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    else:
        articles = None
    context = {
        'query': query,
        'articles': articles,
        'tags':tags
    }
    return render(request, 'search_results.html', context)
