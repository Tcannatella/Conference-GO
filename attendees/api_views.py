from django.http import JsonResponse
from .models import Attendee
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
from events.models import Conference
import json

class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name",
        "email",
        "company_name",
        "created",
        "conference",
    ]

    def get_extra_data(self, o):
        return { "conference": o.conference.id }

class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]

@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    """
    Lists the attendees names and the link to the attendee
    for the specified conference id.

    Returns a dictionary with a single key "attendees" which
    is a list of attendee names and URLS. Each entry in the list
    is a dictionary that contains the name of the attendee and
    the link to the attendee's information.
     """
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        return JsonResponse(
                {"attendees": attendees},
                encoder=AttendeeListEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )

@require_http_methods(["GET", "DELETE", "PUT"])
def api_show_attendee(request, id):
    """
    Returns the details for the Attendee model specified
    by the id parameter.

    This should return a dictionary with email, name,
    company name, created, and conference properties for
    the specified Attendee instance.
    """
    # attendees = Attendee.objects.get(id=id)

    # return JsonResponse(
    #     {
    #     "email": attendees.email,
    #     "name": attendees.name,
    #     "company_name": attendees.company_name,
    #     "created": attendees.created,
    #     "conference": {
    #         "name": attendees.conference.name,
    #         "href": attendees.conference.get_api_url()
    #     }
    # }
    # )

    if request.method == "GET":
        attendees = Attendee.objects.get(id=id)
        return JsonResponse(
                attendees,
                encoder=AttendeeDetailEncoder,
                safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=content["conference"])
            content["conference"] = conference
        except Attendee.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
        )
        Attendee.objects.filter(id=id).update(**content)
        attendees = Attendee.objects.get(id=id)
        return JsonResponse(
            attendees,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
