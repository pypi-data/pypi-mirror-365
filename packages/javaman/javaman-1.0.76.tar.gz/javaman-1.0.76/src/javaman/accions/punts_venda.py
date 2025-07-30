from javaman.connexio import JManCon

class PuntsVenda:
    __slots__ = '_con'

    _url_get_punt_venda = '/punts_venda/{punt_venda_id}'

    def __init__(self, con: JManCon):
        self._con = con

    def get_punt_venda(self, punt_venda_id: int):
        res = self._con.get(url=self._url_get_punt_venda.format(punt_venda_id=str(punt_venda_id)))
        return res.json()