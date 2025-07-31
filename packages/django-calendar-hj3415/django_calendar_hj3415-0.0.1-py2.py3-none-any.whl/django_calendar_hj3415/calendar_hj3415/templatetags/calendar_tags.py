from django import template
from django.utils import timezone
from datetime import date

register = template.Library()

@register.inclusion_tag("calendar_hj3415/modal.html", takes_context=True)
def calendar_modal(context, modal_id="bsmcModal", year=None, month=None, auto_open=False, title="일정"):
    today = timezone.localdate() if hasattr(timezone, "localdate") else date.today()
    year = year or today.year
    month = month or today.month
    return {
        "modal_id": modal_id,
        "year": year,
        "month": month,
        "auto_open": auto_open,
        "title": title,
        "request": context.get("request"),
    }

@register.filter
def get_item(d, key):
    return d.get(key, [])