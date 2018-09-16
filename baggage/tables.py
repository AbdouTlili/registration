import django_filters
import django_tables2 as tables
from baggage.models import Bag, BAG_STATUS, BAG_ADDED, BAG_BUILDINGS
from user.models import User
from django.db.models import Q
from django import forms
from datetime import datetime, timedelta
from django.db.models import CharField, Value, F
from django.db.models.functions import Concat

class BaggageListFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    #status = django_filters.ChoiceFilter('status', label='Status', choices=BAG_STATUS,
    #                                             widget=forms.RadioSelect, empty_label='Any', initial=BAG_ADDED)
    room = django_filters.ChoiceFilter(label='Room', choices=BAG_BUILDINGS, empty_label='Any')
    time_from = django_filters.DateTimeFilter(method='search_time', label='Time from', widget=forms.DateTimeInput(attrs={'class': 'field-left'}), initial=datetime.now()-timedelta(1))
    time_to = django_filters.DateTimeFilter(method='search_time', label='Time to', widget=forms.DateTimeInput(attrs={'class': 'field-right'}), initial=datetime.now())

    def search_filter(self, queryset, name, value):
        return queryset.annotate(fullpos=Concat('room', 'row', 'col', output_field=CharField())).filter((Q(owner__email__icontains=value) | Q(owner__name__icontains=value) |
            Q(status__icontains=value) | Q(type__icontains=value) | Q(color__icontains=value) | Q(description__icontains=value) |
            Q(fullpos__icontains=value)))

    def search_time(self, queryset, name, value):
        if name == 'time_from':
            return queryset.filter(Q(time__gte=value))
        return queryset.filter(Q(time__lte=value))

    class Meta:
        model = Bag
        fields = ['search']

class BaggageListTable(tables.Table):
    checkout = tables.TemplateColumn(
        "<a href='{% url 'baggage_detail' record.id %}'>Detail</a> ",
        verbose_name='Actions', orderable=False)
    
    position = tables.Column(accessor='position', verbose_name='Position')
    
    class Meta:
        model = Bag
        attrs = {'class': 'table table-hover'}
        template = 'templates/baggage_list.html'
        fields = ['id', 'room', 'position', 'owner', 'type', 'description', 'special']
        empty_text = 'No baggage items checked-in'

class BaggageUsersTable(tables.Table):
    checkout = tables.TemplateColumn(
        "<a href='{% url 'baggage_new' record.id %}'>Baggage check-in</a> ",
        verbose_name='Actions', orderable=False)
    
    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'templates/baggage_users.html'
        fields = ['name', 'email']
        empty_text = 'No users'
