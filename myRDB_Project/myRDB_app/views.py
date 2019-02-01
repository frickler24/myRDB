import csv
import json
import re

from json2html import *
import requests
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render
import datetime

# from django_filters.rest_framework import DjangoFilterBackend
from mongoengine import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from .filters import UserFilter
from .forms import CustomUserCreationForm, SomeForm
from .models import Role, AF, GF, TF, Orga, Group, Department, ZI_Organisation, TF_Application, User_AF, User_TF, \
    User_GF
from rest_framework import viewsets
from .serializers import UserSerializer, RoleSerializer, AFSerializer, GFSerializer, TFSerializer, OrgaSerializer, \
    GroupSerializer, DepartmentSerializer, ZI_OrganisationSerializer, TF_ApplicationSerializer, UserListingSerializer, \
    CompleteUserListingSerializer
from django.views import generic

from django.contrib.auth import get_user_model

User = get_user_model()


class CSVtoMongoDB(generic.FormView):
    template_name = 'myRDB/csvToMongo.html'
    form_class = SomeForm
    success_url = '#'

    def form_valid(self, form):
        self.start_import_action()
        return super().form_valid(form)

    def start_import_action(self):
        firstline = True
        # TODO: dateiimportfield und pfad müssen noch verbunden werden!
        with open("myRDB_app/static/myRDB/data/Aus IIQ - User und TF komplett Neu_20180817.csv") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for line in csvreader:
                if firstline == True:
                    firstline = False
                    pass
                else:
                    print(line)
                    orga = None
                    try:
                        orga = Orga.objects.get(team=line[8])
                    except(KeyError, Orga.DoesNotExist):
                        orga = Orga(team=line[8])
                    orga.save()

                    #
                    tf_application = None
                    try:
                        tf_application = TF_Application.objects.get(application_name=line[9])
                    except(KeyError, TF_Application.DoesNotExist):
                        tf_application = TF_Application(application_name=line[9])
                    tf_application.save()

                    tf = None
                    try:
                        tf = TF.objects.get(tf_name=line[3])
                    except(KeyError, TF.DoesNotExist):
                        tf = TF(tf_name=line[3], tf_description=line[4], highest_criticality_in_AF=line[7],
                                tf_owner_orga=orga, tf_application=tf_application, criticality=line[10])
                    tf.save()

                    gf = None
                    try:
                        gf = GF.objects.get(gf_name=line[11])
                    except(KeyError, GF.DoesNotExist):
                        gf = GF(gf_name=line[11], gf_description=line[12])
                        gf.save()
                    gf.tfs.add(tf)
                    gf.save()

                    af = None
                    try:
                        af = AF.objects.get(af_name=line[5])
                    except(KeyError, AF.DoesNotExist):
                        # TODO: Daten werden noch nicht korreckt eingetragen -> immer Null

                        if line[15] == "" and line[16] == "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6])
                        if line[15] != "" and line[16] == "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat())
                        if line[15] != "" and line[16] != "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat()
                                    , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat())
                        if line[15] != "" and line[16] != "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6],
                                    af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat(),
                                    af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat(),
                                    af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                        if line[15] == "" and line[16] != "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat()
                                    , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                        if line[15] == "" and line[16] == "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                    af.save()
                    af.gfs.add(gf)

                    user = None
                    try:
                        user = User.objects.get(identity=line[0])
                        if user.name != line[1]:
                            user.name = line[1]
                        if user.first_name != line[2]:
                            user.first_name = line[2]
                        if user.username != line[0]:
                            user.username = line[0]
                    except(KeyError, User.DoesNotExist):
                        user = User(identity=line[0], name=line[1], first_name=line[2], username=line[0])
                        if not user.orga:
                            user.orga = Orga()
                        if not user.group:
                            user.group = Group()
                        if not user.department:
                            user.department = Department()
                        if not user.zi_organisation:
                            user.zi_organisation = ZI_Organisation()
                        if not user.roles:
                            user.roles = [Role()]
                        if not user.direct_connect_afs:
                            user.direct_connect_afs = [AF()]
                        if not user.direct_connect_gfs:
                            user.direct_connect_gfs = [GF()]
                        if not user.direct_connect_tfs:
                            user.direct_connect_tfs = [TF()]
                        if not user.user_afs:
                            user.user_afs = []
                    if user.user_afs.__len__() == 0:
                        user_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk)
                        user_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk, tfs=[])
                        user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[])
                        user_gf.tfs.append(user_tf)
                        user_af.gfs.append(user_gf)
                        user.user_afs.append(user_af)
                    else:
                        afcount = 0
                        for uaf in user.user_afs:
                            if uaf.af_name != af.af_name:
                                afcount += 1
                            else:
                                gfcount = 0
                                for ugf in uaf.gfs:
                                    if ugf.gf_name != gf.gf_name:
                                        gfcount += 1
                                    else:
                                        tfcount = 0
                                        for utf in ugf.tfs:
                                            if utf.tf_name != tf.tf_name:
                                                tfcount += 1
                                            else:
                                                break
                                        if tfcount == ugf.tfs.__len__():
                                            ugf.tfs.append(User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk))
                                if gfcount == uaf.gfs.__len__():
                                    uaf.gfs.append(User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk,
                                                           tfs=[User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk)]))
                        if afcount == user.user_afs.__len__():
                            user.user_afs.append(User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[
                                User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk,
                                        tfs=[User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk)])]))

                    user.direct_connect_afs.add(af)
                    user.save()


