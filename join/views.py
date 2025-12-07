from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from .models import Membre, Applicant, GalleryPhoto
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4  # pyright: ignore[reportMissingModuleSource]
from reportlab.lib.units import mm  # pyright: ignore[reportMissingModuleSource]
from reportlab.pdfgen import canvas  # pyright: ignore[reportMissingModuleSource]
from reportlab.lib.utils import ImageReader  # pyright: ignore[reportMissingModuleSource]
from PIL import Image, ImageDraw, ImageFont  # pyright: ignore[reportMissingModuleSource]
import textwrap
import qrcode  # pyright: ignore[reportMissingModuleSource]
import hashlib
import logging

logger = logging.getLogger(__name__)


def permission_denied_view(request, exception=None):
    """Affiche la page 403 personnalisée."""
    return render(request, '403.html', status=403)


def send_email_notification(template_name, template_params, subject, body, recipients, attachment_buffer=None, attachment_filename=None):
    """
    Envoi email unifié (SMTP uniquement) avec support des pièces jointes.
    Retourne (success, error_message, channel)
    Ce handler est robuste : il n'exige pas une variable EMAIL_HOST présente.
    """
    try:
        # Trouver un from_email utilisable (fallback)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)

        if not from_email:
            logger.warning("Aucun expéditeur configuré (DEFAULT_FROM_EMAIL ni EMAIL_HOST_USER). Tentative d'envoi néanmoins (fail_silently=True).")

        email = EmailMessage(
            subject,
            body,
            from_email,
            recipients
        )

        # Ajouter la pièce jointe si fournie
        if attachment_buffer and attachment_filename:
            try:
                email.attach(attachment_filename, attachment_buffer.getvalue(), 'application/pdf')
            except Exception as e:
                logger.exception("Impossible d'attacher le buffer PDF à l'email: %s", e)
                # continuer sans pièce jointe

        # Envoyer (laisser l'exception remonter si configuration SMTP invalide)
        email.send(fail_silently=False)
        logger.info("Email envoyé avec succès à %s", recipients)
        return True, None, "smtp"

    except Exception as e:
        logger.exception("Erreur envoi email: %s", e)
        return False, str(e), None


# ----------------------------------------------------------------------
#  UTILITAIRES
# ----------------------------------------------------------------------

def get_logo_path():
    """Retourne le chemin réel du logo."""
    try:
        logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')
        if os.path.exists(logo_path):
            return logo_path

        for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
            path = os.path.join(static_dir, 'img', 'logo.png')
            if os.path.exists(path):
                return path

    except Exception as e:
        logger.exception("Erreur lors de la recherche du logo: %s", e)

    return None


def generate_qr_code_image(membre, request):
    """Génère un QR code sécurisé pour le badge."""
    try:
        secret_key = getattr(settings, 'SECRET_KEY', '')
        # fallback safe if created_at is missing
        created_at_str = ''
        try:
            created_at_str = membre.created_at.strftime('%Y%m%d')
        except Exception:
            created_at_str = timezone.now().strftime('%Y%m%d')

        data_string = f"{membre.numero_id}|{membre.id}|{created_at_str}"
        signature = hashlib.sha256(f"{data_string}{secret_key}".encode()).hexdigest()[:16]

        try:
            verification_url = request.build_absolute_uri(
                reverse('join:verify_badge', args=[membre.id, signature])
            )
        except Exception:
            # fallback to simple path if reverse fails
            verification_url = f"/join/verify/{membre.id}/{signature}/"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        return qr.make_image(fill_color="black", back_color="white")
    except Exception as e:
        logger.exception("Erreur génération QR: %s", e)
        return Image.new('RGB', (60, 60), color='white')


