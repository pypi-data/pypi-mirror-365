from django.db import models

BOOTSTRAP_VARIANTS = [
    ("primary", "Primary"),
    ("secondary", "Secondary"),
    ("success", "Success"),
    ("danger", "Danger"),
    ("warning", "Warning"),
    ("info", "Info"),
    ("light", "Light"),
    ("dark", "Dark"),
]

class Event(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # 없으면 단일일정
    url = models.URLField(blank=True)
    # 두 가지 방식 중 하나로 색상 설정:
    color_variant = models.CharField(max_length=16, choices=BOOTSTRAP_VARIANTS, blank=True)
    color_hex = models.CharField(max_length=9, blank=True, help_text="#RRGGBB 또는 #RRGGBBAA (선택)")

    class Meta:
        ordering = ["start_date", "title"]

    def __str__(self):
        return self.title

    @property
    def effective_end(self):
        return self.end_date or self.start_date