class Login(generic.TemplateView):
    template_name = 'myRDB/registration/login.html'


class Logout(generic.TemplateView):
    template_name = 'myRDB/registration/logout.html'


class Register(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = '/myRDB/login'
    template_name = 'myRDB/registration/register.html'


class Password_Reset(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_form.html'


class Password_Reset_Done(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_done.html'


class Password_Reset_Confirm(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_confirm.html'


class Password_Reset_Complete(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_complete.html'


class IndexView(generic.ListView):
    template_name = 'myRDB/index.html'
    queryset = User.objects.all()

    def get_queryset(self):
        logged_in_user = self.request.user
        return Response({'user': logged_in_user})


class Search_All(generic.ListView):
    template_name = 'myRDB/search_all.html'
    extra_context = {}

    def get_queryset(self):
        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/searchlistings/'
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        lis = ['zi_organisations', 'orgas','tf_applications', 'departments', 'roles', 'groups']
        for e in lis:
            self.extra_context[e] = populate_choice_fields(headers, e)
        params, changed = build_url_params(self.request, self.extra_context)
        if 'entries_per_page' in self.request.GET:
            self.paginate_by = self.request.GET['entries_per_page']
            if self.paginate_by == '':
                self.paginate_by = 20
        else:
            self.paginate_by = 20
        if params == "":
            prefix = "?"
        else:
            prefix = "&"
        params = params + prefix + "entries_per_page=" + self.paginate_by.__str__()
        url = url + params

        if not self.extra_context.keys().__contains__('data') or changed == True:
            res = requests.get(url, headers=headers)
            user_json_data = res.json()
            self.extra_context['data'] = self.prepare_table_data(user_json_data, headers)
        self.extra_context['params_for_pagination'] = params
        return self.extra_context['data']

        # table=json2html.convert(json=user_json_data['results'])
        # print(table)
        # return Response(data=user_json_data, content_type='application/html')

    def prepare_table_data(self, json_data, headers):
        lines = []

        url = 'http://127.0.0.1:8000/tfs/'
        res = requests.get(url, headers=headers)
        tf_json_data = res.json()
        for user in json_data['results']:
            for af in user['user_afs']:
                if self.request.GET.keys().__contains__('af_name'):
                    if not af['af_name'].__contains__(self.request.GET['af_name']):
                        continue
                for gf in af['gfs']:
                    if self.request.GET.keys().__contains__('gf_name'):
                        if not gf['gf_name'].__contains__(self.request.GET['gf_name']):
                            continue
                    for tf in gf['tfs']:
                        if self.request.GET.keys().__contains__('tf_name'):
                            if not tf['tf_name'].__contains__(self.request.GET['tf_name']):
                                continue
                        model_tf = [x for x in tf_json_data['results'] if x['pk'] == tf['model_tf_pk']].pop(0)
                        line = [user['identity'], user['name'], user['first_name'], tf['tf_name'], gf['gf_name'],
                                af['af_name'],
                                model_tf['tf_owner_orga']['team'],
                                model_tf['tf_application']['application_name'], model_tf['tf_description'], '',
                                user['deleted']]
                        if self.extra_context.keys().__contains__('tf_owner_orga') and self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_owner_orga']['team'] == self.request.GET['tf_owner_orga'] and model_tf['tf_application']['application_name']==self.request.GET['tf_application']:
                                lines.append(line)
                        elif self.extra_context.keys().__contains__('tf_owner_orga') and not self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_owner_orga']['team'] == self.request.GET['tf_owner_orga']:
                                lines.append(line)
                        elif not self.extra_context.keys().__contains__('tf_owner_orga') and self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_application']['application_name']==self.request.GET['tf_application']:
                                lines.append(line)
                        else:
                            lines.append(line)
        return lines


class Users(generic.ListView):
    template_name = 'myRDB/users.html'
    extra_context = {}

    def get_queryset(self):
        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/userlistings/'
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        lis = ['zi_organisations', 'orgas', 'departments', 'roles', 'groups']
        for e in lis:
            self.extra_context[e] = populate_choice_fields(headers, e)
        params, changed = build_url_params(self.request, self.extra_context)
        if 'entries_per_page' in self.request.GET:
            self.paginate_by = self.request.GET['entries_per_page']
            if self.paginate_by == '':
                self.paginate_by = 10
        else:
            self.paginate_by = 10
        if params == "":
            prefix = "?"
        else:
            prefix = "&"
        params = params + prefix + "entries_per_page=" + self.paginate_by.__str__()
        url = url + params
        self.extra_context['params_for_pagination'] = params

        if changed == True or not self.extra_context.keys().__contains__('paginated_users'):
            res = requests.get(url, headers=headers)
            user_json_data = res.json()
            # user_count= user_json_data['count']
            users = {'users': user_json_data['results']}
            self.extra_context['paginated_users'] = users
        else:
            users = self.extra_context['paginated_users']
        response = Response(users)
        print(response.data['users'])

        user_paginator = Paginator(response.data['users'], self.paginate_by)
        page = self.request.GET.get('page')
        try:
            user_paged_data = user_paginator.page(page)
        except PageNotAnInteger:
            user_paged_data = user_paginator.page(1)
        except EmptyPage:
            user_paged_data = user_paginator.page(user_paginator.num_pages)

        self.extra_context['paged_data'] = user_paged_data
        return response.data['users']


def populate_choice_fields(headers, field):
    url = 'http://127.0.0.1:8000/' + field + '/'
    res = requests.get(url, headers=headers)
    json_data = res.json()
    results = {field: json_data['results']}
    response = Response(results)
    return response.data[field]


def build_url_params(request, extra_context):
    params = ""
    changed = False
    if 'userSearch' in request.GET:
        user_search = request.GET['userSearch']
        search_what = request.GET['search_what']
        if extra_context.keys().__contains__("user_search"):
            if user_search != extra_context["user_search"] or search_what != extra_context["search_what"]:
                changed = True
        else:
            changed = True
        extra_context["userSearch"] = user_search
        extra_context["search_what"] = search_what
        params = "?userSearch=" + user_search + "&search_what=" + search_what
    if 'zi_organisation' in request.GET:
        zi_organisation = '----'
        if not request.GET['zi_organisation'] == '----':
            zi_organisation = request.GET['zi_organisation']
            params = params + "&zi_organisation=" + zi_organisation
        if extra_context.keys().__contains__("zi_organisation"):
            if zi_organisation != extra_context["zi_organisation"]:
                changed = True
        else:
            changed = True
        extra_context["zi_organisation"] = zi_organisation
    if 'department' in request.GET:
        department = '----'
        if not request.GET['department'] == '----':
            department = request.GET['department']
            params = params + "&department=" + department
        if extra_context.keys().__contains__("department"):
            if department != extra_context["department"]:
                changed = True
        else:
            changed = True
        extra_context["department"] = department
    if 'orga' in request.GET:
        orga = '----'
        if not request.GET['orga'] == '----':
            orga = request.GET['orga']
            params = params + "&orga=" + orga
        if extra_context.keys().__contains__("orga"):
            if orga != extra_context["orga"]:
                changed = True
        else:
            changed = True
        extra_context["orga"] = orga
    if 'tf_owner_orga' in request.GET:
        tf_owner_orga = '----'
        if not request.GET['tf_owner_orga'] == '----':
            tf_owner_orga = request.GET['tf_owner_orga']
            params = params + "&tf_owner_orga=" + tf_owner_orga
        if extra_context.keys().__contains__("tf_owner_orga"):
            if tf_owner_orga != extra_context["tf_owner_orga"]:
                changed = True
        else:
            changed = True
        extra_context["tf_owner_orga"] = tf_owner_orga
    if 'tf_application' in request.GET:
        tf_application = '----'
        if not request.GET['tf_application'] == '----':
            tf_application = request.GET['tf_application']
            params = params + "&tf_application=" + tf_application
        if extra_context.keys().__contains__("tf_application"):
            if tf_application != extra_context["tf_application"]:
                changed = True
        else:
            changed = True
        extra_context["tf_application"] = tf_application
    if 'role' in request.GET:
        role = '----'
        if not request.GET['role'] == '----':
            role = request.GET['role']
            params = params + "&role=" + role
        if extra_context.keys().__contains__("role"):
            if role != extra_context["role"]:
                changed = True
        else:
            changed = True
        extra_context["role"] = role
    if 'group' in request.GET:
        group = '----'
        if not request.GET['group'] == '----':
            group = request.GET['group']
            params = params + "&group=" + group
        if extra_context.keys().__contains__("group"):
            if group != extra_context["group"]:
                changed = True
        else:
            changed = True
        extra_context["group"] = group
    if 'af_name' in request.GET:
        af_name =''
        if not request.GET['af_name'] == '':
            af_name = request.GET['af_name']
            params = params + "&af_name=" + af_name
        if extra_context.keys().__contains__("af_name"):
            if af_name != extra_context["af_name"]:
                changed = True
        else:
            changed = True
        extra_context["af_name"] = af_name
    if 'gf_name' in request.GET:
        gf_name = ''
        if not request.GET['gf_name'] == '':
            gf_name = request.GET['gf_name']
            params = params + "&gf_name=" + gf_name
        if extra_context.keys().__contains__("gf_name"):
            if gf_name != extra_context["gf_name"]:
                changed = True
        else:
            changed = True
        extra_context["gf_name"] = gf_name
    if 'tf_name' in request.GET:
        tf_name = ''
        if not request.GET['tf_name'] == '':
            tf_name = request.GET['tf_name']
            params = params + "&tf_name=" + tf_name
        if extra_context.keys().__contains__("tf_name"):
            if tf_name != extra_context["tf_name"]:
                changed = True
        else:
            changed = True
        extra_context["tf_name"] = tf_name

    return params, changed


class Compare(generic.ListView):
    model = User
    template_name = 'myRDB/compare.html'
    paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.extra_context['current_site'] = "compare"
        compareUserIdentity = self.request.GET['userSearch']
        print(compareUserIdentity)

        # TODO: hier noch lösung mit Params über API finden!
        compareUser = User.objects.get(identity=compareUserIdentity)

        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/users/%d' % compareUser.pk
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        res = requests.get(url, headers=headers)
        user_json_data = res.json()

        compUserRoles = user_json_data['roles']
        compUserAfs = user_json_data['user_afs']

        data, comp_gf_count, comp_tf_count = prepareTableData(compareUser, compUserRoles, compUserAfs, headers)

        prepareJSONdata(compareUserIdentity, user_json_data, True, headers)

        compare_paginator = Paginator(data, 10)
        page = self.request.GET.get('compare_page')

        try:
            compare_data = compare_paginator.page(page)
        except PageNotAnInteger:
            compare_data = compare_paginator.page(1)
        except EmptyPage:
            compare_data = compare_paginator.page(compare_paginator.num_pages)

        context['comp_role_count'] = len(compUserRoles)
        context['comp_af_count'] = len(compUserAfs)
        context['comp_gf_count'] = comp_gf_count
        context['comp_tf_count'] = comp_tf_count
        context["compareUser"] = compareUser
        context["compareUser_table_data"] = compare_data

        return context

    def get_queryset(self):
        user_data = self.request.session.get('user_data')
        table_data = self.request.session.get('table_data')
        self.extra_context['user_identity'] = user_data['identity']
        self.extra_context['user_first_name'] = user_data['first_name']
        self.extra_context['user_name'] = user_data['name']
        self.extra_context['user_department'] = user_data['department']
        self.extra_context['role_count'] = self.request.session.get('role_count')
        self.extra_context['af_count'] = self.request.session.get('af_count')
        self.extra_context['gf_count'] = self.request.session.get('gf_count')
        self.extra_context['tf_count'] = self.request.session.get('tf_count')

        roles = user_data['roles']
        afs = user_data['user_afs']

        return table_data


class ProfileRightsAnalysis(generic.ListView):
    model = User
    template_name = 'myRDB/profile_rights_analysis.html'
    extra_context = {}

    def get_queryset(self):
        self.extra_context['current_site'] = "analysis"
        user_data = self.request.session.get('user_data')
        table_data = self.request.session.get('table_data')
        self.extra_context['user_identity']=user_data['identity']
        self.extra_context['user_first_name'] = user_data['first_name']
        self.extra_context['user_name'] = user_data['name']
        self.extra_context['user_department'] = user_data['department']
        self.extra_context['role_count'] = self.request.session.get('role_count')
        self.extra_context['af_count'] = self.request.session.get('af_count')
        self.extra_context['gf_count'] = self.request.session.get('gf_count')
        self.extra_context['tf_count'] = self.request.session.get('tf_count')
        return None

class Profile(generic.ListView):
    model = User
    template_name = 'myRDB/profile.html'
    paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_queryset(self):
        self.extra_context['current_site']="profile"
        if not "identity" in self.request.GET.keys():
            user = self.request.user
        else:
            # TODO: hier noch lösung mit Params über API finden!
            user = User.objects.get(identity=self.request.GET['identity'])
            self.extra_context['identity_param'] = self.request.GET['identity']

        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/users/%d' % user.pk
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        res = requests.get(url, headers=headers)
        user_json_data = res.json()

        userid = user.id
        roles = user_json_data['roles']
        print(userid, user)
        afs = user_json_data['user_afs']

        data, gf_count, tf_count = prepareTableData(user, roles, afs, headers)
        self.request.session['table_data'] = data
        self.request.session['user_data'] = user_json_data.copy()
        prepareJSONdata(user.identity, user_json_data, False, headers)

        self.extra_context['role_count'] = len(roles)
        self.extra_context['af_count'] = len(afs)
        self.extra_context['gf_count'] = gf_count
        self.extra_context['tf_count'] = tf_count
        self.extra_context['user_identity'] = user_json_data['identity']
        self.extra_context['user_first_name'] = user_json_data['first_name']
        self.extra_context['user_name'] = user_json_data['name']
        self.extra_context['user_department'] = user_json_data['department']
        self.request.session['role_count'] = len(roles)
        self.request.session['af_count'] = len(afs)
        self.request.session['gf_count'] = gf_count
        self.request.session['tf_count'] = tf_count


        # manipuation für graphen nur auf kopie deswegen immernoch gleich ! <-TipTop
        # print(type(user_json_data), user_json_data)
        return data
        # return tfList

    def autocompleteModel(request):
        if request.is_ajax():
            q = request.GET.get('term', '').capitalize()
            search_qs = User.objects.filter(name__startswith=q)
            results = []
            print(q)
            for r in search_qs:
                results.append(r.FIELD)
            data = json.dumps(results)
        else:
            data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


def prepareTableData(user, roles, afs, headers):
    tfList = []
    gfList = []
    afList = []
    gf_count = 0
    for af in afs:
        gfs = af['gfs']
        gf_count += len(gfs)
        for gf in gfs:
            tfs = gf['tfs']
            for tf in tfs:
                tfList.append(tf['tf_name'])
                gfList.append(gf['gf_name'])
                afList.append(af['af_name'])

    data = zip(tfList, gfList, afList)
    tf_count = len(tfList)
    return list(data), gf_count, tf_count


def get_af_by_key(pk, headers):
    url = 'http://127.0.0.1:8000/afs/%d' % pk
    res = requests.get(url, headers=headers)
    af_json = res.json()
    return af_json


def prepareJSONdata(identity, user_json_data, compareUser, headers):
    print(type(user_json_data), user_json_data)
    user_json_data['children'] = user_json_data.pop('user_afs')
    scatterData = []
    i = 1
    for af in user_json_data['children']:
        af['name'] = af.pop('af_name')
        af['children'] = af.pop('gfs')
        model_af = get_af_by_key(pk=af['model_af_pk'], headers=headers)
        if model_af['af_applied'] is None:
            af_applied = ""
        else:
            af_applied = model_af['af_applied']
        for gf in af['children']:
            gf['name'] = gf.pop('gf_name')
            gf['children'] = gf.pop('tfs')
            for tf in gf['children']:
                tf['name'] = tf.pop('tf_name')
                tf['size'] = 3000
                scatterData.append({"name": tf['name'], "index": i, "af_applied": af_applied})

                i += 1
    if compareUser:
        # path = 'myRestfulRDB/static/myRDB/data/compareGraphData_%s.json' % identity
        path = 'myRDB_app/static/myRDB/data/compareGraphData.json'

    else:
        # path = 'myRestfulRDB/static/myRDB/data/graphData_%s.json' % identity
        path = 'myRDB_app/static/myRDB/data/graphData.json'
    with open(path, 'w') as outfile:
        json.dump(user_json_data, outfile, indent=2)

    if not compareUser:
        scatterData.sort(key=lambda r: r["af_applied"])
        # path = 'myRestfulRDB/static/myRDB/data/scatterGraphData_%s.json' % identity
        path = 'myRDB_app/static/myRDB/data/scatterGraphData.json'
        with open(path, 'w') as outfile:
            json.dump(scatterData, outfile, indent=2)


class CompleteUserListingViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be listed and detail-viewed
        """
    permission_classes = (IsAuthenticated,)
    serializer_class = CompleteUserListingSerializer

    def get_queryset(self):
        self.paginator.page_size = 1000
        if 'search_what' in self.request.GET:
            search_what = self.request.GET["search_what"]
            user_search = self.request.GET["userSearch"]
            if search_what == "identity":
                users = User.objects.filter(identity__startswith=user_search).order_by('name')
            elif search_what == "name":
                users = User.objects.filter(name__startswith=user_search).order_by('name')
            elif search_what == "first_name":
                users = User.objects.filter(first_name__startswith=user_search).order_by('name')
            if 'orga' in self.request.GET:
                orga = self.request.GET['orga']
                users = users.filter(orga={'team': orga})

        else:
            return User.objects.all().order_by('name')
        return users


class UserListingViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be listed and detail-viewed
        """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserListingSerializer

    def get_queryset(self):
        self.paginator.page_size = 1000

        if 'search_what' in self.request.GET:
            search_what = self.request.GET["search_what"]
            user_search = self.request.GET["userSearch"]
            if search_what == "identity":
                users = User.objects.filter(identity__startswith=user_search).order_by('name')
            elif search_what == "name":
                users = User.objects.filter(name__startswith=user_search).order_by('name')
            elif search_what == "first_name":
                users = User.objects.filter(first_name__startswith=user_search).order_by('name')
            if 'orga' in self.request.GET:
                orga = self.request.GET['orga']
                users = users.filter(orga={'team': orga})
        else:
            return User.objects.all().order_by('name')
        return users


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    page_size = 10

    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = UserFilter

    def get_queryset(self):
        return User.objects.all().order_by('name')


class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Roles to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.all()


class AFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AFSerializer

    def get_queryset(self):
        return AF.objects.all()


class GFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows GF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = GFSerializer

    def get_queryset(self):
        return GF.objects.all()


class TFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TFSerializer

    def get_queryset(self):
        self.paginator.page_size = 5000
        return TF.objects.all()


class OrgaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orgas to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = OrgaSerializer

    def get_queryset(self):
        self.paginator.page_size = 1000
        return Orga.objects.all()


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.all()


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Departments to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.all()


class ZI_OrganisationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ZI_Organisations to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ZI_OrganisationSerializer

    def get_queryset(self):
        return ZI_Organisation.objects.all()


class TF_ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TF_Applications to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TF_ApplicationSerializer

    def get_queryset(self):
        return TF_Application.objects.all()
# Create your views here.
