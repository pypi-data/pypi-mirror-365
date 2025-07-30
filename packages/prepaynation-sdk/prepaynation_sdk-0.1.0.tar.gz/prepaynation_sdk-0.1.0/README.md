[![PyPI version](https://img.shields.io/pypi/v/prepaynation_sdk.svg)](https://pypi.org/project/prepaynation_sdk/)
\[![Python Version](https://img.shields.io/pypi/pyversions/prepaynation_sdk.svg)]
\[![License](https://img.shields.io/github/license/ninjaroot-509/prepaynation_sdk.svg)]

---

# PrepayNation SDK

Un SDK Python simple et léger pour interagir avec l’API Prepay Nation Top‑Up v2 sans gérer manuellement l’authentification, les en‑têtes HTTP ou le parsing JSON.

## Table des matières

* [Fonctionnalités](#fonctionnalités)
* [Installation](#installation)
* [Utilisation rapide](#utilisation-rapide)
* [Personnalisation avancée](#personnalisation-avancée)
* [Gestion des erreurs](#gestion-des-erreurs)
* [Référence des méthodes SDK](#référence-des-méthodes-sdk)
* [Contribuer](#contribuer)
* [Licence](#licence)

---

## Fonctionnalités

* 🔐 **Authentification Basic Auth** automatique (Base64(user\:pass)).
* 🌍 **Sandbox & Production** : change d’URL via le paramètre `sandbox`.
* 🔄 **Gestion unifiée des requêtes** et des erreurs HTTP/JSON.
* ⚙️ **Extensible** : injection d’une `requests.Session` personnalisée.
* 📚 Méthodes Pythonic pour :

  * Solde de compte
  * Catalogues (pays, opérateurs, produits, SKUs, bundles, gift cards)
  * Recharges (mobile, PIN, eSIM)
  * Paiement de factures
  * Statut de transaction et port-in SIM

---

## Installation

Installez depuis PyPI :

```bash
pip install prepaynation_sdk
```

Ou depuis la source :

```bash
git clone https://github.com/ninjaroot-509/prepaynation_sdk.git
cd prepaynation_sdk
pip install .
```

---

## Utilisation rapide

```python
from prepaynation_sdk.client import PrepayNationClient

# Initialisation (mode sandbox)
client = PrepayNationClient(
    user_id="VOTRE_USER_ID",
    password="VOTRE_PASSWORD",
    sandbox=True
)

# Récupérer le solde du compte
balance = client.get_balance()
print(balance)

# Effectuer une recharge mobile
resp = client.mobile_topup(
    sku_id=1234,
    amount=5.0,
    mobile="+50937123456",
    correlation_id="txn-001"
)
print(resp)
```

---

## Personnalisation avancée

Vous pouvez passer votre propre `requests.Session` pour :

* Gérer les **timeouts**
* Configurer des **retries**
* Ajouter des **middlewares** ou du **logging**

```python
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

session = requests.Session()
retries = Retry(total=3, backoff_factor=0.3)
session.mount('https://', HTTPAdapter(max_retries=retries))

client = PrepayNationClient(
    user_id="…",
    password="…",
    sandbox=False,
    session=session
)
```

---

## Gestion des erreurs

Chaque méthode renvoie :

* Un `dict` Python parsé depuis la réponse JSON en cas de succès.
* Un `{'error': '<message>'}` si une erreur HTTP (401, 403, 404, 5xx) ou JSON se produit.

```python
result = client.get_balance()
if 'error' in result:
    raise RuntimeError(result['error'])
```

---

## Référence des méthodes SDK

### `get_balance()`

Récupère le solde du compte Prepay Nation.

```python
balance = client.get_balance()
print(balance)  # Ex: {'balance': 123.45, 'currency': 'USD'}
```

### `get_countries()`

Retourne la liste des pays disponibles.

```python
countries = client.get_countries()
print(countries)  # Ex: [{'countryCode': 'US', 'name': 'United States'}, ...]
```

### `get_operators(operator_id: int = None, country_code: str = None)`

Liste les opérateurs, optionnellement filtrés par ID ou code pays.

```python
operators = client.get_operators(country_code='HT')
print(operators)  # Ex: [{'operatorId': 1, 'name': 'Digicel'}, ...]
```

### `get_products(operator_id: int = None, country_code: str = None)`

Liste les produits proposés par un opérateur ou un pays.

```python
products = client.get_products(operator_id=1)
print(products)  # Ex: [{'productId': 10, 'name': 'Airtime'}, ...]
```

### `get_skus(product_id: int)`

Récupère les SKUs pour un produit donné.

```python
skus = client.get_skus(product_id=10)
print(skus)  # Ex: {'skus': [...]} ou {'error': 'Product ID invalide'}
```

### `get_exchange_rate(sku_id: int)`

Obtient le taux de change pour une SKU spécifique.

```python
rate = client.get_exchange_rate(sku_id=100)
print(rate)  # Ex: {'rate': 0.95, 'currency': 'USD'}
```

### `get_error_codes()`

Liste les codes d’erreur documentés par l’API.

```python
errors = client.get_error_codes()
print(errors)  # Ex: [{'code': 'E001', 'message': 'Invalid SKU'}, ...]
```

### `get_bundles(product_id: int, phone_number: str)`

Récupère les offres de bundle pour un produit et un numéro de téléphone.

```python
bundles = client.get_bundles(product_id=10, phone_number='+50937123456')
print(bundles)  # Ex: {'bundles': [...]} ou {'error': 'Numéro de téléphone invalide'}
```

### `get_gift_cards(cursor: int = 0, page_size: int = 500, **filters)`

Liste les gift cards avec pagination et filtres.

```python
giftcards = client.get_gift_cards(product_id=10)
print(giftcards)  # Ex: {'giftCards': [...], 'nextCursor': 1}
```

### `mobile_number_lookup(phone_number: str)`

Recherche des informations sur un numéro mobile.

```python
info = client.mobile_number_lookup('+50937123456')
print(info)  # Ex: {'countryCode': 'HT', 'operatorId': 1}
```

### `bill_payment_lookup(sku_id: int = None, account_number: str = None)`

Lookup des détails d’un compte pour paiement de facture.

```python
acct = client.bill_payment_lookup(sku_id=200, account_number='12345')
print(acct)  # Ex: {'accountName': 'John Doe', ...}
```

### `esim_transaction(sku_id: int, correlation_id: str)`

Passe une commande eSIM.

```python
esim = client.esim_transaction(sku_id=300, correlation_id='txn-002')
print(esim)  # Ex: {'orderId': 'ORD123', 'status': 'PENDING'}
```

### `get_remaining_data_balance_of_bundle(iccid: str)`

Vérifie le solde de données restant sur un bundle eSIM.

```python
balance = client.get_remaining_data_balance_of_bundle('890112...')
print(balance)  # Ex: {'remainingMB': 500}
```

### `mobile_topup(sku_id: int, amount: float, mobile: str, correlation_id: str, **kwargs)`

Effectue une recharge mobile airtime.

```python
resp = client.mobile_topup(
    sku_id=1234,
    amount=5.0,
    mobile='+50937123456',
    correlation_id='txn-001'
)
print(resp)  # Ex: {'transactionId': 'TX123', 'status': 'SUCCESS'}
```

### `pin_transaction(sku_id: int, correlation_id: str, **kwargs)`

Demande une transaction via PIN.

```python
pin = client.pin_transaction(sku_id=1234, correlation_id='txn-003')
print(pin)  # Ex: {'pin': '1234'}
```

### `bill_payment(sku_id: int, amount: float, account_number: str, correlation_id: str, **kwargs)`

Execute un paiement de facture.

```python
bill = client.bill_payment(
    sku_id=200,
    amount=50.0,
    account_number='12345',
    correlation_id='txn-004'
)
print(bill)  # Ex: {'paymentId': 'PMT123', 'status': 'SUCCESS'}
```

### `get_status_by_correlation_id(correlation_id: str)`

Récupère le statut d’une transaction via son correlation ID.

```python
status = client.get_status_by_correlation_id('txn-001')
print(status)  # Ex: {'status': 'SUCCESS'}
```

### `gift_card(sku_id: int, amount: float, correlation_id: str, **kwargs)`

Commande une gift card.

```python
gc = client.gift_card(
    sku_id=400,
    amount=25.0,
    correlation_id='txn-005'
)
print(gc)  # Ex: {'giftCardId': 'GC123', 'status': 'ISSUED'}
```

### `fetch_gift_card_info(order_id: str)`

Récupère les détails d’une gift card existante.

```python
info = client.fetch_gift_card_info('GC123')
print(info)  # Ex: {'status': 'ISSUED', 'balance': 25.0}
```

### `sim_activation(sku_id: int, sim_number: str, zip_code: str, correlation_id: str, **kwargs)`

Active une nouvelle eSIM.

```python
sim = client.sim_activation(
    sku_id=500,
    sim_number='890112...',
    zip_code='12345',
    correlation_id='txn-006'
)
print(sim)  # Ex: {'activationStatus': 'ACTIVE'}
```

### `sim_port_in(sku_id: int, sim_number: str, zip_code: str, correlation_id: str, **kwargs)`

Demande le portage d’une SIM existante.

```python
port = client.sim_port_in(
    sku_id=500,
    sim_number='890112...',
    zip_code='12345',
    correlation_id='txn-007'
)
print(port)  # Ex: {'portRequestId': 'PORT123', 'status': 'PENDING'}
```

### `check_port_in_status(correlation_id: str)`

Vérifie le statut d’une demande de portage SIM.

```python
port_status = client.check_port_in_status('txn-007')
print(port_status)  # Ex: {'status': 'COMPLETED'}
```

## Contribuer

1. Fork du projet
2. Créer une branche `feature/...`
3. Commit & Pull Request

---

## Licence

MIT © ninjaroot-509