def generate_badge_pdf_buffer(membre, request):
    """
    Génère le PDF du badge et retourne un buffer BytesIO
    """
    try:
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

        return buffer
    except Exception as e:
        logger.exception("Erreur lors de la génération du PDF: %s", e)
        # retourner un buffer vide pour ne pas casser la suite
        return BytesIO()


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

    except Exception as e:
        logger.exception("Erreur badge_qr_view: %s", e)
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

        secret_key = getattr(settings, 'SECRET_KEY', '')
        created_at_str = ''
        try:
            created_at_str = membre.created_at.strftime('%Y%m%d')
        except Exception:
            created_at_str = timezone.now().strftime('%Y%m%d')

        data_string = f"{membre.numero_id}|{membre.id}|{created_at_str}"
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

    except Exception as e:
        logger.exception("Erreur verify_badge: %s", e)
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
    try:
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
        c.setFillColorRGB(1, 1, 1)
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

        if membre.photo and os.path.exists(getattr(membre.photo, 'path', '')):
            try:
                c.drawImage(membre.photo.path, photo_x, photo_y, photo_size_mm, photo_size_mm, mask='auto')
            except Exception:
                c.setFillColorRGB(0.9, 0.9, 0.9)
                c.roundRect(photo_x, photo_y, photo_size_mm, photo_size_mm, 5, fill=1, stroke=0)

        # ---------- NOM COMPLET ----------
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(1, 1, 1)
        name_text = (membre.nom_complet or "").upper()
        namew = c.stringWidth(name_text, "Helvetica-Bold", 11)
        name_y = photo_y - 8*mm
        c.drawString(x + (badge_width - namew) / 2, name_y, name_text)

        # ---------- POSTE/POSITION ----------
        pos_y = name_y - 5*mm
        if getattr(membre, 'position', None):
            c.setFont("Helvetica", 9)
            c.setFillColorRGB(1, 1, 1)
            posw = c.stringWidth(membre.position, "Helvetica", 9)
            pos_y = name_y - 5*mm
            c.drawString(x + (badge_width - posw) / 2, pos_y, membre.position)

        # ---------- ID ----------
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(1, 1, 1)
        id_text = f"ID: {membre.numero_id}"
        idw = c.stringWidth(id_text, "Helvetica", 8)
        id_y = pos_y - 7*mm if getattr(membre, 'position', None) else name_y - 12*mm
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
            except Exception:
                logger.exception("Erreur affichage logo recto")

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
            except Exception:
                logger.exception("Erreur affichage QR recto")

    except Exception as e:
        logger.exception("Erreur dans draw_badge_recto: %s", e)
        # Ne pas lever l'exception pour éviter crash complet du rendu


# ----------------------------------------------------------------------
#  DESSIN DU VERSO - SANS CHEVAUCHEMENT
# ----------------------------------------------------------------------

def draw_badge_verso(c, x, y, width, height):
    try:
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
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(0, 0, 0)
        title = "CONDITIONS D'UTILISATION"
        w = c.stringWidth(title, "Helvetica-Bold", 9)
        c.drawString(x + (badge_width - w)/2, y + badge_height - 18*mm, title)

        # ---------- LISTE DES CONDITIONS ----------
        c.setFont("Helvetica", 6)
        c.setFillColorRGB(0.2, 0.2, 0.2)

        conditions = [
            "Ce badge est personnel et non transférable.",
            "Il doit être présenté lors des événements.",
            "En cas de perte, contactez l'administration.",
            "Le badge reste propriété de Debout Wanindara.",
            "Toute utilisation frauduleuse est interdite."
        ]

        line_y = y + badge_height - 26*mm

        for cond in conditions:
            lines = textwrap.wrap(cond, width=38)
            for line in lines:
                if line_y > y + 30*mm:
                    c.drawString(x + 6*mm, line_y, f"• {line}")
                line_y -= 3.2*mm
            line_y -= 0.5*mm

        # ---------- ZONE SIGNATURE ----------
        signature_y = y + 20*mm

        c.setFont("Helvetica-Bold", 7)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(x + 6*mm, signature_y, "Signature du membre")

        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.5)
        c.line(x + 6*mm, signature_y - 2*mm, x + badge_width - 6*mm, signature_y - 2*mm)

        c.setFont("Helvetica", 7)
        c.drawString(x + 6*mm, signature_y - 6*mm, "Date:")
    except Exception as e:
        logger.exception("Erreur draw_badge_verso: %s", e)


