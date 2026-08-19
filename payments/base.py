# payments/base.py
class BasePaymentProvider:
    def crear_orden(self, total, descripcion):
        raise NotImplementedError

    def consultar_estado(self, orden_id):
        raise NotImplementedError

    def cancelar_orden(self, orden_id=None):
        """Opcional: liberar recursos del lado del proveedor
        (por ejemplo, la caja de MP) al cancelar/timeoutear.
        Los providers que no lo necesiten pueden ignorarlo."""
        pass
