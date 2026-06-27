# payments/base.py
class BasePaymentProvider:
    def crear_orden(self, total, descripcion):
        raise NotImplementedError

    def consultar_estado(self, orden_id):
        raise NotImplementedError
