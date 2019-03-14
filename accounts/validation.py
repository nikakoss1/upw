class AjaxValidation(FormView):
    form_dict = {
        'signin': SignInForm,
    }

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/')

    def form_invalid(self, form):
        data = []
        for k, v in form._errors.iteritems():
            text = {
                'desc': ', '.join(v),
            }
            if k == '__all__':
                text['key'] = '#%s' % self.request.POST.get('form')
            else:
                text['key'] = '#id_%s' % k
            data.append(text)
        return HttpResponse(json.dumps(data))

    def form_valid(self, form):
        return HttpResponse("ok")

    def get_form_class(self):
        return self.form_dict[self.request.POST.get('form')]