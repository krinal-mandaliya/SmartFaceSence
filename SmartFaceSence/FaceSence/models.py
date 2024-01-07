from django.db import models
from django.utils import timezone

# Create your models here.
class Signup(models.Model):
    name_office=models.CharField(max_length=100,default=None)
    name_head=models.CharField(max_length=100,default=None)
    address=models.CharField(max_length=256,default=None)
    email_admin=models.CharField(max_length=256,default=None)
    password=models.CharField(max_length=30)
    
    def __str__(self):
        return self.name_office
    
class Image(models.Model):
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    scan_image = models.ImageField(upload_to='captured_faces/', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
         return self.image
    
class Person(models.Model):
    person_name = models.CharField(max_length=100, default=None)
    dob = models.DateField(default=None)
    face_image = models.ImageField(upload_to='person/', blank=True, null=True)
    doj = models.DateField(default=None)
    scan_image = models.ImageField(upload_to='person-scan/', blank=True, null=True)
    person_email = models.CharField(max_length=256, default=None)
    phoneno = models.CharField(max_length=13, default=None)
    time = models.DateTimeField(default=timezone.now)
    type_person = models.CharField(max_length=20, default=None, blank=False, null=False)

    class Meta:
        # Add unique constraint for person_name, dob, and doj
        unique_together = ['person_name', 'dob', 'doj']

    def save(self, *args, **kwargs):
    # Set the 'time' field to the current server time before saving
        self.time = timezone.now()

    # Check if dob and doj are not None before saving
        if self.dob is None or self.doj is None or self.person_name is None:
            raise ValueError("Person Name, Date of Birth (dob), and Date of Joining (doj) cannot be None.")

        super().save(*args, **kwargs)


    def __str__(self):
        return self.person_name
    
class Flat(models.Model):
    block_no=models.CharField(max_length=2)
    total_floor=models.CharField(max_length=3)
    flat_no=models.CharField(max_length=3)
    flat_type=models.CharField(max_length=5)
    status=models.CharField(max_length=5)
    alloted_to=models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.block_no
    
class Visitor(models.Model):
    visitor_name=models.CharField(max_length=256)
    mobile_no=models.IntegerField()
    address=models.CharField(max_length=256)
    visitor_image=models.ImageField(upload_to='visitors/',default=None)
    flat_id=models.ForeignKey(Flat, on_delete=models.CASCADE)
    whome_to_meet=models.ForeignKey(Person, on_delete=models.CASCADE)
    entry_time=models.DateTimeField(default=timezone.now)
    proof=models.CharField(max_length=20)
    
    def __str__(self) -> str:
        return self.visitor_name
    def save(self, *args, **kwargs):
        # If the entry_time is not provided, set it to the current time
        if not self.entry_time:
            self.entry_time = timezone.now()

        super().save(*args, **kwargs)

class Profile(models.Model):
    signup = models.OneToOneField(Signup, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.signup.name_office