# ----------------------------------------------------------------------
#  EXPORT PDF - ACCÈS PUBLIC
# ----------------------------------------------------------------------

def badge_pdf_view(request, membre_id):
    """Génère le PDF du badge - Accès public."""
    try:
        membre = get_object_or_404(Membre, id=membre_id)

        buffer = generate_badge_pdf_buffer(membre, request)
        filename = f"badge_{(membre.nom_complet or 'membre').replace(' ', '_')}.pdf"

        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        logger.exception("Erreur badge_pdf_view: %s", e)
        return HttpResponse("Erreur lors de la génération du PDF.", status=500)


# ----------------------------------------------------------------------
# EXPORT PNG - ACCÈS PUBLIC
# ----------------------------------------------------------------------

def badge_png_view(request, membre_id):
    """Génère le PNG du badge - Accès public."""
    try:
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
        except Exception:
            font_title = ImageFont.load_default()
        org_text = "DEBOUT WANINDARA"
        bbox = draw.textbbox((0, 0), org_text, font=font_title)
        tw = bbox[2] - bbox[0]
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

        if membre.photo and os.path.exists(getattr(membre.photo, 'path', '')):
            try:
                photo = Image.open(membre.photo.path).convert("RGBA")
                photo = photo.resize((photo_size, photo_size))
                img.paste(photo, (photo_x, photo_y), photo)
            except Exception:
                draw.rectangle([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size],
                               fill=(240,240,240), outline=None)

        # ---------- NOM COMPLET ----------
        try:
            font_name = ImageFont.truetype("arialbd.ttf", int(11 * dpi / 25.4))
        except Exception:
            font_name = ImageFont.load_default()
        name_text = (membre.nom_complet or "").upper()
        bbox = draw.textbbox((0, 0), name_text, font=font_name)
        tw = bbox[2] - bbox[0]
        name_y = photo_y - int(8 * mm * dpi / 25.4)
        draw.text(((badge_width_px - tw)//2, name_y), name_text, fill=(255,255,255), font=font_name)

        # ---------- POSTE/POSITION ----------
        try:
            font_pos = ImageFont.truetype("arial.ttf", int(9 * dpi / 25.4))
        except Exception:
            font_pos = ImageFont.load_default()
        pos_y = name_y - int(5 * mm * dpi / 25.4)
        if getattr(membre, 'position', None):
            bbox = draw.textbbox((0, 0), membre.position, font=font_pos)
            tw = bbox[2] - bbox[0]
            pos_y = name_y - int(5 * mm * dpi / 25.4)
            draw.text(((badge_width_px - tw)//2, pos_y), membre.position, fill=(255,255,255), font=font_pos)

        # ---------- ID ----------
        try:
            font_id = ImageFont.truetype("arial.ttf", int(8 * dpi / 25.4))
        except Exception:
            font_id = ImageFont.load_default()
        id_text = f"ID: {membre.numero_id}"
        bbox = draw.textbbox((0, 0), id_text, font=font_id)
        tw = bbox[2] - bbox[0]
        id_y = pos_y - int(7 * mm * dpi / 25.4) if getattr(membre, 'position', None) else name_y - int(12 * mm * dpi / 25.4)
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
                logger.exception("Erreur collage logo png")

        # QR Code à droite
        try:
            qr_img = generate_qr_code_image(membre, request).resize((logo_qr_size, logo_qr_size))
            qr_x = badge_width_px - logo_qr_size - int(8 * mm * dpi / 25.4)
            img.paste(qr_img, (qr_x, logo_qr_y))
        except Exception:
            logger.exception("Erreur collage QR png")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        filename = f"badge_{(membre.nom_complet or 'membre').replace(' ', '_')}.png"

        response = HttpResponse(buffer.getvalue(), content_type="image/png")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.exception("Erreur badge_png_view: %s", e)
        return HttpResponse("Erreur lors de la génération du PNG.", status=500)


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
            # support both "languages" and "languages[]"
            languages = ",".join(request.POST.getlist("languages") or request.POST.getlist("languages[]") or [])
            country = request.POST.get('country', 'GIN')
            city = request.POST.get('city', 'CONAKRY')
            district = request.POST.get('district', '').strip()

            logger.info("Formulaire badge reçu: %s %s - %s - %s", first_name, last_name, email, position)

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
                photo=applicant.photo if getattr(applicant, 'photo', None) else None
            )
            logger.info("Badge sauvegardé en base de données: %s", numero_id)

            # GÉNÉRATION DU PDF DU BADGE
            pdf_buffer = generate_badge_pdf_buffer(membre, request)
            pdf_filename = f"badge_{nom_complet.replace(' ', '_')}.pdf"

            # Vérifier la configuration email
            email_configured = (
                hasattr(settings, 'EMAIL_HOST_PASSWORD') and
                settings.EMAIL_HOST_PASSWORD and
                getattr(settings, 'EMAIL_BACKEND', '') == 'django.core.mail.backends.smtp.EmailBackend'
            )

            # Envoi des emails avec le badge en pièce jointe
            email_results = {'admin': False, 'user': False}
            email_channels = {'admin': None, 'user': None}
            email_errors = []

            # Email à Debout Wanindara AVEC le badge PDF
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

Le badge est joint à cet email.

Debout Wanindara - Système de badges"""

            # Créer une nouvelle copie du buffer pour l'admin
            try:
                admin_pdf_buffer = BytesIO(pdf_buffer.getvalue())
            except Exception:
                admin_pdf_buffer = None
                logger.exception("Impossible de cloner le buffer PDF pour admin")

            success, error_msg, channel = send_email_notification(
                'application_admin',
                {},
                admin_subject,
                admin_body.strip(),
                ['deboutwanindara@gmail.com'],
                attachment_buffer=admin_pdf_buffer,
                attachment_filename=pdf_filename
            )

            if success:
                email_results['admin'] = True
                email_channels['admin'] = channel
                logger.info("Email ADMIN envoyé avec badge PDF")
            else:
                logger.error("Erreur envoi email admin: %s", error_msg)
                email_errors.append("admin")

            # Email de confirmation au membre AVEC le badge PDF
            try:
                badge_url = request.build_absolute_uri(reverse('join:badge_view', args=[membre.id]))
                badge_pdf_url = request.build_absolute_uri(reverse('join:badge_pdf', args=[membre.id]))
                badge_png_url = request.build_absolute_uri(reverse('join:badge_png', args=[membre.id]))
            except Exception:
                # fallback si reverse échoue (urls.py différent)
                badge_url = f"/join/badge/{membre.id}/"
                badge_pdf_url = f"/join/badge/{membre.id}/pdf/"
                badge_png_url = f"/join/badge/{membre.id}/png/"

            user_subject = "✅ Votre badge Debout Wanindara est prêt !"
            user_body = f"""Bonjour {nom_complet},

Félicitations ! Votre badge a été généré avec succès.

📋 Récapitulatif de votre inscription :
• Numéro de badge: {numero_id}
• Poste: {position}
• Date d'inscription: {timezone.now().strftime('%d/%m/%Y à %H:%M')}
• Référence membre: #{membre.id}

📎 Votre badge est joint à cet email au format PDF.

Vous pouvez également :
• Consulter votre badge en ligne: {badge_url}
• Le télécharger en PDF: {badge_pdf_url}
• Le télécharger en PNG: {badge_png_url}

💡 Conseil: Imprimez votre badge ou gardez une copie sur votre téléphone pour le présenter lors des événements.

Pour toute question, contactez-nous :
📞 +224 629829087
📧 deboutwanindara@gmail.com

Bienvenue dans la communauté Debout Wanindara !

Cordialement,
L'équipe Debout Wanindara

---
Ceci est un message automatique, merci de ne pas y répondre."""

            # Créer une nouvelle copie du buffer pour l'utilisateur
            try:
                user_pdf_buffer = BytesIO(pdf_buffer.getvalue())
            except Exception:
                user_pdf_buffer = None
                logger.exception("Impossible de cloner le buffer PDF pour user")

            success, error_msg, channel = send_email_notification(
                'application_user',
                {},
                user_subject,
                user_body.strip(),
                [email],
                attachment_buffer=user_pdf_buffer,
                attachment_filename=pdf_filename
            )

            if success:
                email_results['user'] = True
                email_channels['user'] = channel
                logger.info("Email CONFIRMATION envoyé avec badge PDF à %s", email)
            else:
                logger.error("Erreur envoi email confirmation: %s", error_msg)
                email_errors.append("user")

            # Message de succès
            if email_results['admin'] and email_results['user']:
                success_message = f'Badge généré! Numéro: {numero_id}. Vous avez reçu votre badge par email avec les liens de téléchargement.'
            elif email_results['user']:
                success_message = f'Badge généré! Numéro: {numero_id}. Vous avez reçu votre badge par email.'
            else:
                success_message = f'Badge enregistré. Numéro: {numero_id}. Téléchargez-le via les liens ci-dessous.'

            if email_errors and email_configured:
                logger.warning("Emails non envoyés malgré la configuration: %s", email_errors)

            # Vérifier si c'est une requête AJAX ou formulaire classique
            try:
                redirect_path = reverse('join:badge_success', args=[membre.id])
            except Exception:
                redirect_path = f"/join/badge/success/{membre.id}/"

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Retourner JSON pour AJAX
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'badge_id': numero_id,
                    'membre_id': membre.id,
                    'redirect_url': redirect_path,
                })
            else:
                # Rediriger vers la page de succès (utiliser reverse pour éviter NoReverseMatch silencieux)
                return redirect(redirect_path)

        except Exception as e:
            logger.exception("Erreur générale badge: %s", e)
            return JsonResponse({
                'success': False,
                'message': 'Une erreur est survenue lors de la génération du badge. Veuillez réessayer.'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée.'
    }, status=405)


# ----------------------------------------------------------------------
# PAGE DE SUCCÈS APRÈS GÉNÉRATION DU BADGE
# ----------------------------------------------------------------------

def badge_success_view(request, membre_id):
    """Affiche la page de succès après génération du badge"""
    membre = get_object_or_404(Membre, id=membre_id)

    # Vérifier la configuration email
    email_configured = (
        hasattr(settings, 'EMAIL_HOST_PASSWORD') and
        settings.EMAIL_HOST_PASSWORD and
        getattr(settings, 'EMAIL_BACKEND', '') == 'django.core.mail.backends.smtp.EmailBackend'
    )

    # URLs du badge
    try:
        badge_url = request.build_absolute_uri(reverse('join:badge_view', args=[membre.id]))
        badge_pdf_url = request.build_absolute_uri(reverse('join:badge_pdf', args=[membre.id]))
        badge_png_url = request.build_absolute_uri(reverse('join:badge_png', args=[membre.id]))
    except Exception:
        badge_url = f"/join/badge/{membre.id}/"
        badge_pdf_url = f"/join/badge/{membre.id}/pdf/"
        badge_png_url = f"/join/badge/{membre.id}/png/"

    message = f'Votre badge {membre.numero_id} a été généré avec succès.'

    context = {
        'membre': membre,
        'badge_id': membre.numero_id,
        'membre_id': membre.id,
        'message': message,
        'badge_url': badge_url,
        'badge_pdf_url': badge_pdf_url,
        'badge_png_url': badge_png_url,
        'emails_sent': {
            'user': email_configured,
            'admin': email_configured,
        }
    }

    return render(request, 'join/badge_success.html', context)


# ----------------------------------------------------------------------
#  GALERIE PHOTOS
# ----------------------------------------------------------------------

def gallery_view(request):
    """Affiche la galerie photos de l'ONG"""
    try:
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
        logger.exception("Erreur dans gallery_view: %s", e)
        context = {
            'photos': [],
            'featured_photos': [],
            'categories': [],
            'selected_category': 'all',
            'page_title': 'Galerie Photos - Debout Wanindara',
        }

    return render(request, "join/gallery.html", context)
