from django.core.management.base import BaseCommand
from sorting.models import Socket, BagType


class Command(BaseCommand):
    help = 'Populate Socket and BagType objects from predefined lists'

    def handle(self, *args, **options):
        # Create Sockets
        sockets_data = [
            ('SEP_COT', 'COT', '#FF5733', 'Separator'),
            ('SEP_COT2', 'COT 2 Opole', '#33FF57', 'Separator'),
            ('SEP_BANDERAS', 'Banderas', '#5733FF', 'Separator'),
            ('SEP_ALF', 'Alf', '#FF33F5', 'Separator'),
            ('SEP_SELLPY', 'Sellpy', '#F5FF33', 'Separator'),
            ('SEP_CHARITY', 'Charity', '#33F5FF', 'Separator'),
            ('SEP_POSKLEPOWKA', 'Posklepówka', '#FF8C33', 'Separator'),
            ('PL_1', 'PL_1', '#8A2BE2', 'Poland Area 1'),
            ('PL_2', 'PL_2', '#20B2AA', 'Poland Area 2'),
            ('AF', 'AF', '#DC143C', 'Africa')
        ]

        for socket_id, socket_name, color, location in sockets_data:
            socket, created = Socket.objects.get_or_create(
                socket_id=socket_id,
                defaults={
                    'socket_name': socket_name,
                    'socket_color': color,
                    'location': location,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created socket: {socket_name}')
            else:
                self.stdout.write(f'Socket already exists: {socket_name}')

        # Get sockets for BagType assignment
        pl_1_socket = Socket.objects.get(socket_id='PL_1')
        pl_2_socket = Socket.objects.get(socket_id='PL_2')
        af_socket = Socket.objects.get(socket_id='AF')

        # PL_1 BagTypes
        pl_1_items = [
            ('bluzy', 'BLZ', 'bluzy', True),  # (X) - both parameters
            ('piżamy', 'PJM', 'piżamy', True),  # (X) - both parameters
            ('polary', 'PLR', 'polary', True),  # (X) - both parameters
            ('koszule', 'KSZ', 'koszule', False),
            ('bawełna długi rękaw', 'BDR', 'bawełna długi rękaw', True),  # (X) - both parameters
            ('vintage', 'VTG', 'vintage', False),
            ('karnawał', 'KRN', 'karnawał', False)
        ]

        for i, (name, code, description, has_x) in enumerate(pl_1_items, 1):
            parameter = 'Standard,Extra' if has_x else 'Standard'
            bag_type, created = BagType.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'parameter': parameter,
                    'order': i * 10,  # 10, 20, 30, etc.
                    'bag_source': 'IN',
                    'socket': pl_1_socket,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created BagType: {name} for PL_1')

        # PL_2 BagTypes
        pl_2_items = [
            ('mix lato', 'MLT', 'mix lato', False),
            ('mix zima', 'MZM', 'mix zima', False),
            ('płaszcze', 'PLZ', 'płaszcze', False),
            ('futra', 'FTR', 'futra', False),
            ('domowe', 'DOM', 'domowe', False),
            ('XL', 'XL', 'XL', True),  # (X) - both parameters
            ('kids sort', 'KDS', 'kids sort', False),
            ('denim', 'DNM', 'denim', False),
            ('spodnie extra', 'SPE', 'spodnie extra', False),
            ('legginsy', 'LGS', 'legginsy', True)  # (X) - both parameters
        ]

        for i, (name, code, description, has_x) in enumerate(pl_2_items, 100):
            parameter = 'Standard,Extra' if has_x else 'Standard'
            bag_type, created = BagType.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'parameter': parameter,
                    'order': i,  # 100, 101, 102, etc.
                    'bag_source': 'OUT',
                    'socket': pl_2_socket,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created BagType: {name} for PL_2')

        # AF BagTypes
        af_items = [
            ('A Grade', 'AGR', 'A Grade', False),
            ('B Grade', 'BGR', 'B Grade', False),
            ('Pakistan', 'PAK', 'Pakistan', False),
            ('Buty', 'BTY', 'Buty', False)
        ]

        for i, (name, code, description, has_x) in enumerate(af_items, 200):
            parameter = 'Standard,Extra' if has_x else 'Standard'
            bag_type, created = BagType.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'parameter': parameter,
                    'order': i,  # 200, 201, 202, etc.
                    'bag_source': 'IN',
                    'socket': af_socket,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created BagType: {name} for AF')

        self.stdout.write(self.style.SUCCESS('Successfully populated all data!'))