import boto3
import pytest
from botocore.stub import Stubber

from estado import EstadoNoDisponible, RegistroMinuto, RepositorioDynamo

TABLA = "reto3-estado"


@pytest.fixture
def cliente():
    c = boto3.client("dynamodb", region_name="us-east-2",
                     aws_access_key_id="x", aws_secret_access_key="x")
    with Stubber(c) as s:
        yield c, s


def test_leer_minutos(cliente):
    c, s = cliente
    s.add_response("batch_get_item", {"Responses": {TABLA: [
        {"pk": {"S": "MIN#10"}, "nivel": {"N": "2"}, "errores": {"N": "7"}},
    ]}, "UnprocessedKeys": {}}, {"RequestItems": {TABLA: {
        "Keys": [{"pk": {"S": "MIN#10"}}, {"pk": {"S": "MIN#9"}}], "ConsistentRead": True}}})
    repo = RepositorioDynamo(TABLA, cliente=c)
    assert repo.leer_minutos([10, 9]) == {10: RegistroMinuto(nivel=2, errores=7)}


def test_fijar_nivel_gana(cliente):
    c, s = cliente
    s.add_response("update_item", {})
    assert RepositorioDynamo(TABLA, cliente=c, reloj=lambda: 0).fijar_nivel(10, 3) == (3, True)


def test_fijar_nivel_pierde_la_carrera_y_lee_al_ganador(cliente):
    c, s = cliente
    s.add_client_error("update_item", service_error_code="ConditionalCheckFailedException")
    s.add_response("get_item", {"Item": {"pk": {"S": "MIN#10"}, "nivel": {"N": "2"}}})
    assert RepositorioDynamo(TABLA, cliente=c, reloj=lambda: 0).fijar_nivel(10, 3) == (2, False)


def test_error_de_servicio_es_estado_no_disponible(cliente):
    c, s = cliente
    s.add_client_error("update_item", service_error_code="ProvisionedThroughputExceededException")
    with pytest.raises(EstadoNoDisponible):
        RepositorioDynamo(TABLA, cliente=c, reloj=lambda: 0).registrar_resultado(10, True)


def test_claves_sin_procesar_es_estado_no_disponible(cliente):
    c, s = cliente
    s.add_response("batch_get_item", {"Responses": {TABLA: []},
                                      "UnprocessedKeys": {TABLA: {"Keys": [{"pk": {"S": "MIN#10"}}]}}})
    with pytest.raises(EstadoNoDisponible):
        RepositorioDynamo(TABLA, cliente=c).leer_minutos([10])
