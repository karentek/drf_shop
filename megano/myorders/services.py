
class Basket(object):

    """Кастомный класс для работы корзины"""

    def __init__(self, request):
        """
        :param request: запрос с данными заказа прходит с вью функции BasketView
        создается словарь в котором будут хранится данние о заказе в течении сессии
        """

        self.request = request
        self.session = request.session
        basket = self.session.get('basket')
        if not basket:
            basket = self.session['basket'] = {}
        self.basket = basket

    def dell_value_equals_zero(self):

        """Метот удаляет из корзины товары колличество которых равно нулю"""

        new_dict = {}
        for key, value in self.basket.items():
            if value != 0:
                new_dict[key] = value
        self.basket = new_dict
        self.save()
        return self.basket

    def add_item(self, product_id, products_count, quantity=1):

        """

        :param product_id: продукт
        :param products_count: колличество продукта на складе
        :param quantity: заказанное колличество
        сохраняет колличество товара добавленного в корзину
        не дает заказать товар в колличестве большем чем его есть на складе
        """
        product_id = str(product_id)
        quantity = int(quantity)
        if product_id in self.basket and self.basket[product_id] + quantity < products_count:
            self.basket[product_id] += quantity
        elif product_id in self.basket and self.basket[product_id] + quantity == products_count:
            self.basket[product_id] = products_count
        elif product_id in self.basket and self.basket[product_id] + quantity > products_count:
            self.basket[product_id] = products_count
        else:
            if quantity < products_count:
                self.basket[product_id] = quantity
            elif quantity >= products_count:
                self.basket[product_id] = products_count
        self.save()

    def remove_item(self, product_id, quantity=1):
        """

        :param product_id: продукт
        :param quantity: удаляемое колличество
        """
        product_id = str(product_id)
        quantity = int(quantity)
        if product_id in self.basket and self.basket[product_id] != 0:
            self.basket[product_id] -= quantity
        self.save()

    def get_basket_items(self):
        """
        :return: возвращает корозину
        """
        return self.basket

    def clear_basket(self):
        """
        Метод удаляет данные корзины
        :return:
        """
        self.session['basket'] = {}
        self.save()

    def save(self):
        """
        Сохранение корзины
        :return:
        """
        self.session.modified = True

    def get_ids(self):
        """

        :return:  возвращает список из ID товаров в корзине  для удобства
        """
        items = self.basket
        ids = [int(item) for item in items]
        return ids


def aply_count_for_product(first_list: list[dict[str, any]], second_dict: dict) -> list[dict[str, any]]:
    """
     функция помощник для сериалайзеров и вью корзины
    :param first_list: список со словарями ID товаров и колличества этого товара в карзине,
    :param second_dict: словарь с данными о товаре для сериализации в котором
     заменяется колличество товара на складе на его колличество в корзине
    :return: список со словарями "ID: count"
    """
    for item in first_list:
        item_id = str(item.get('id'))
        if item_id in second_dict:
            item['count'] = second_dict.get(item_id, 0)
    return first_list
