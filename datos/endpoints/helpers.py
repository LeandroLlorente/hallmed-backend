from multiprocessing.dummy import Array
from operator import concat
from django.http import QueryDict
from django.http.response import JsonResponse
from rest_framework import status


def ifDo(expresion, resultTrue, resultFalse):
    if expresion:
        return resultTrue
    else:
        return resultFalse


def isEmpty(object):
    return object is None


def ifEmptyGet(object, result=""):
    if isEmpty(object):
        return result
    return object


def unir(separador: str, *argumentos) -> str:
    s = ""
    for item in argumentos:
        if s == "":
            s = str(ifEmptyGet(item))
        else:
            s = concat(s, ifDo(isEmpty(item), "", concat(separador, str(item))))
    return s


def pares(argumento: str) -> str:
    return unir("", "(", str(argumento), ")")


def str2time(fecha, formato="%d/%m/%Y"):
    return fecha.strftime(formato)


def fullname(paciente):
    return unir(" ", paciente.nombre, paciente.apellidos)


def calc_compensacion(precio, valor):
    return ((precio * valor) / 100).__round__(2)


def handle_error(e: Exception):
    s = f"{str(type(e))} ( {str(e)} )"
    print("<error>",s)
    return JsonResponse({"error": s}, status=status.HTTP_400_BAD_REQUEST)
