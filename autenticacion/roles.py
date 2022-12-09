from django.contrib.auth.models import Group


def create_a_role(name):
    role, _ = Group.objects.get_or_create(name=name)
    return role


class ROLES:
    APP_ROLES = {
        "ADMINISTRADOR": create_a_role(name="ADMINISTRADOR"),
        "MEDICO": create_a_role(name="MEDICO"),
        "PACIENTE": create_a_role(name="PACIENTE"),
        "SUCURSAL": create_a_role(name="SUCURSAL"),
		"GRUPOEMPRESARIAL" : create_a_role(name="GRUPOEMPRESARIAL"),
		"FARMACIA" : create_a_role(name="FARMACIA"),
    }

    @staticmethod
    def set_role(user, role):
        ROLES.APP_ROLES[role].user_set.add(user)

