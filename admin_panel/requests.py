from starlette.templating import Jinja2Templates


async def confirm_post(request):
    return Jinja2Templates("templates").TemplateResponse(
        "index.html", {"request": request}
    )
