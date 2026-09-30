"""Esquemas de datos del Fin de Semana de Asaltos a la Capital del Clan."""

from datetime import datetime, timezone

from pydantic import BaseModel


def _parsear_fecha_coc(valor: str | None) -> datetime | None:
    """Convierte una fecha en el formato de Supercell a datetime con zona UTC."""
    if not valor:
        return None
    return datetime.strptime(valor, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)


class MiembroAsaltoOut(BaseModel):
    """Participación de un miembro propio en el fin de semana de asaltos."""

    tag: str
    nombre: str
    ataques_usados: int
    limite_ataques: int
    ataques_bono: int
    oro_capital_saqueado: int

    @classmethod
    def _desde_api(cls, datos: dict) -> "MiembroAsaltoOut":
        return cls(
            tag=datos["tag"],
            nombre=datos["name"],
            ataques_usados=datos["attacks"],
            limite_ataques=datos["attackLimit"],
            ataques_bono=datos["bonusAttackLimit"],
            oro_capital_saqueado=datos["capitalResourcesLooted"],
        )


class AtaqueDistritoOut(BaseModel):
    """Un ataque individual contra un distrito, propio o rival."""

    atacante_tag: str
    atacante_nombre: str
    estrellas: int
    destruccion: int

    @classmethod
    def _desde_api(cls, datos: dict) -> "AtaqueDistritoOut":
        atacante = datos.get("attacker", {})
        return cls(
            atacante_tag=atacante.get("tag", ""),
            atacante_nombre=atacante.get("name", ""),
            estrellas=datos["stars"],
            destruccion=datos["destructionPercent"],
        )


class DistritoOut(BaseModel):
    """Un distrito de una capital, propia o rival, dentro de un asalto."""

    id: int
    nombre: str
    nivel: int
    destruccion: int
    estrellas: int
    ataques_usados: int
    saqueado: int
    ataques: list[AtaqueDistritoOut]

    @classmethod
    def _desde_api(cls, datos: dict) -> "DistritoOut":
        return cls(
            id=datos["id"],
            nombre=datos["name"],
            nivel=datos["districtHallLevel"],
            destruccion=datos["destructionPercent"],
            estrellas=datos["stars"],
            ataques_usados=datos["attackCount"],
            saqueado=datos["totalLooted"],
            # A veces llega vacía aunque hubo ataques, por datos incompletos
            # del lado de Supercell; no es un error de nuestro parseo.
            ataques=[AtaqueDistritoOut._desde_api(a) for a in datos.get("attacks", [])],
        )


class RegistroCapitalOut(BaseModel):
    """Una entrada del registro de asaltos, propios o recibidos, contra un clan."""

    clan_tag: str
    clan_nombre: str
    clan_nivel: int
    ataques_usados: int
    distritos_totales: int
    distritos_destruidos: int
    distritos: list[DistritoOut]

    @classmethod
    def _desde_api(cls, datos: dict, clave_clan: str) -> "RegistroCapitalOut":
        # clave_clan es "defender" dentro de attackLog (el clan que atacamos)
        # y "attacker" dentro de defenseLog (el clan que nos atacó a nosotros).
        clan = datos.get(clave_clan, {})
        return cls(
            clan_tag=clan.get("tag", ""),
            clan_nombre=clan.get("name", ""),
            # Sin confirmar de forma independiente si este sub-objeto usa
            # "clanLevel", como el resto de la API, o un nombre distinto;
            # si sale en 0 de forma sistemática, revisar este campo primero.
            clan_nivel=clan.get("clanLevel", 0),
            ataques_usados=datos["attackCount"],
            distritos_totales=datos["districtCount"],
            distritos_destruidos=datos["districtsDestroyed"],
            distritos=[DistritoOut._desde_api(d) for d in datos.get("districts", [])],
        )


class AsaltoOut(BaseModel):
    """Un fin de semana de asaltos completo, tal como lo entrega Supercell."""

    estado: str
    inicio: datetime | None
    fin: datetime | None
    oro_capital_total: int
    asaltos_completados: int
    ataques_totales: int
    distritos_rivales_destruidos: int
    recompensa_ofensiva: int
    recompensa_defensiva: int
    miembros: list[MiembroAsaltoOut]
    # Distritos rivales que atacamos nosotros.
    ataques_realizados: list[RegistroCapitalOut]
    # Nuestros propios distritos que atacaron otros clanes.
    ataques_recibidos: list[RegistroCapitalOut]

    @classmethod
    def desde_api(cls, datos: dict) -> "AsaltoOut":
        return cls(
            estado=datos["state"],
            inicio=_parsear_fecha_coc(datos.get("startTime")),
            fin=_parsear_fecha_coc(datos.get("endTime")),
            oro_capital_total=datos["capitalTotalLoot"],
            asaltos_completados=datos["raidsCompleted"],
            ataques_totales=datos["totalAttacks"],
            distritos_rivales_destruidos=datos["enemyDistrictsDestroyed"],
            recompensa_ofensiva=datos["offensiveReward"],
            recompensa_defensiva=datos["defensiveReward"],
            miembros=[MiembroAsaltoOut._desde_api(m) for m in datos.get("members", [])],
            ataques_realizados=[
                RegistroCapitalOut._desde_api(a, "defender") for a in datos.get("attackLog", [])
            ],
            ataques_recibidos=[
                RegistroCapitalOut._desde_api(a, "attacker") for a in datos.get("defenseLog", [])
            ],
        )

    @classmethod
    def lista_desde_api(cls, items: list[dict]) -> list["AsaltoOut"]:
        return [cls.desde_api(item) for item in items]