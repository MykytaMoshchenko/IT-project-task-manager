from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from tasks.models import Worker, Task, Position


class DateInput(forms.DateInput):
    input_type = 'date'


def validate_position(position):
    if position not in Position.objects.all():
        raise ValidationError(
            "Position must be one of the defined in the Task Manager"
        )

    return position


class WorkerCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "position",
            "first_name",
            "last_name",
        )


class AssigneesForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["assignees"]

    def clean_position(self):
        return validate_position(self.cleaned_data["assignees"])


class WorkerPositionUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["position"]

    def clean_position(self):
        return validate_position(self.cleaned_data["position"])


class WorkerSearchForm(forms.Form):
    username = forms.CharField(
        max_length=44,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by username"})
    )


class TaskSearchForm(forms.Form):
    name = forms.CharField(
        max_length=44,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by task name"})
    )
