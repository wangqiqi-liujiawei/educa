from django.forms.models import modelform_factory
from django.db.models import Count
from django.apps import apps
from .form import ModuleFormSet
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from .models import Courses, Module, Content, Subject
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from students.forms import CourseEnrollForm
from django.core.cache import cache


# Create your views here.
class ManageCourseListView(ListView):
    model = Courses
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


# 只检索当前用户
class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


# 表单有效之后执行
class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# 课程视图展示字段和重定向地址
class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Courses
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


# 表单使用的模板
class OwnerCourseEditMixin(OwnerEditMixin, OwnerCourseMixin):
    template_name = 'courses/manage/course/form.html'


# 当前用户创建的课程
class ManageCourseListMixin(ListView, OwnerCourseMixin):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_courses'


# 当前用户创建新的 课程 对象
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_courses'


# 当前用户编辑已有的的 课程 对象
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_courses'


# 当前用户确认删除 课程 对象
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    permission_required = 'courses.delete_courses'
    template_name = 'courses/manage/course/delete.html'


# 课程模块内容管理
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Courses, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        course = self.course
        datas = {'formset': formset, 'course': course}
        return self.render_to_response(datas)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        course = self.course
        datas = {'formset': formset, 'course': course}
        return self.render_to_response(datas)


class ContentCreateUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/content/form.html'
    module = None
    modle = None
    obj = None

    def get_model(self, model_name):
        if model_name in ['text', 'image', 'video', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.modle = self.get_model(model_name)
        # print(self.modle)
        if id:
            self.obj = get_object_or_404(self.modle, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.modle, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                Content.objects.create(module=self.module, item=obj)
                return redirect('module_content_list', self.module.id)
        datas = {'form': form, 'object': self.obj}
        return self.render_to_response(datas)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.modle, instance=self.obj)
        datas = {'form': form, 'object': self.obj}
        return self.render_to_response(datas)


class ContentDeleteView(View):
    def post(self, request):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        # 删除所关联的 text/image/file/video
        content.item.delete()
        # 删除内容
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        datas = {'module': module}
        # print(module.contents.item)
        return self.render_to_response(datas)


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Courses
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
        all_courses = Courses.objects.annotate(total_module=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        datas = {'subjects': subjects, 'courses': courses, 'subject': subject}
        return self.render_to_response(datas)


class CourseDetailView(DetailView):
    template_name = 'courses/course/detail.html'
    model = Courses
    # print(model.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        return context
