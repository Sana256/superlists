from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.generic import FormView, CreateView
from django.utils.html import escape
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm


class HomePageView(FormView):
    template_name = 'home.html'
    form_class = ItemForm


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)
    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)
    return render(request, 'list.html', {'list': list_, 'form': form})


def new_list(request):
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List()
        if request.user.is_authenticated:
            list_.owner = request.user
        list_.save()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        return render(request, 'home.html', {"form": form})


def my_lists(request, email):
    owner = User.objects.get(email=email)
    shared_with = List.objects.filter(owner=owner).filter(shared_with__isnull=False).distinct()
    shared_from = List.objects.filter(shared_with=owner)
    return render(request, 'my_lists.html', {'owner': owner, 'shared_with': shared_with, 'shared_from': shared_from})


def share_list(request, list_id):
    email = request.POST['email']
    list_ = List.objects.get(id=list_id)
    try:
        user = User.objects.get(email=email)
        list_.shared_with.add(user)
        messages.success(request, f'List shared with user: {user.email}')
        return redirect(list_)
    except User.DoesNotExist:
        messages.error(request, f'User {email} does not exist')
        return redirect(list_)
