from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from core.email_utils import send_email_robust
from .models import Membre, Applicant, GalleryPhoto
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import textwrap
import qrcode
import hashlib
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

def permission_denied_view(request, exception=None):
    """Affiche la page 403 personnalisée."""
    return render(request, '403.html', status=403)


# ----------------------------------------------------------------------
#  UTILITAIRES
# ----------------------------------------------------------------------

def get_logo_path():
    """Retourne le chemin réel du logo."""
    logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')
    if os.path.exists(logo_path):
        return logo_path

    for static_dir in settings.STATICFILES_DIRS:
        path = os.path.join(static_dir, 'img', 'logo.png')
        if os.path.exists(path):
            return path

    return None


def generate_qr_code_image(membre, request):
    """Génère un QR code sécurisé pour le badge."""
    try:
        secret_key = settings.SECRET_KEY
        data_string = f"{membre.numero_id}|{membre.id}|{membre.created_at.strftime('%Y%m%d')}"
        signature = hashlib.sha256(f"{data_string}{secret_key}".encode()).hexdigest()[:16]

        verification_url = request.build_absolute_uri(
            reverse('join:verify_badge', args=[membre.id, signature])
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        return qr.make_image(fill_color="black", back_color="white")
    except:
        return Image.new('RGB', (60, 60), color='white')


# ----------------------------------------------------------------------
#  VUE POUR AFFICHER LE QR CODE DIRECTEMENT
# ----------------------------------------------------------------------

def badge_qr_view(request, membre_id):
    """Affiche juste le QR code du membre."""
    try:
        membre = get_object_or_404(Membre, id=membre_id)
        qr_img = generate_qr_code_image(membre, request)

        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)
        return HttpResponse(buffer.getvalue(), content_type="image/png")

    except:
        img = Image.new('RGB', (50, 50), color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return HttpResponse(buffer.getvalue(), content_type="image/png")


# ----------------------------------------------------------------------
#  VERIFICATION DU BADGE VIA QR CODE
# ----------------------------------------------------------------------

def verify_badge(request, membre_id, signature):
    """Vérifie l'authenticité numérique du badge."""
    try:
        membre = get_object_or_404(Membre, id=membre_id)

        secret_key = settings.SECRET_KEY
        data_string = f"{membre.numero_id}|{membre.id}|{membre.created_at.strftime('%Y%m%d')}"
        expected_signature = hashlib.sha256(f"{data_string}{secret_key}".encode()).hexdigest()[:16]

        if signature == expected_signature:
            valid = True
            message = "Badge authentique"
        else:
            valid = False
            message = "Badge falsifié"

        return render(request, 'join/verify_badge.html', {
            'membre': membre if valid else None,
            'valid': valid,
            'message': message,
        })

    except:
        return render(request, 'join/verify_badge.html', {
            'valid': False,
            'message': "Erreur pendant la vérification."
        })


# ----------------------------------------------------------------------
#  FONCTION DE VÉRIFICATION ADMIN
# ----------------------------------------------------------------------

def is_admin(user):
    """Vérifie si l'utilisateur est administrateur."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ----------------------------------------------------------------------
#  AFFICHAGE DU BADGE HTML - ACCÈS PUBLIC
# ----------------------------------------------------------------------

def badge_view(request, membre_id):
    """Affiche le badge HTML - Accès public."""
    membre = get_object_or_404(Membre, id=membre_id)

    if not membre.numero_id:
        membre.numero_id = f"DW-{membre.id:04d}"
        membre.save()

    context = {
        'membre': membre,
        'date_emission': timezone.now().strftime("%d/%m/%Y"),
    }
    return render(request, "join/badge.html", context)


# ----------------------------------------------------------------------
#  DESSIN DU RECTO (PDF) - AVEC COULEUR ET DESIGN
# ----------------------------------------------------------------------

def draw_badge_recto(c, membre, date_emission, x, y, width, height, request=None):
    """
    VERSION AVEC COULEUR ET DESIGN - Recto comme sur l'image
    """
    badge_width = 53.98 * mm
    badge_height = 85.6 * mm

    # Dégradé de couleur orange vers cyan
    orange_start = (234/255, 88/255, 12/255)
    orange_mid = (249/255, 115/255, 22/255)
    cyan_end = (6/255, 182/255, 212/255)

    # Dessin du dégradé
    for i in range(50):
        ratio = i / 49
        if ratio < 0.5:
            r = orange_start[0] + (orange_mid[0] - orange_start[0]) * (ratio * 2)
            g = orange_start[1] + (orange_mid[1] - orange_start[1]) * (ratio * 2)
            b = orange_start[2] + (orange_mid[2] - orange_start[2]) * (ratio * 2)
        else:
            r = orange_mid[0] + (cyan_end[0] - orange_mid[0]) * ((ratio - 0.5) * 2)
            g = orange_mid[1] + (cyan_end[1] - orange_mid[1]) * ((ratio - 0.5) * 2)
            b = orange_mid[2] + (cyan_end[2] - orange_mid[2]) * ((ratio - 0.5) * 2)

        c.setFillColorRGB(r, g, b)
        step_height = badge_height / 50
        c.rect(x, y + i * step_height, badge_width, step_height, fill=1, stroke=0)

    # Bordure blanche
    c.setStrokeColorRGB(1, 1, 1)
    c.setLineWidth(0.53 * mm)
    c.roundRect(x, y, badge_width, badge_height, 12, fill=0, stroke=1)

    # ---------- TITRE DEBOUT WANINDARA EN HAUT ----------
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(1, 1, 1)  # Blanc pour contraster avec le dégradé
    org_text = "DEBOUT WANINDARA"
    textw = c.stringWidth(org_text, "Helvetica-Bold", 10)
    org_y = y + badge_height - 12*mm
    c.drawString(x + (badge_width - textw) / 2, org_y, org_text)

    # ---------- PHOTO CENTRÉE ----------
    photo_size_mm = 25 * mm
    photo_x = x + (badge_width - photo_size_mm) / 2
    photo_y = org_y - 5*mm - photo_size_mm
    
    # Cadre blanc pour la photo
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(1, 1, 1)
    c.setLineWidth(1)
    c.roundRect(photo_x - 1*mm, photo_y - 1*mm, photo_size_mm + 2*mm, photo_size_mm + 2*mm, 8, fill=1, stroke=1)
    
    if membre.photo and os.path.exists(membre.photo.path):
        try:
            c.drawImage(membre.photo.path, photo_x, photo_y, photo_size_mm, photo_size_mm, mask='auto')
        except:
            # Placeholder si photo non disponible
            c.setFillColorRGB(0.9, 0.9, 0.9)
            c.roundRect(photo_x, photo_y, photo_size_mm, photo_size_mm, 5, fill=1, stroke=0)

    # ---------- NOM COMPLET ----------
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(1, 1, 1)  # Blanc
    name_text = (membre.nom_complet or "").upper()
    namew = c.stringWidth(name_text, "Helvetica-Bold", 11)
    name_y = photo_y - 8*mm
    c.drawString(x + (badge_width - namew) / 2, name_y, name_text)

    # ---------- POSTE/POSITION ----------
    if membre.position:
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(1, 1, 1)  # Blanc
        posw = c.stringWidth(membre.position, "Helvetica", 9)
        pos_y = name_y - 5*mm
        c.drawString(x + (badge_width - posw) / 2, pos_y, membre.position)

    # ---------- ID ----------
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(1, 1, 1)  # Blanc
    id_text = f"ID: {membre.numero_id}"
    idw = c.stringWidth(id_text, "Helvetica", 8)
    id_y = pos_y - 7*mm if membre.position else name_y - 12*mm
    c.drawString(x + (badge_width - idw) / 2, id_y, id_text)

    # ---------- ZONE LOGO + QR CODE CÔTE À CÔTE EN BAS ----------
    logo_qr_y = y + 10*mm
    logo_qr_size = 12 * mm
    
    # Logo à gauche
    logo_path = get_logo_path()
    if logo_path:
        try:
            logo = ImageReader(logo_path)
            logo_x = x + 8*mm
            c.drawImage(logo, logo_x, logo_qr_y, logo_qr_size, logo_qr_size, mask='auto')
        except:
            pass

    # QR Code à droite
    if request:
        try:
            qr_img = generate_qr_code_image(membre, request)
            buf = BytesIO()
            qr_img.save(buf, format="PNG")
            buf.seek(0)
            qr = ImageReader(buf)
            qr_x = x + badge_width - logo_qr_size - 8*mm
            c.drawImage(qr, qr_x, logo_qr_y, logo_qr_size, logo_qr_size)
        except:
            pass


# ----------------------------------------------------------------------
#  DESSIN DU VERSO - SANS CHEVAUCHEMENT
# ----------------------------------------------------------------------

def draw_badge_verso(c, x, y, width, height):
    badge_width = 53.98 * mm
    badge_height = 85.6 * mm

    # Dégradé de couleur (identique au recto)
    orange_start = (234/255, 88/255, 12/255)
    orange_mid = (249/255, 115/255, 22/255)
    cyan_end = (6/255, 182/255, 212/255)

    for i in range(50):
        ratio = i / 49
        if ratio < 0.5:
            r = orange_start[0] + (orange_mid[0] - orange_start[0]) * (ratio * 2)
            g = orange_start[1] + (orange_mid[1] - orange_start[1]) * (ratio * 2)
            b = orange_start[2] + (orange_mid[2] - orange_start[2]) * (ratio * 2)
        else:
            r = orange_mid[0] + (cyan_end[0] - orange_mid[0]) * ((ratio - 0.5) * 2)
            g = orange_mid[1] + (cyan_end[1] - orange_mid[1]) * ((ratio - 0.5) * 2)
            b = orange_mid[2] + (cyan_end[2] - orange_mid[2]) * ((ratio - 0.5) * 2)

        c.setFillColorRGB(r, g, b)
        step_height = badge_height / 50
        c.rect(x, y + i * step_height, badge_width, step_height, fill=1, stroke=0)

    # Bordure blanche
    c.setStrokeColorRGB(1, 1, 1)
    c.setLineWidth(0.53 * mm)
    c.roundRect(x, y, badge_width, badge_height, 12, fill=0, stroke=1)

    # Zone de contenu blanc avec marges plus grandes
    content_margin = 4*mm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(x + content_margin, y + content_margin, 
                badge_width - 2*content_margin, badge_height - 2*content_margin, 
                8, fill=1, stroke=0)

    # ---------- TITRE CONDITIONS ----------
    c.setFont("Helvetica-Bold", 9)  # Taille réduite
    c.setFillColorRGB(0, 0, 0)
    title = "CONDITIONS D'UTILISATION"
    w = c.stringWidth(title, "Helvetica-Bold", 9)
    c.drawString(x + (badge_width - w)/2, y + badge_height - 18*mm, title)

    # ---------- LISTE DES CONDITIONS ----------
    c.setFont("Helvetica", 6)  # Taille réduite pour éviter le chevauchement
    c.setFillColorRGB(0.2, 0.2, 0.2)
    
    conditions = [
        "Ce badge est personnel et non transférable.",
        "Il doit être présenté lors des événements.",
        "En cas de perte, contactez l'administration.",
        "Le badge reste propriété de Debout Wanindara.",
        "Toute utilisation frauduleuse est interdite."
    ]

    # Position de départ ajustée
    line_y = y + badge_height - 26*mm
    
    for cond in conditions:
        # Gestion du texte avec largeur réduite
        lines = textwrap.wrap(cond, width=38)  # Largeur réduite
        for line in lines:
            if line_y > y + 30*mm:  # Vérifier qu'on ne dépasse pas la zone signature
                c.drawString(x + 6*mm, line_y, f"• {line}")
            line_y -= 3.2*mm  # Espacement réduit
        line_y -= 0.5*mm  # Petit espace entre conditions

    # ---------- ZONE SIGNATURE ----------
    # S'assurer que la zone signature est bien en bas
    signature_y = y + 20*mm
    
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x + 6*mm, signature_y, "Signature du membre")
    
    # Ligne de signature
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    c.line(x + 6*mm, signature_y - 2*mm, x + badge_width - 6*mm, signature_y - 2*mm)

    # ---------- DATE ----------
    c.setFont("Helvetica", 7)
    c.drawString(x + 6*mm, signature_y - 6*mm, "Date:")


# ----------------------------------------------------------------------
#  EXPORT PDF - ACCÈS PUBLIC
# ----------------------------------------------------------------------

def badge_pdf_view(request, membre_id):
    """Génère le PDF du badge - Accès public."""
    membre = get_object_or_404(Membre, id=membre_id)
    date_emission = timezone.now().strftime("%d/%m/%Y")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    badge_width = 53.98 * mm
    badge_height = 85.6 * mm
    spacing = 20 * mm

    page_width, page_height = A4
    total_width = badge_width * 2 + spacing
    start_x = (page_width - total_width) / 2
    start_y = (page_height - badge_height) / 2

    draw_badge_recto(c, membre, date_emission, start_x, start_y, badge_width, badge_height, request)
    draw_badge_verso(c, start_x + badge_width + spacing, start_y, badge_width, badge_height)

    c.showPage()
    c.save()

    buffer.seek(0)
    filename = f"badge_{membre.nom_complet.replace(' ', '_')}.pdf"

    return HttpResponse(buffer.getvalue(), content_type="application/pdf")


# ----------------------------------------------------------------------
# EXPORT PNG - ACCÈS PUBLIC
# ----------------------------------------------------------------------

def badge_png_view(request, membre_id):
    """Génère le PNG du badge - Accès public."""
    membre = get_object_or_404(Membre, id=membre_id)
    date_emission = timezone.now().strftime("%d/%m/%Y")

    dpi = 300
    badge_width_px = int(53.98 * mm * dpi / 25.4)
    badge_height_px = int(85.6 * mm * dpi / 25.4)

    # Création de l'image avec dégradé de couleur
    img = Image.new("RGB", (badge_width_px, badge_height_px), color=(234, 88, 12))
    draw = ImageDraw.Draw(img)

    # Dégradé vertical (pixel)
    orange_start = (234, 88, 12)
    orange_mid = (249, 115, 22)
    cyan_end = (6, 182, 212)

    for py in range(badge_height_px):
        ratio = py / badge_height_px
        if ratio < 0.5:
            r = int(orange_start[0] + (orange_mid[0] - orange_start[0]) * (ratio * 2))
            g = int(orange_start[1] + (orange_mid[1] - orange_start[1]) * (ratio * 2))
            b = int(orange_start[2] + (orange_mid[2] - orange_start[2]) * (ratio * 2))
        else:
            r = int(orange_mid[0] + (cyan_end[0] - orange_mid[0]) * ((ratio - 0.5) * 2))
            g = int(orange_mid[1] + (cyan_end[1] - orange_mid[1]) * ((ratio - 0.5) * 2))
            b = int(orange_mid[2] + (cyan_end[2] - orange_mid[2]) * ((ratio - 0.5) * 2))

        draw.line([(0, py), (badge_width_px, py)], fill=(r, g, b))

    # Bordure blanche
    border_w = max(4, int(0.53 * mm * dpi / 25.4))
    draw.rectangle([(0, 0), (badge_width_px-1, badge_height_px-1)], outline=(255,255,255), width=border_w)

    # ---------- TITRE DEBOUT WANINDARA EN HAUT ----------
    try:
        font_title = ImageFont.truetype("arialbd.ttf", int(10 * dpi / 25.4))
    except:
        font_title = ImageFont.load_default()
    org_text = "DEBOUT WANINDARA"
    tw, th = draw.textsize(org_text, font=font_title)
    org_y = badge_height_px - int(12 * mm * dpi / 25.4)
    draw.text(((badge_width_px - tw)//2, org_y), org_text, fill=(255,255,255), font=font_title)

    # ---------- PHOTO CENTRÉE ----------
    photo_size = int(25 * mm * dpi / 25.4)
    photo_x = (badge_width_px - photo_size) // 2
    photo_y = org_y - int(5 * mm * dpi / 25.4) - photo_size
    
    # Cadre blanc pour la photo
    draw.rectangle([photo_x - int(1*mm*dpi/25.4), photo_y - int(1*mm*dpi/25.4), 
                   photo_x + photo_size + int(1*mm*dpi/25.4), photo_y + photo_size + int(1*mm*dpi/25.4)], 
                  fill=(255,255,255), outline=None)
    
    if membre.photo and os.path.exists(membre.photo.path):
        try:
            photo = Image.open(membre.photo.path).convert("RGBA")
            photo = photo.resize((photo_size, photo_size))
            img.paste(photo, (photo_x, photo_y), photo)
        except:
            # Placeholder si photo non disponible
            draw.rectangle([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size], 
                          fill=(240,240,240), outline=None)

    # ---------- NOM COMPLET ----------
    try:
        font_name = ImageFont.truetype("arialbd.ttf", int(11 * dpi / 25.4))
    except:
        font_name = ImageFont.load_default()
    name_text = (membre.nom_complet or "").upper()
    tw, th = draw.textsize(name_text, font=font_name)
    name_y = photo_y - int(8 * mm * dpi / 25.4)
    draw.text(((badge_width_px - tw)//2, name_y), name_text, fill=(255,255,255), font=font_name)

    # ---------- POSTE/POSITION ----------
    try:
        font_pos = ImageFont.truetype("arial.ttf", int(9 * dpi / 25.4))
    except:
        font_pos = ImageFont.load_default()
    if membre.position:
        tw, th = draw.textsize(membre.position, font=font_pos)
        pos_y = name_y - int(5 * mm * dpi / 25.4)
        draw.text(((badge_width_px - tw)//2, pos_y), membre.position, fill=(255,255,255), font=font_pos)

    # ---------- ID ----------
    try:
        font_id = ImageFont.truetype("arial.ttf", int(8 * dpi / 25.4))
    except:
        font_id = ImageFont.load_default()
    id_text = f"ID: {membre.numero_id}"
    tw, th = draw.textsize(id_text, font=font_id)
    id_y = pos_y - int(7 * mm * dpi / 25.4) if membre.position else name_y - int(12 * mm * dpi / 25.4)
    draw.text(((badge_width_px - tw)//2, id_y), id_text, fill=(255,255,255), font=font_id)

    # ---------- ZONE LOGO + QR CODE CÔTE À CÔTE EN BAS ----------
    logo_qr_size = int(12 * mm * dpi / 25.4)
    logo_qr_y = int(10 * mm * dpi / 25.4)

    # Logo à gauche
    logo_path = get_logo_path()
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize((logo_qr_size, logo_qr_size))
            logo_x = int(8 * mm * dpi / 25.4)
            img.paste(logo, (logo_x, logo_qr_y), logo)
        except Exception:
            pass

    # QR Code à droite
    try:
        qr_img = generate_qr_code_image(membre, request).resize((logo_qr_size, logo_qr_size))
        qr_x = badge_width_px - logo_qr_size - int(8 * mm * dpi / 25.4)
        img.paste(qr_img, (qr_x, logo_qr_y))
    except:
        pass

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    filename = f"badge_{membre.nom_complet.replace(' ', '_')}.png"

    return HttpResponse(buffer.getvalue(), content_type="image/png")


# ----------------------------------------------------------------------
# ADMIN - LISTE DES BADGES (SEULEMENT POUR ADMINS)
# ----------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def badge_list(request):
    """Liste des badges - Accès réservé aux administrateurs."""
    membres = Membre.objects.all().order_by("nom_complet")
    return render(request, "join/badge_list.html", {"membres": membres})


# ----------------------------------------------------------------------
# ADHESION + GENERATION AUTOMATIQUE DU BADGE
# ----------------------------------------------------------------------

def join_view(request):
    return render(request, "join/join-us.html")


def volunteer_view(request):
    return redirect("join:join")


def submit_application(request):
    if request.method == "POST":
        try:
            # Récupération des données
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            gender = request.POST.get('gender', 'O')
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            position = request.POST.get('position', '').strip()
            diploma = request.POST.get('diploma', '').strip()
            skills = request.POST.get('skills', '').strip()
            languages = ",".join(request.POST.getlist("languages[]", []))
            country = request.POST.get('country', 'GIN')
            city = request.POST.get('city', 'CONAKRY')
            district = request.POST.get('district', '').strip()

            print(f"📨 Formulaire badge reçu: {first_name} {last_name} - {email} - {position}")

            # Validation
            required_fields = [first_name, last_name, email, position, diploma, skills, district]
            if not all(required_fields):
                return JsonResponse({
                    'success': False,
                    'message': 'Veuillez remplir tous les champs obligatoires.'
                })

            # Sauvegarde en base
            applicant = Applicant.objects.create(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                phone=phone,
                email=email,
                position=position,
                diploma=diploma,
                skills=skills,
                languages=languages,
                country=country,
                city=city,
                district=district,
                status="approved",
            )

            if "photo" in request.FILES:
                applicant.photo = request.FILES["photo"]
                applicant.save()

            nom_complet = (applicant.first_name + " " + applicant.last_name).strip() or applicant.email.split("@")[0]

            # Numéro de badge
            count = Membre.objects.count()
            next_id = count + 1
            while Membre.objects.filter(numero_id=f"DW-{next_id:04d}").exists():
                next_id += 1

            numero_id = f"DW-{next_id:04d}"

            membre = Membre.objects.create(
                nom_complet=nom_complet,
                position=applicant.position,
                email=applicant.email,
                phone=applicant.phone,
                numero_id=numero_id,
                photo=applicant.photo if applicant.photo else None
            )
            print("✅ Badge sauvegardé en base de données")

            # Vérifier la configuration email
            email_configured = (
                hasattr(settings, 'EMAIL_HOST_PASSWORD') and 
                settings.EMAIL_HOST_PASSWORD and
                settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend'
            )

            # Envoi des emails - TOUJOURS EN RÉEL SI CONFIGURÉ
            email_results = {'admin': False, 'user': False}
            email_errors = []

            # Email à Debout Wanindara
            admin_subject = f"🆔 Nouveau badge généré: {nom_complet}"
            admin_body = f"""Nouveau badge généré pour un nouveau membre :

👤 Nom complet: {nom_complet}
📧 Email: {email}
📞 Téléphone: {phone or 'Non renseigné'}
🎯 Poste: {position}
📅 Date d'inscription: {timezone.now().strftime('%d/%m/%Y à %H:%M')}

📋 Informations supplémentaires :
• Diplôme: {diploma}
• Compétences: {skills}
• Langues: {languages}
• Pays: {country}, Ville: {city}, Quartier: {district}

---
Numéro de badge: {numero_id}
ID Membre: #{membre.id}
Debout Wanindara - Système de badges"""

            success, error_msg = send_email_robust(
                admin_subject,
                admin_body.strip(),
                ['deboutwanindara@gmail.com'],
                max_retries=2
            )
            
            if success:
                email_results['admin'] = True
                print(f"✅ Email ADMIN envoyé avec succès à deboutwanindara@gmail.com")
            else:
                print(f"❌ Erreur envoi email admin: {error_msg}")
                logger.error(f"Erreur envoi email admin: {error_msg}")
                email_errors.append("admin")

            # Email de confirmation au membre
            user_subject = "✅ Confirmation de génération de badge - Debout Wanindara"
            badge_url = request.build_absolute_uri(reverse('join:badge_view', args=[membre.id]))
            badge_pdf_url = request.build_absolute_uri(reverse('join:badge_pdf', args=[membre.id]))
            badge_png_url = request.build_absolute_uri(reverse('join:badge_png', args=[membre.id]))
            
            user_body = f"""Bonjour {nom_complet},

Félicitations ! Votre badge a été généré avec succès.

📋 Récapitulatif de votre inscription :
• Numéro de badge: {numero_id}
• Poste: {position}
• Date d'inscription: {timezone.now().strftime('%d/%m/%Y à %H:%M')}
• Référence membre: #{membre.id}

Votre badge est maintenant actif et vous pouvez :
• Le consulter en ligne: {badge_url}
• Le télécharger en PDF: {badge_pdf_url}
• Le télécharger en PNG: {badge_png_url}

Pour toute question, contactez-nous :
📞 +224 629829087
📧 deboutwanindara@gmail.com

Bienvenue dans la communauté Debout Wanindara !

Cordialement,
L'équipe Debout Wanindara

---
Ceci est un message automatique, merci de ne pas y répondre."""

            success, error_msg = send_email_robust(
                user_subject,
                user_body.strip(),
                [email],
                max_retries=2
            )
            
            if success:
                email_results['user'] = True
                print(f"✅ Email CONFIRMATION envoyé avec succès à {email}")
            else:
                print(f"❌ Erreur envoi email confirmation: {error_msg}")
                logger.error(f"Erreur envoi email confirmation: {error_msg}")
                email_errors.append("user")

            # Message de succès
            if email_results['admin'] and email_results['user']:
                success_message = f'✅ Votre badge a été généré avec succès! Numéro : {numero_id}. Vous recevrez une confirmation par email.'
            elif email_results['admin']:
                success_message = f'✅ Votre badge a été généré! Numéro : {numero_id}. Notre équipe vous contactera rapidement.'
            elif email_results['user']:
                success_message = f'✅ Votre badge a été généré! Numéro : {numero_id}. Vous avez reçu une confirmation par email.'
            else:
                success_message = f'⚠️ Votre badge a été enregistré. Numéro : {numero_id}. Erreur lors de l\'envoi des emails - nous vous contacterons.'
                
            if email_errors and email_configured:
                logger.warning(f"Emails non envoyés malgré la configuration: {email_errors}")

            return JsonResponse({
                'success': True,
                'message': success_message,
                'badge_id': numero_id,
                'membre_id': membre.id,
                'mode': 'production' if email_configured else 'development',
                'emails_sent': {
                    'admin': email_results['admin'],
                    'user': email_results['user']
                }
            })

        except Exception as e:
            print(f"❌ Erreur générale badge: {e}")
            logger.error(f"Erreur générale badge: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Une erreur est survenue lors de la génération du badge. Veuillez réessayer.'
            })

    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée.'
    })

# ----------------------------------------------------------------------
#  GALERIE PHOTOS 
# ----------------------------------------------------------------------

def gallery_view(request):
    """
    Affiche la galerie photos de l'ONG avec les VRAIES données
    """
    try:
        # UTILISEZ LES VRAIES DONNÉES DE LA BASE
        photos = GalleryPhoto.objects.all()
        featured_photos = GalleryPhoto.objects.filter(featured=True)[:6]
        
        categories = [
            ('EVENTS', 'Événements'),
            ('TEAM', 'Équipe'),
            ('PROJECTS', 'Projets'),
            ('COMMUNITY', 'Communauté'),
            ('ACTIVITIES', 'Activités'),
        ]
        
        selected_category = request.GET.get('category', 'all')
        
        # Filtrer par catégorie si sélectionnée
        if selected_category != 'all':
            photos = photos.filter(category=selected_category)
        
        context = {
            'photos': photos,
            'featured_photos': featured_photos,
            'categories': categories,
            'selected_category': selected_category,
            'page_title': 'Galerie Photos - Debout Wanindara',
        }
        
    except Exception as e:
        # En cas d'erreur
        print(f"Erreur dans gallery_view: {e}")
        context = {
            'photos': [],
            'featured_photos': [],
            'categories': [],
            'selected_category': 'all',
            'page_title': 'Galerie Photos - Debout Wanindara',
        }
    
    return render(request, "join/gallery.html", context)