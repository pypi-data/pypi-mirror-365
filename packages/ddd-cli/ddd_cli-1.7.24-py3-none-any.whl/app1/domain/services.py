"""
Los servicios en DDD son responsables de manejar la lógica de negocio 
y las operaciones CRUD relacionadas con una entidad específica. 
Este servicio proporciona métodos para listar, contar, crear, recuperar, actualizar y eliminar instancias de la entidad entity1. 
Cada método maneja la validación necesaria y utiliza un repositorio para interactuar con la persistencia de datos.
son utiles para:
- Centralizar la lógica de negocio relacionada con una entidad.
- Facilitar la reutilización de código en diferentes partes de la aplicación.
- Proporcionar una interfaz clara para interactuar con las entidades.
- Facilitar la implementación de patrones como CQRS (Command Query Responsibility Segregation).
- Permitir la separación de preocupaciones entre la lógica de negocio y la persistencia de datos.
- Facilitar la implementación de pruebas unitarias y de integración.
- Facilitar la gestión de transacciones y la consistencia de datos.
- Permitir la implementación de reglas de negocio complejas que pueden involucrar múltiples entidades o servicios.
- Facilitar la implementación de patrones de diseño como el patrón de servicio, unidad de trabajo, repositorio, etc.
- Proporcionar una interfaz coherente para interactuar con diferentes tipos de almacenamiento de datos (por ejemplo, bases de datos, servicios web, etc.).
"""

from typing import List, Optional

# importa las entidades utilizadas aqui
from .entities import Entity1Entity
from ..infrastructure.entity1_repository import Entity1Repository

"""
Servicio para manejar las operaciones CRUD relacionadas con entity1.

Métodos disponibles:
    - list_entity1: Lista todas las instancias de entity1.
    - count_all_entity1: Cuenta todas las instancias de entity1.
    - create_entity1: Crea una nueva instancia de entity1.
    - retrieve_entity1: Recupera una instancia de entity1 por ID.
    - update_entity1: Actualiza una instancia existente de entity1.
    - delete_entity1: Elimina una instancia de entity1.
"""

#Si necesitas mantener un estado de lista de entidades
entity1_list = []   

def list_entity1(repository: Entity1Repository, filters: Optional[dict] = None) -> List[dict]:
    """
    Lista instancias de entity1.

    :param repository: Repositorio que maneja la persistencia de entity1.
    :return: Lista de la entidad.
    :raises ValueError: Si las reglas de negocio no se cumplen.
    """

    entity_list = repository.get_all(filters=filters)

    return [entity.to_dict() for entity in entity_list]  


def count_all_entity1(repository: Entity1Repository, filters: Optional[dict] = None) -> int:
    """
    Cuenta todas las instancias de entity1.

    :param repository: Repositorio que maneja la persistencia de entity1.
    :param filters: Filtros opcionales para la consulta.
    :return: Número total de instancias.
    """
    return repository.count_all(filters=filters)


def create_entity1(repository: Entity1Repository, data, external_id: Optional[int], externals: Optional[List[int]], adicionalData=None) -> dict:
    """
    Crea una nueva instancia de entity1.

    :param repository: Repositorio que maneja la persistencia de entity1.
    :param data: Diccionario o DTO con los datos necesarios para crear la instancia.
    :param external_id: ID del padre si es necesario (opcional).
    :param externals: Lista de IDs de entidades relacionadas (opcional).
    :param adicionalData: Datos adicionales a incluir en la creación.
    :return: La entidad creada.
    :raises ValueError: Si las reglas de negocio no se cumplen.
    """
    # Validación de reglas de negocio (opcional)
    if repository.exists_by_field(field_name="attributeName", value=data['attributeName']):
        raise ValueError("An instance with this attributeName already exists")

    #crear y validar la entidad
    entity = Entity1Entity.from_dict(data)
    entity.validate()

    # Guardar en el repositorio
    saved_entity = repository.create(entity=entity, external_id=external_id, externals=externals, adicionalData=adicionalData)

    return saved_entity.to_dict()


def retrieve_entity1(repository: Entity1Repository, entity_id: int) -> dict:
    """
    Recupera una instancia de entity1 por su ID.

    :param repository: Repositorio que maneja la persistencia de entity1.
    :param entity_id: ID de la instancia a recuperar.
    :return: La entidad recuperada.
    :raises ValueError: Si no se encuentra la instancia.
    """
    entity = repository.get_by_id(id=entity_id)
    if not entity:
        raise ValueError(f"No entity1 found with ID {entity_id}")

    return entity.to_dict()


def update_entity1(repository: Entity1Repository, entity_id: int, data, external_id: Optional[int]=None, externals: Optional[List[int]]=None, adicionalData=None) -> dict:
    """
    Actualiza una instancia existente de entity1.

    :param repository: Repositorio que maneja la persistencia de entity1.
    :param entity_id: ID de la instancia a actualizar.
    :param data: Diccionario o DTO con los datos a actualizar.
    :param external_id: ID del padre si es necesario (opcional).
    :param externals: Lista de IDs de entidades relacionadas (opcional).
    :param adicionalData: Datos adicionales a incluir en la actualización.
    :return: La entidad actualizada.
    :raises ValueError: Si no se encuentra la instancia o las reglas de negocio no se cumplen.
    """
    # Recuperar la entidad
    entity = repository.get_by_id(id=entity_id)
    if not entity:
        raise ValueError(f"No entity1 found with ID {entity_id}")

    # actualizar la instancia y validar
    entity.update(data)     
    entity.validate()   

    # Guardar en el repositorio
    updated_entity = repository.save(entity=entity, external_id=external_id, externals=externals, adicionalData=adicionalData)

    return updated_entity.to_dict()


def delete_entity1(repository: Entity1Repository, entity_id: int) -> bool:
    """
    Elimina una instancia de entity1.

    :param repository: Repositorio que maneja la persistencia de entity1.
    :param entity_id: ID de la instancia a eliminar.
    :return: True/False (depende del exito de la operacion)
    :raises ValueError: Si no se encuentra la instancia.
    """
    # Verifica si la entidad existe
    if not repository.exists_by_field(field_name="id", value=entity_id):
        raise ValueError(f"No entity1 found with ID {entity_id}")

    # Eliminación en el repositorio
    repository.delete(id=entity_id)

    return True
