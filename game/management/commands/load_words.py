from django.core.management.base import BaseCommand
from game.models import Word

class Command(BaseCommand):
    help = "Load initial 20 five-letter words into Word table (uppercase)."

    def handle(self, *args, **options):
        words = [
            "APPLE","BRAVE","CRANE","DREAM","ELITE",
            "FRAME","GLASS","HOUSE","IMAGE","JUMPY",
            "KNIFE","LIGHT","MONEY","NURSE","OCEAN",
            "PILOT","QUERY","RIVER","STONE","TRACK"
        ]
        created = 0
        for w in words:
            obj, created_flag = Word.objects.get_or_create(text=w)
            if created_flag:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Loaded/verified {len(words)} words. New created: {created}'))
