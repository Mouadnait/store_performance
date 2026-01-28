from django.core.management.base import BaseCommand
from core.models import Client


class Command(BaseCommand):
    help = 'Enable GPT-5.2-Codex for all clients'

    def handle(self, *args, **kwargs):
        # Update all clients to enable GPT-5.2-Codex
        clients = Client.objects.all()
        total_clients = clients.count()
        
        if total_clients == 0:
            self.stdout.write(self.style.WARNING('No clients found in the database.'))
            return
        
        # Enable GPT for all clients
        updated_count = clients.update(gpt5_enabled=True)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully enabled GPT-5.2-Codex for {updated_count} out of {total_clients} clients.'
            )
        )
        
        # Show summary
        enabled_clients = Client.objects.filter(gpt5_enabled=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'  Total Clients: {total_clients}\n'
                f'  GPT Enabled: {enabled_clients}\n'
                f'  GPT Disabled: {total_clients - enabled_clients}'
            )
        )
