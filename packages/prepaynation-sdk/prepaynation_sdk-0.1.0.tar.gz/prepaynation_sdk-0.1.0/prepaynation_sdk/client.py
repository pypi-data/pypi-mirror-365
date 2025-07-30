import base64
import json
import requests


class PrepayNationClient:

    def __init__(
        self,
        user_id: str,
        password: str,
        sandbox: bool = True,
        session: requests.Session = None
    ):
        self.base_url = (
            "https://sandbox.valuetopup.com/api/v2"
            if sandbox else
            "https://www.valuetopup.com/api/v2"
        )
        auth_string = f"{user_id}:{password}"
        token = base64.b64encode(auth_string.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json"
        }
        self.session = session or requests.Session()

    def _request(self, method: str, endpoint: str, params=None, data=None) -> dict:
        url = f"{self.base_url}{endpoint}"
        try:
            resp = self.session.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
        except requests.RequestException as e:
            return {"error": f"Erreur de connexion: {e}"}

        if resp.status_code == 401:
            return {"error": "Unauthorized - Vérifiez vos identifiants"}
        if resp.status_code == 403:
            return {"error": "Forbidden - Accès refusé"}
        if resp.status_code == 404:
            return {"error": "Not Found - Endpoint invalide"}
        if resp.status_code >= 500:
            return {"error": f"Erreur serveur ({resp.status_code})"}

        try:
            return resp.json()
        except json.JSONDecodeError:
            return {"error": "Réponse invalide (non JSON)", "raw": resp.text}

    def get_balance(self) -> dict:
        return self._request("GET", "/account/balance")

    def get_countries(self) -> list:
        return self._request("GET", "/catalog/countries").get("payLoad", [])

    def get_operators(self, operator_id: int = None, country_code: str = None) -> list:
        params = {}
        if operator_id:
            params["operatorId"] = operator_id
        if country_code:
            params["countryCode"] = country_code
        return self._request("GET", "/catalog/operators", params=params).get("payLoad", [])

    def get_products(self, operator_id: int = None, country_code: str = None) -> list:
        params = {}
        if operator_id:
            params["operatorId"] = operator_id
        if country_code:
            params["countryCode"] = country_code
        return self._request("GET", "/catalog/products", params=params).get("payLoad", [])

    def get_skus(self, product_id: int) -> dict:
        if not isinstance(product_id, int) or product_id <= 0:
            return {"error": "Product ID invalide"}
        return self._request("GET", "/catalog/skus", params={"productId": product_id})

    def get_exchange_rate(self, sku_id: int) -> dict:
        if not isinstance(sku_id, int) or sku_id <= 0:
            return {"error": "SKU ID invalide"}
        return self._request("GET", f"/catalog/sku/exchangeRate/{sku_id}").get("payLoad", {})

    def get_error_codes(self) -> list:
        return self._request("GET", "/catalog/errors").get("payLoad", [])

    def get_bundles(self, product_id: int, phone_number: str) -> dict:
        if not phone_number:
            return {"error": "Numéro de téléphone invalide"}
        phone = phone_number.replace(" ", "").replace("-", "")
        if phone.startswith("+"):
            phone = phone[1:]
        if not product_id:
            return {"error": "Product invalide"}
        return self._request("GET", f"/catalog/bundles/{product_id}/{phone}")

    def get_gift_cards(self, cursor: int = 0, page_size: int = 500, product_id: int = None, sku_id: int = None, country_code: str = None) -> dict:
        params = {"cursor": cursor, "pageSize": page_size}
        if product_id:
            params["productId"] = product_id
        if sku_id:
            params["skuId"] = sku_id
        if country_code:
            params["countryCode"] = country_code
        return self._request("GET", "/catalog/skus/giftcards", params=params)

    def mobile_number_lookup(self, phone_number: str) -> dict:
        if not phone_number:
            return {"error": "Numéro de téléphone invalide"}
        phone = phone_number.replace(" ", "").replace("-", "")
        if phone.startswith("+"):
            phone = phone[1:]
        return self._request("GET", f"/lookup/mobile/{phone}")

    def bill_payment_lookup(self, sku_id: int = None, account_number: str = None) -> dict:
        params = {}
        if sku_id:
            params["skuId"] = sku_id
        if account_number:
            params["accountNumber"] = account_number
        return self._request("GET", "/lookup/billpay/fetch-account-detail", params=params)

    def esim_transaction(self, sku_id: int, correlation_id: str) -> dict:
        payload = {"skuId": sku_id, "correlationId": correlation_id}
        return self._request("POST", "/esim/order", data=payload)

    def get_remaining_data_balance_of_bundle(self, iccid: str) -> dict:
        return self._request("GET", f"/esim/status/{iccid}")

    def mobile_topup(self, sku_id: int, amount: float, mobile: str, correlation_id: str, sender_mobile: str = None, boost_pin: str = None, number_of_plan_months: int = None, transaction_currency_code: str = "USD", additional_info: dict = None) -> dict:
        phone = mobile.replace(" ", "").replace("-", "")
        if phone.startswith("+"):
            phone = phone[1:]
        payload = {
            "skuId": sku_id,
            "amount": amount,
            "mobile": phone,
            "correlationId": correlation_id,
            "transactionCurrencyCode": transaction_currency_code
        }
        if sender_mobile:
            payload["senderMobile"] = sender_mobile
        if boost_pin:
            payload["boostPin"] = boost_pin
        if number_of_plan_months:
            payload["numberOfPlanMonths"] = number_of_plan_months
        if additional_info:
            payload["additionalInfo"] = additional_info
        return self._request("POST", "/transaction/topup", data=payload)

    def pin_transaction(self, sku_id: int, correlation_id: str, recipient: dict = None, additional_info: dict = None) -> dict:
        payload = {"skuId": sku_id, "correlationId": correlation_id}
        if recipient:
            payload["recipient"] = recipient
        if additional_info:
            payload["additionalInfo"] = additional_info
        return self._request("POST", "/topup/pin", data=payload)

    def bill_payment(self, sku_id: int, amount: float, account_number: str, correlation_id: str, mobile_number: str = None, check_digit: str = None, sender_mobile: str = None, sender_name: str = None, transaction_currency_code: str = "USD", additional_info: dict = None) -> dict:
        payload = {"skuId": sku_id, "amount": amount, "accountNumber": account_number, "correlationId": correlation_id}
        if mobile_number:
            payload["mobileNumber"] = mobile_number
        if check_digit:
            payload["checkDigit"] = check_digit
        if sender_mobile:
            payload["senderMobile"] = sender_mobile
        if sender_name:
            payload["senderName"] = sender_name
        if transaction_currency_code:
            payload["transactionCurrencyCode"] = transaction_currency_code
        if additional_info:
            payload["additionalInfo"] = additional_info
        return self._request("POST", "/billpay", params=payload)

    def get_status_by_correlation_id(self, correlation_id: str) -> dict:
        return self._request("GET", f"/transaction/status/{correlation_id}")

    def gift_card(self, sku_id: int, amount: float, correlation_id: str, first_name: str = None, last_name: str = None, recipient: dict = None, transaction_currency_code: str = "USD", additional_info: dict = None) -> dict:
        payload = {"skuId": sku_id, "amount": amount, "correlationId": correlation_id}
        if first_name:
            payload["firstName"] = first_name
        if last_name:
            payload["lastName"] = last_name
        if recipient:
            payload["recipient"] = recipient
        if transaction_currency_code:
            payload["transactionCurrencyCode"] = transaction_currency_code
        if additional_info:
            payload["additionalInfo"] = additional_info
        return self._request("POST", "/transaction/giftcard/order", data=payload)

    def fetch_gift_card_info(self, order_id: str) -> dict:
        return self._request("GET", f"/transaction/giftcard/fetch/{order_id}")

    def sim_activation(self, sku_id: int, sim_number: str, zip_code: str, correlation_id: str, language: str = None, email: str = None, number_of_plan_months: int = None, area_code: str = None, imei: str = None, additional_info: dict = None) -> dict:
        payload = {"skuId": sku_id, "simNumber": sim_number, "zipCode": zip_code, "correlationId": correlation_id}
        if language:
            payload["language"] = language
        if email:
            payload["email"] = email
        if number_of_plan_months:
            payload["numberOfPlanMonths"] = number_of_plan_months
        if area_code:
            payload["areaCode"] = area_code
        if imei:
            payload["imei"] = imei
        if additional_info:
            payload["additionalInfo"] = additional_info
        return self._request("POST", "/sim/activate", data=payload)

    def sim_port_in(self, sku_id: int, sim_number: str, zip_code: str, correlation_id: str, language: str = None, email: str = None, number_of_plan_months: int = None, area_code: str = None, imei: str = None, operator_id: int = None, mobile_number: str = None, account_number: str = None, password_pin: str = None, first_name: str = None, last_name: str = None, address: str = None, city: str = None, state: str = None, account_holder_zip: str = None, equipment_type: str = None, street_number: str = None, street_name: str = None, contact_number: str = None, additional_info: dict = None) -> dict:
        payload = {"skuId": sku_id, "simNumber": sim_number, "zipCode": zip_code, "correlationId": correlation_id}
        for key, val in {"language": language, "email": email, "numberOfPlanMonths": number_of_plan_months, "areaCode": area_code, "imei": imei, "operatorId": operator_id, "mobileNumber": mobile_number, "accountNumber": account_number, "passwordPin": password_pin, "firstName": first_name, "lastName": last_name, "address": address, "city": city, "state": state, "accountHolderZip": account_holder_zip, "equipmentType": equipment_type, "streetNumber": street_number, "streetName": street_name, "contactNumber": contact_number, "additionalInfo": additional_info}.items():
            if val is not None:
                payload[key] = val
        return self._request("POST", "/sim/port-in", data=payload)

    def check_port_in_status(self, correlation_id: str) -> dict:
        return self._request("GET", f"/transaction/sim/portin/status/{correlation_id}")
