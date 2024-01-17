from django.http import JsonResponse
from .models import Presentation
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json

class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
        "status",
        "href"
    ]

class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
    ]

@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    """
    Lists the presentation titles and the link to the
    presentation for the specified conference id.

    Returns a dictionary with a single key "presentations"
    which is a list of presentation titles and URLS. Each
    entry in the list is a dictionary that contains the
    title of the presentation, the name of its status, and
    the link to the presentation's information.

    {
        "presentations": [
            {
                "title": presentation's title,
                "status": presentation's status name
                "href": URL to the presentation,
            },
            ...
        ]
    }
    """
    # presentations = [
    #     {
    #         "title": p.title,
    #         "status": p.status.name,
    #         "href": p.get_api_url(),
    #     }
    #     for p in Presentation.objects.filter(conference=conference_id)
    # ]
    # return JsonResponse({"presentations": presentations})

    if request.method == "GET":
        presentation = Presentation.objects.all()
        return JsonResponse(
            {"presentation": presentation},
            encoder=PresentationDetailEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the Presentatio object and put it in the content dict
        try:
            presentation = Presentation.objects.get(id=content["presentation"])
            content["presentation"] = presentation
        except Presentation.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )

        presentation = Presentation.objects.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["GET","DELETE","PUT"])
def api_show_presentation(request, id):
    """
    Returns the details for the Presentation model specified
    by the id parameter.

    This should return a dictionary with the presenter's name,
    their company name, the presenter's email, the title of
    the presentation, the synopsis of the presentation, when
    the presentation record was created, its status name, and
    a dictionary that has the conference name and its URL
    """

    # presentation = Presentation.objects.get(id=id)
    # return JsonResponse(
    #     presentation,
    #     encoder=PresentationDetailEncoder,
    #     safe=False,
    # )

    if request.method == "GET":
        location = Presentation.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        # copied from create
        content = json.loads(request.body)
        try:
            # new code
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except Presentation.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )
