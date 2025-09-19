from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from colorfield.fields import ColorField
from multiselectfield import MultiSelectField


class Socket(models.Model):
    socket_id = models.CharField(max_length=50, unique=True)
    socket_name = models.CharField(max_length=50)
    socket_color = ColorField(default='#010101')
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    # Users who have access to this socket
    users = models.ManyToManyField(User, blank=True, related_name='accessible_sockets')

    def __str__(self):
        return f"{self.socket_id} - {self.socket_name }"

    class Meta:
        ordering = ['socket_id']


class BagTypeCategory(models.Model):
    """Categories for organizing bag subtypes (e.g., Basic Clothing, Outerwear, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = ColorField(default='#87CEEB', help_text="Background color for this category")
    icon = models.CharField(max_length=50, default='fas fa-layer-group', 
                           help_text="FontAwesome icon class (e.g., 'fas fa-tshirt')")
    order = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(1000)],
                               help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Bag Type Category'
        verbose_name_plural = 'Bag Type Categories'


class BagType(models.Model):
    PARAMETER_CHOICES = [
        ('Standard', 'Standard'),
        ('Extra', 'Extra'),
    ]

    BAG_SOURCE_CHOICES = [
        ('IN', 'IN'),
        ('OUT', 'OUT'),
    ]

    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    color = ColorField(default='#808080')
    parameter = MultiSelectField(max_length=50, choices=PARAMETER_CHOICES, blank=True, null=True)
    order = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000)])
    bag_source = models.CharField(max_length=3, choices=BAG_SOURCE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    socket = models.ForeignKey(Socket, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class SortingPerson(models.Model):
    name = models.CharField(max_length=100)
    person_id = models.CharField(max_length=20, unique=True)
    person_color = ColorField(default='#000000')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.person_id})"

    class Meta:
        ordering = ['name']


class BagSubtype(models.Model):
    """Subtypes for specific bag types (e.g., A Grade, B Grade)"""
    bag_type = models.ForeignKey(BagType, on_delete=models.CASCADE, related_name='subtypes')
    category = models.ForeignKey(BagTypeCategory, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='subtypes', help_text="Category for organizing this subtype")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_color(self):
        """Return the color from the assigned category, or a default if no category"""
        if self.category:
            return self.category.color
        return '#808080'  # Default gray for uncategorized items

    def __str__(self):
        return f"{self.bag_type.name} - {self.name}"

    class Meta:
        ordering = ['name']  # Sort alphabetically by name
        unique_together = ['bag_type', 'name']


class Bag(models.Model):
    QUALITY_GRADES = [
        ('A', 'Klasa A'),
        ('B', 'Klasa B'),
        ('C', 'Klasa C'),
    ]

    bag_id = models.CharField(max_length=50, unique=True)
    socket = models.ForeignKey(Socket, on_delete=models.CASCADE, related_name='bags')
    sorting_person = models.ForeignKey(SortingPerson, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='sorted_bags')
    bag_type = models.ForeignKey(BagType, on_delete=models.PROTECT, related_name='bags')
    bag_subtype = models.ForeignKey(BagSubtype, on_delete=models.SET_NULL, null=True, blank=True, related_name='bags')
    quality_grade = models.CharField(max_length=1, choices=QUALITY_GRADES, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    item_count = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)
    extra = models.BooleanField(default=False, help_text="Prawda jeśli wybrano parametr Dodatkowy")
    notes = models.TextField(blank=True)
    # Time tracking for Separator IN bags
    bag_source = models.CharField(max_length=3, blank=True, help_text="IN or OUT for SEP socket")
    processing_time_seconds = models.IntegerField(null=True, blank=True, help_text="Time spent in separator (seconds)")
    auto_processed_by_next_bag = models.BooleanField(default=False, help_text="True if automatically processed by next bag")
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Handle automatic processing for Separator IN bags
        if not self.pk:  # New bag being created
            self._handle_separator_processing()
        
        if self.is_processed and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)

    def _handle_separator_processing(self):
        """Handle automatic processing logic for Separator IN bags"""
        if (self.socket.socket_id == 'SEP' and 
            self.bag_source == 'IN'):
            
            # Find the most recent pending Separator IN bag
            previous_bag = Bag.objects.filter(
                socket__socket_id='SEP',
                bag_source='IN',
                is_processed=False
            ).order_by('-received_at').first()
            
            if previous_bag:
                # Calculate processing time for the previous bag
                time_diff = timezone.now() - previous_bag.received_at
                previous_bag.processing_time_seconds = int(time_diff.total_seconds())
                previous_bag.is_processed = True
                previous_bag.auto_processed_by_next_bag = True
                previous_bag.save()

    def get_processing_duration(self):
        """Get human-readable processing duration"""
        if not self.processing_time_seconds:
            return None
        
        hours = self.processing_time_seconds // 3600
        minutes = (self.processing_time_seconds % 3600) // 60
        seconds = self.processing_time_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def is_separator_in_bag(self):
        """Check if this is a Separator IN bag"""
        return self.socket.socket_id == 'SEP' and self.bag_source == 'IN'

    @classmethod
    def generate_next_bag_id(cls):
        """Generate the next sequential bag ID"""
        from django.db import transaction
        
        with transaction.atomic():
            # Get all existing bag numbers to find the highest
            existing_bags = cls.objects.filter(
                bag_id__startswith='BAG_'
            ).values_list('bag_id', flat=True)
            
            existing_numbers = []
            for bag_id in existing_bags:
                try:
                    # Extract number from bag ID (e.g., "BAG_000023" -> 23)
                    number = int(bag_id.split('_')[1])
                    existing_numbers.append(number)
                except (ValueError, IndexError):
                    continue
            
            # Find the next available number
            if existing_numbers:
                next_number = max(existing_numbers) + 1
            else:
                next_number = 1
            
            # Ensure uniqueness by checking if this ID already exists
            while cls.objects.filter(bag_id=f"BAG_{next_number:06d}").exists():
                next_number += 1
            
            # Format with leading zeros (6 digits)
            return f"BAG_{next_number:06d}"

    def __str__(self):
        return f"Bag {self.bag_id} - {self.bag_type.name}"

    class Meta:
        ordering = ['-received_at']



class SortedBag(models.Model):
    DESTINATION_CHOICES = [
        ('retail', 'Sklep Detaliczny'),
        ('outlet', 'Outlet'),
        ('donation', 'Centrum Darowizn'),
        ('recycling', 'Zakład Recyklingu'),
        ('disposal', 'Utylizacja'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Oczekuje na Wysyłkę'),
        ('shipped', 'Wysłane'),
        ('delivered', 'Dostarczone'),
        ('returned', 'Zwrócone'),
    ]

    original_bag = models.OneToOneField(Bag, on_delete=models.CASCADE, related_name='sorted_bag')
    destination = models.CharField(max_length=20, choices=DESTINATION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    final_quality_check = models.BooleanField(default=False)
    packaging_notes = models.TextField(blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status == 'shipped' and not self.shipped_at:
            self.shipped_at = timezone.now()
        elif self.status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SortedBag {self.original_bag.bag_id} -> {self.get_destination_display()}"

    class Meta:
        ordering = ['-created_at']
