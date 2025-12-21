# join/migrations/0006_add_member_categories.py
# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('join', '0005_galleryphoto'),  # Adapter selon votre dernière migration
    ]

    operations = [
        migrations.AddField(
            model_name='membre',
            name='categorie',
            field=models.CharField(
                choices=[
                    ('MEMBRE', 'Membre'),
                    ('INVITE', 'Invité'),
                    ('PRESIDENT', 'Président'),
                    ('VICE_PRESIDENT', 'Vice-Président'),
                    ('SECRETAIRE_GENERAL', 'Secrétaire Général'),
                    ('TRESORIER', 'Trésorier'),
                    ('DIRECTEUR', 'Directeur'),
                    ('PARTENAIRE', 'Partenaire'),
                    ('BENEVOLE', 'Bénévole'),
                    ('MEMBRE_HONNEUR', "Membre d'Honneur"),
                ],
                default='MEMBRE',
                help_text="Type de membre dans l'organisation",
                max_length=30,
                verbose_name='Catégorie de membre'
            ),
        ),
        migrations.AddField(
            model_name='membre',
            name='niveau_acces',
            field=models.CharField(
                choices=[
                    ('BASIQUE', 'Accès Basique'),
                    ('STANDARD', 'Accès Standard'),
                    ('PRIVILEGIE', 'Accès Privilégié'),
                    ('COMPLET', 'Accès Complet'),
                ],
                default='BASIQUE',
                help_text="Niveau d'accès aux ressources de l'organisation",
                max_length=20,
                verbose_name="Niveau d'accès"
            ),
        ),
        migrations.AddField(
            model_name='membre',
            name='statut',
            field=models.CharField(
                choices=[
                    ('ACTIF', 'Actif'),
                    ('SUSPENDU', 'Suspendu'),
                    ('EXPIRE', 'Expiré'),
                    ('REVOQUE', 'Révoqué'),
                ],
                default='ACTIF',
                help_text='État actuel du badge',
                max_length=20,
                verbose_name='Statut du badge'
            ),
        ),
        migrations.AddField(
            model_name='membre',
            name='date_expiration',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Date d'expiration"
            ),
        ),
        migrations.AddField(
            model_name='membre',
            name='derniere_modification',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='Dernière modification'
            ),
        ),
        migrations.AddField(
            model_name='membre',
            name='departement',
            field=models.CharField(
                blank=True,
                default='',
                max_length=100,
                verbose_name='Département'
            ),
        ),
        migrations.AddField(
            model_name='membre',
            name='notes',
            field=models.TextField(
                blank=True,
                default='',
                verbose_name='Notes internes'
            ),
        ),
        migrations.AlterField(
            model_name='membre',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name='Date de création'
            ),
        ),
        migrations.AlterModelOptions(
            name='membre',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Membre',
                'verbose_name_plural': 'Membres'
            },
        ),
    ]