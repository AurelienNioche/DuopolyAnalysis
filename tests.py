from django.test import TestCase
from game.models import Room, Round, FirmPosition, FirmPrice, FirmProfit, RoundComposition, RoundState

from tqdm import tqdm

class AnimalTestCase(TestCase):
    def merge(self):
        for table in tqdm(Room, Round, FirmPosition, FirmPrice, FirmProfit, RoundComposition, RoundState):

            entries = table.objects.all().using('old')

            # new_entries = []
            for e in entries:
                new_e = table()
                #new_e = table(**e.__dict__)
                new_e.save()