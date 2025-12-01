import json
import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import BlogPost, Category, NewsletterSubscriber

logger = logging.getLogger(__name__)

def blog(request):
    # Récupérer les articles publiés, triés par date de création
    posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    
    # Récupérer toutes les catégories avec le compte d'articles
    categories = Category.objects.all()
    
    # Statistiques
    total_posts = BlogPost.objects.filter(is_published=True).count()
    newsletter_total = NewsletterSubscriber.objects.count()
    
    context = {
        'posts': posts,
        'categories': categories,
        'total_posts': total_posts,
        'newsletter_total': newsletter_total,
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


@require_POST
def newsletter_subscribe(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        payload = request.POST

    email = (payload.get('email') or '').strip().lower()

    if not email:
        return JsonResponse({
            'success': False,
            'message': "Merci d'indiquer votre adresse email."
        }, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({
            'success': False,
            'message': "L'adresse email fournie n'est pas valide."
        }, status=400)

    subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
    timestamp = timezone.now().strftime('%d/%m/%Y à %H:%M')

    response_message = (
        "Merci ! Votre inscription est confirmée."
        if created else
        "Vous êtes déjà inscrit(e) à notre newsletter."
    )

    email_feedback = {'user': False, 'admin': False}

    if created:
        user_subject = "✅ Confirmation d'inscription newsletter - Debout Wanindara"
        user_body = f"""Bonjour,

Merci de vous être abonné(e) à la newsletter de Debout Wanindara.

🕒 Date d'inscription : {timestamp}
📧 Adresse enregistrée : {email}

Vous recevrez désormais nos actualités, événements et appels à projets.

Cordialement,
L'équipe Debout Wanindara
"""
        user_template_params = {
            'to_email': email,
            'subscription_date': timestamp,
        }

        success, error_msg, channel = dispatch_email_notification(
            'newsletter_user',
            user_template_params,
            user_subject,
            user_body.strip(),
            [email],
        )
        if success:
            email_feedback['user'] = True
        else:
            logger.error("Newsletter user email error: %s", error_msg)

        admin_subject = "📰 Nouvelle inscription newsletter"
        admin_body = f"""Nouvelle inscription à la newsletter :

📧 Email : {email}
📅 Date : {timestamp}
"""
        admin_template_params = {
            'to_email': 'deboutwanindara@gmail.com',
            'subscriber_email': email,
            'subscription_date': timestamp,
        }

        success, error_msg, channel = dispatch_email_notification(
            'newsletter_admin',
            admin_template_params,
            admin_subject,
            admin_body.strip(),
            ['deboutwanindara@gmail.com'],
        )
        if success:
            email_feedback['admin'] = True
        else:
            logger.error("Newsletter admin email error: %s", error_msg)

    return JsonResponse({
        'success': True,
        'message': response_message,
        'already_subscribed': not created,
        'email_notifications': email_feedback,
    })