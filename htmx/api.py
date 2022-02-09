from django.http import HttpResponse
from django.utils.safestring import mark_safe
from ninja import Router
from django import template

router = Router(tags=['htmx'])


@router.get("/hello", include_in_schema=False)
def hello(request):
    return "Hello"


@router.get("/contact/1/edit")
def add(request):
    t = template.Template("""
<form hx-put="/contact/1" hx-target="this" hx-swap="outerHTML">
  <div>
    <label>First Name</label>
    <input type="text" name="firstName" value="Joe">
  </div>
  <div class="form-group">
    <label>Last Name</label>
    <input type="text" name="lastName" value="Blow">
  </div>
  <div class="form-group">
    <label>Email Address</label>
    <input type="email" name="email" value="joe@blow.com">
  </div>
  <button class="btn">Submit</button>
  <button class="btn" hx-get="/contact/1">Cancel</button>
</form> 
""")
    html = t.render(template.Context({}))
    return HttpResponse(html)
