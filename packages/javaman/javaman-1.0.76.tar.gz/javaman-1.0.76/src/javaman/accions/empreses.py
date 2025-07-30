from javaman.connexio import JManCon


class Empreses:
    __slots__ = '_con'

    _url_get_empresa = '/empreses?empresa_id={empresa_id}'

    def __init__(self, con: JManCon):
        self._con = con

    def get_empresa_by_id(self, p_empresa_id: int):
        tmp_url = self._url_get_empresa.format(empresa_id=p_empresa_id)
        req = self._con.get(url=tmp_url)
        return req.json()
