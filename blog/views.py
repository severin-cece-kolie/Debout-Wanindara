from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Category

def blog(request):
    # Récupérer les articles publiés, triés par date de création
    posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    
    # Récupérer toutes les catégories avec le compte d'articles
    categories = Category.objects.all()
    
    # Statistiques
    total_posts = BlogPost.objects.filter(is_published=True).count()
    
    context = {
        'posts': posts,
        'categories': categories,
        'total_posts': total_posts,
    }
    
    return render(request, 'blog/blog.html', context)

def post_detail(request, slug):
    # Récupérer l'article ou retourner une 404
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Articles récents de la même catégorie
    related_posts = BlogPost.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id).order_by('-created_at')[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'blog/post_detail.html', context)