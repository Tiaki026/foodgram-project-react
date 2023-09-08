


class M2MAddDelMixin:
    def add_to_m2m(self, instance, objects):
        for obj in objects:
            instance.m2m_field.add(obj)

    def remove_from_m2m(self, instance, objects):
        for obj in objects:
            instance.m2m_field.remove(obj)