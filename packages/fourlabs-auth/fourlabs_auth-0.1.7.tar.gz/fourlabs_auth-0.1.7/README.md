# 🔐 Fourlabs Auth

Autenticação via e-mail corporativo para projetos Django, com código de verificação por e-mail, gerenciamento de conta, exportação de dados e mais.

---

## 🚀 Instalação

### 1. Instale via pip (local ou via PyPI)

#### Local (modo desenvolvimento):

```bash
pip install -e /caminho/para/fourlabs_auth/
```

#### Ou (se publicado no PyPI):

```bash
pip install foursys-auth
```

## ⚙️ Configuração

### 1. Adicione fourlabs_auth no INSTALLED_APPS

```python
# settings.py

INSTALLED_APPS = [
    ...
    'fourlabs_auth',
]
```


### 2. Configure o modelo de usuário customizado

```bash
AUTH_USER_MODEL = 'fourlabs_auth.User'
```

### 3. Middleware e context processors (mensagens)

```python
MIDDLEWARE = [
    ...
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

```


### 4. Configure os templates e arquivos estáticos (se necessário)

```python

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

TEMPLATES = [
    {
        ...
        'DIRS': [BASE_DIR / "templates"],
    }
]


```

## 🔗 URLs

#### Inclua as rotas da biblioteca no seu urls.py principal:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('auth/', include('fourlabs_auth.urls')),
]

```

## 💾 Migrações

```bash
python manage.py makemigrations fourlabs_auth
python manage.py migrate
```


## 🧑‍💼 Funcionalidades Incluídas

Rota	Descrição
/auth/login/	Solicita o e-mail corporativo
/auth/verify/	Verifica o código recebido
/auth/edit-user-name/	Atualiza o nome do usuário
/auth/change-password/	Altera a senha do usuário
/auth/delete-account/	Encerra a conta do usuário
/auth/export-user-data/	Exporta os dados em JSON
/auth/logout/	Logout seguro do usuário


## ✏️ Customização
#### Você pode sobrescrever os templates HTML criando arquivos com o mesmo nome em:

```bash
templates/accounts/
```

## 📦 Exemplo de fluxo de autenticação

Acesse /auth/login/

Insira seu email da empresa (@foursys.com.br)

Verifique o código enviado e faça login


## 🧪 Requisitos

Django >= 3.2
Python >= 3.8

## Gerar o Pacote

```bash
python setup.py sdist bdist_wheel
```

## Publicar no PyPI

```bash
twine upload dist/*
```


## Dicas para Atualizações

#### Aumente a versão em setup.py (version='0.1.1', por exemplo)

#### Apague a pasta dist/:

```bash
rm -rf dist/
```

#### Gere e envie novamente:

```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```