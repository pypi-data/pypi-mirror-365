from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from fourlabs_auth.models import EmailLoginCode
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class EditUserNameView(LoginRequiredMixin, View):
    def post(self, request):
        full_name = request.POST.get('full_name', '').strip()
        if not full_name:
            messages.error(request, "O nome não pode estar vazio.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        name_parts = full_name.split(maxsplit=1)
        request.user.first_name = name_parts[0]
        request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''

        request.user.save()
        messages.success(request, "Seu nome foi atualizado com sucesso.")
        return redirect(request.META.get('HTTP_REFERER', '/'))


class ChangePasswordView(LoginRequiredMixin, View):
    def post(self, request):
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Senha atual incorreta.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if new_password != confirm_new_password:
            messages.error(request, "A nova senha e a confirmação não coincidem.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if len(new_password) < 8:
            messages.error(request, "A nova senha deve ter pelo menos 8 caracteres.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Evita logout
        messages.success(request, "Senha alterada com sucesso!")
        return redirect(request.META.get('HTTP_REFERER', '/'))


class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request):
        confirmation = request.POST.get('confirmation')

        if confirmation != 'ENCERRAR':
            messages.error(request, 'Confirmação incorreta. Digite exatamente "ENCERRAR".')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        user = request.user
        logout(request)  # Faz logout primeiro
        user.delete()  # Depois remove o usuário do banco
        messages.success(request, 'Sua conta foi encerrada com sucesso.')
        return redirect('login')


class ExportUserDataView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        data = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined if hasattr(user, 'date_joined') else None,
            "last_login": user.last_login,
        }

        response = JsonResponse(data, encoder=DjangoJSONEncoder, json_dumps_params={"indent": 4})
        response["Content-Disposition"] = f'attachment; filename="meus_dados.json"'
        return response


class RequestEmailView(View):
    template_name = 'accounts/request_email.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        if not email:
            return render(request, self.template_name, {'error': 'Email é obrigatório'})

        if not email.endswith('@foursys.com.br'):
            messages.info(request, "Apenas emails corporativos da Foursys são permitidos.")
            return render(request, self.template_name, {
                'error': 'Apenas emails corporativos da Foursys são permitidos.'
            })

        code = EmailLoginCode.generate_code()
        EmailLoginCode.objects.create(email=email, code=code)

        # Simples envio de email (console)
        print(code)
        messages.info(request, "O código foi enviado para seu email Foursys.")
        request.session['auth_email'] = email
        return redirect('verify_code')


class VerifyCodeView(View):
    template_name = 'accounts/verify_code.html'

    def get(self, request):
        if not request.session.get('auth_email'):
            return redirect('request_email')
        return render(request, self.template_name)

    def post(self, request):
        email = request.session.get('auth_email')
        code_input = request.POST.get('code')

        if not email or not code_input:
            messages.info(request, "Código é obrigatório")
            return render(request, self.template_name, {'error': 'Código é obrigatório'})

        try:
            code_obj = EmailLoginCode.objects.filter(email=email, code=code_input).latest('created_at')
            if not code_obj.is_valid():
                messages.info(request, "Código expirado. Peça um novo.")
                return render(request, self.template_name, {'error': 'Código expirado. Peça um novo.'})
        except EmailLoginCode.DoesNotExist:
            messages.error(request, "Código inválido.")
            return render(request, self.template_name, {'error': 'Código inválido.'})

        # Autentica ou cria usuário
        user, created = User.objects.get_or_create(email=email, defaults={
            'first_name': 'Usuário',
            'last_name': 'Foursys',
            'password': get_random_string(30)
        })

        login(request, user)
        messages.success(request, "Bem vindo!")
        return redirect('home')
