from django.db import models

class Employee(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    position = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    hire_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
