from django import forms
from datetime import date
from models import Enrollment

class EnrollmentForm(forms.Form):
    key = forms.CharField(label="Enrollment key", max_length=32)
    for_credit = forms.BooleanField(label="For credit", required=False)

    def __init__(self, user, course, *args, **kwargs):
        self.user = user
        self.course = course
        # Assume for_credit, unless this semester is over
        initial = {'for_credit':
                       date.today() < course.semester.end_date}
        super(EnrollmentForm, self).__init__(*args, initial=initial, **kwargs)
# 2fdc422

    def clean_key(self):
        key = self.cleaned_data['key']
        if key != self.course.key:
            raise forms.ValidationError(
                """That is not the correct enrollment key for this course."""
                )
        return key

    def save(self, commit=True):
        e = Enrollment(course=self.course, user=self.user,
                       kind='G' if self.cleaned_data['for_credit'] else 'A')
        self.user.groups.add(self.course.group) # does this save?
        if commit:
            e.save()
        return e
