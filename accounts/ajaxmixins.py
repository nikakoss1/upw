# -*- coding: utf-8 -*-
import json
from django.views.generic import FormView
from django.http import JsonResponse
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView


############################################################################################################################
### AjaxMixins

class AjaxLoginFormMixin(object):
    def form_valid(self, form):
        response = super(AjaxLoginFormMixin, self).form_valid(form)
        if self.request.method == 'POST' and self.request.is_ajax():
            date_created = self.request.session.get('create_date', None)
            if date_created:
                delta = int(time.time()) - int(date_created)
                if delta < 120:
                    form.errors['card'] = "Повторная отправка кода возможна через %s секунд" % (120 - delta)
                    return JsonResponse(form.errors, status=400)
            cd_form = form.cleaned_data
            card = cd_form['card']
            try:
                user = Card.objects.get(card_number=card, status=True)
            except Card.DoesNotExist:
                form.errors['card'] = "Карта не найдена"
                return JsonResponse(form.errors, status=400)
            self.request.session.set_expiry(600)
            self.request.session['smscode_send'] = random.randint(1000, 9999)  # Сам код
            self.request.session['create_date'] = int(time.time())  # время отправки кода
            self.request.session['card_tmp'] = card  # Карта на которую отправлен код
            sendCode(phone=user.passport.phone, code=self.request.session['smscode_send'])
            data = {
                    'message': "Successfully submitted form data."
                        }
            return JsonResponse(data)
        else:
            return response


class AjaxConfirmFormMixin(object):
    def form_valid(self, form):
        response = super(AjaxConfirmFormMixin, self).form_valid(form)
        if self.request.method == 'POST' and self.request.is_ajax():
            if self.request.session.get('smscode_send', None) is None:
                return response
            cd_form = form.cleaned_data
            smscode = cd_form['smscode']
            if int(self.request.session['smscode_send']) == int(smscode):
                self.request.session.set_expiry(600)
                self.request.session['card'] = self.request.session['card_tmp']
                del self.request.session['create_date']  # удаляем время отправки
                del self.request.session['smscode_send']  # удаляем отправленный код
                del self.request.session['card_tmp']  # удаляем временную карту
                data = {
                        'message': "SMS code is OK"
                            }
                return JsonResponse(data)
            else:
                form.errors['smscode'] = "Не верный код"
                return JsonResponse(form.errors, status=400)
        else:
            return response

class AjaxGetMoneyFormMixin(object):
    def form_valid(self, form):
        response = super(AjaxGetMoneyFormMixin, self).form_valid(form)
        if self.request.method == 'POST' and self.request.is_ajax():
            getmoneyform = form.cleaned_data
            name = getmoneyform['name']
            phone = getmoneyform['phone']
            send_email(name, phone)
            data = {
                    'message': "OK"
                        }
            return JsonResponse(data)
        else:
            return response












