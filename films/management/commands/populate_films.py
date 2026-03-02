import csv
from django.core.management.base import BaseCommand
from films.models import Film

class Command(BaseCommand):
    help = 'Populates the Film model with initial data from a TSV file'

    def add_arguments(self, parser):
        # On définit l'argument pour passer le chemin du fichier TSV [cite: 65, 66]
        parser.add_argument('file', type=str, help='Path to the TSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']
        try:
            with open(file_path, newline='', encoding='utf-8') as tsvfile:
                # DictReader avec le délimiteur tabulation (\t) [cite: 72, 73]
                reader = csv.DictReader(tsvfile, delimiter='\t')
                for row in reader:
                    try:
                        # get_or_create évite de créer des doublons [cite: 76, 78]
                        film, created = Film.objects.get_or_create(
                            title=row['title'],
                            release_year=int(row['release_year'])
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Created film: {film.title}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Film already exists: {film.title}"))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Could not create film: {row['title']}"))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))