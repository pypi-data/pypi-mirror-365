
---

````markdown
# Django Auth Boilerplate 🔐

A simple, production-ready Django authentication boilerplate using **JWT (JSON Web Tokens)** powered by `djangorestframework-simplejwt`.

## Features

✅ JWT Authentication (access & refresh tokens)  
✅ Registration with validation  
✅ Login & Logout  
✅ Token Blacklisting  
✅ Custom Exception Handling with Logging  
✅ Throttling (Rate Limiting)  
✅ Clean project structure  
✅ Ready for PyPI packaging


---

## 📦 Installation

```bash
pip install auth-boilerplate
````

Or if you’re developing locally:

```bash
git clone https://github.com/Meekemma/auth-boilerplate.git
cd auth-boilerplate
pip install -r requirements.txt
```

---

## ⚙️ Setup Instructions

1. **Add to `INSTALLED_APPS`** in your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'your_auth_app',  # Replace with your app name
]
```

2. **Configure Authentication & Throttling:**

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'login': '3/minute',
        'register': '5/minute',
        'logout': '5/minute',
    },
    'EXCEPTION_HANDLER': 'coreuser.utils.custom_exception_handler',
}
```

3. **Add JWT Settings (Optional):**

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'BLACKLIST_AFTER_ROTATION': True,
}
```

---

## 🔑 Generating a Secret Key

Run this in Python shell:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Copy the result and paste it into your `.env` or `settings.py` as:

```python
SECRET_KEY = 'your-generated-secret-key'
```
---



## 📮 API Endpoints

| Method | Endpoint          | Description              |
| ------ | ----------------- | ------------------------ |
| POST   | `/register/`      | Register a user          |
| POST   | `/login/`         | Obtain tokens (JWT)      |
| POST   | `/logout/`        | Logout & blacklist token |
| POST   | `/token/refresh/` | Refresh access token     |

---

## 🧪 Testing with Postman

### ✅ **Registration**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "StrongPassword123!",
  "password2": "StrongPassword123!"
}
```

### 🔐 **Login**

```json
{
  "email": "john@example.com",
  "password": "StrongPassword123!"
}
```

**Response:**

```json
{
  "refresh": "your-refresh-token",
  "access": "your-access-token",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

---

### 🚪 **Logout**

```json
{
  "refresh": "your-refresh-token"
}
```

**Note:** This will blacklist the token and invalidate future use.

---

### 🔄 **Token Refresh**

```json
{
  "refresh": "your-refresh-token"
}
```

**Response:**

```json
{
  "access": "new-access-token"
}
```

---

---

## 💡 Contribution

Pull requests are welcome! Please fork the repo and submit a PR with a clear description.

---

## 📝 License

This project is licensed under the MIT License.

---

## 📫 Contact

* Author: [@meekemma](https://github.com/meekemma)
* Email: [ibehemmanuel32@gmail.com](mailto:ibehemmanuel32@gmail.com)

```

---

```
