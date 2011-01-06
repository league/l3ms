from datetime import date
from django import forms
from models import Enrollment
from strings import *

class EnrollmentForm(forms.Form):
    key = forms.CharField(label=LABEL_KEY, max_length=32)
    for_credit = forms.BooleanField(label=LABEL_FOR_CREDIT, required=False)

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
            raise forms.ValidationError(M_INCORRECT_KEY)
        return key

    def save(self, commit=True):
        e = Enrollment(course=self.course, user=self.user,
                       kind='G' if self.cleaned_data['for_credit'] else 'A')
        self.user.groups.add(self.course.group) # does this save?
        if commit:
            e.save()
        return e

class CourseOptionsForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        exclude = ['course', 'user', 'kind']
