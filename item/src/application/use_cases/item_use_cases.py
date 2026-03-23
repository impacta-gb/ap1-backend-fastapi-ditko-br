from typing import List, Optional
from datetime import datetime
from item.src.domain.entities.item import Item
from item.src.domain.repositories.item_repository import ItemRepository


class CreateItemUseCase:
    """Caso de uso para criar um novo item"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, item: Item) -> Item:
        """
        Executa a criação de um novo item com validações de negócio.
        
        Regras de negócio:
        - Status inicial deve ser sempre 'disponivel'
        - Data de encontro não pode ser futura
        - IDs de local e responsável devem ser válidos
        """
        # Garante que novo item sempre começa como disponível
        item.status = 'disponivel'
        
        # Validação: data de encontro não pode ser futura
        if item.data_encontro > datetime.now():
            raise ValueError("Data de encontro não pode ser no futuro")
        
        # Validação: IDs devem ser positivos
        if item.local_id <= 0:
            raise ValueError("ID do local deve ser maior que zero")
        
        if item.responsavel_id <= 0:
            raise ValueError("ID do responsável deve ser maior que zero")

        # Regra: só cria Item se local e responsável existirem no módulo Item
        # via projeções sincronizadas por eventos Kafka.
        if not await self.repository.exists_local(item.local_id):
            raise ValueError(
                f"Local com ID {item.local_id} não encontrado no módulo Item. "
                "Aguarde sincronização do evento de local."
            )

        if not await self.repository.exists_responsavel(item.responsavel_id):
            raise ValueError(
                f"Responsável com ID {item.responsavel_id} não encontrado no módulo Item. "
                "Aguarde sincronização do evento de responsável."
            )

        if not await self.repository.exists_responsavel_ativo(item.responsavel_id):
            raise ValueError(
                f"Responsável com ID {item.responsavel_id} está inativo e não pode ser usado para registrar item."
            )
        
        return await self.repository.create(item)


class GetItemByIdUseCase:
    """Caso de uso para buscar um item por ID"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, item_id: int) -> Optional[Item]:
        """Executa a busca de um item por ID"""
        if item_id <= 0:
            raise ValueError("ID do item deve ser maior que zero")
        
        return await self.repository.get_by_id(item_id)


class GetAllItemsUseCase:
    """Caso de uso para listar todos os itens"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[Item]:
        """Executa a listagem de todos os itens com validação de paginação"""
        if skip < 0:
            raise ValueError("Skip não pode ser negativo")
        
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit deve estar entre 1 e 1000")
        
        return await self.repository.get_all(skip, limit)


class UpdateItemUseCase:
    """Caso de uso para atualizar um item"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, item_id: int, item: Item) -> Optional[Item]:
        """
        Executa a atualização de um item com validações de negócio.
        
        Regras de negócio:
        - Não pode mudar status para 'devolvido' diretamente (use MarcarComoDevolvido)
        - Item deve existir
        """
        # Busca o item atual para comparar
        existing_item = await self.repository.get_by_id(item_id)
        
        if not existing_item:
            return None
        
        # Regra de negócio: Não pode marcar como devolvido diretamente pelo update
        if existing_item.status != 'devolvido' and item.status == 'devolvido':
            raise ValueError(
                "Para marcar um item como devolvido, use o processo de devolução apropriado"
            )
        
        # Validação: data de encontro não pode ser futura
        if item.data_encontro > datetime.now():
            raise ValueError("Data de encontro não pode ser no futuro")
        
        return await self.repository.update(item_id, item)


class DeleteItemUseCase:
    """Caso de uso para deletar um item"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, item_id: int) -> bool:
        """
        Executa a remoção de um item com validações de negócio.
        
        Regras de negócio:
        - Não pode deletar itens já devolvidos (manter histórico)
        """
        # Busca o item para verificar o status
        item = await self.repository.get_by_id(item_id)
        
        if not item:
            return False
        
        # Regra de negócio: Não pode deletar item devolvido (preservar histórico)
        if item.status == 'devolvido':
            raise ValueError(
                "Não é permitido deletar itens já devolvidos. "
                "O histórico de devoluções deve ser preservado."
            )
        
        return await self.repository.delete(item_id)


class GetItemsByCategoriaUseCase:
    """Caso de uso para buscar itens por categoria"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, categoria: str) -> List[Item]:
        """Executa a busca de itens por categoria"""
        if not categoria or len(categoria.strip()) == 0:
            raise ValueError("Categoria não pode estar vazia")
        
        return await self.repository.get_by_categoria(categoria)


class GetItemsByStatusUseCase:
    """Caso de uso para buscar itens por status"""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
    
    async def execute(self, status: str) -> List[Item]:
        """Executa a busca de itens por status com validação"""
        # Normaliza e valida o status
        status_normalizado = status.lower().replace('í', 'i').replace('é', 'e').replace('á', 'a')
        
        status_validos = ['disponivel', 'devolvido', 'em_analise']
        if status_normalizado not in status_validos:
            raise ValueError(
                f"Status '{status}' inválido. "
                f"Status válidos: {', '.join(status_validos)}"
            )
        
        return await self.repository.get_by_status(status)
