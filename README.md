# Sistema de Achados e Perdidos

<p align="center">
  <img src="img/achados-e-perdidos-github-readme.jpg" alt="Achados e Perdidos" width="800">
</p>

Sistema fullstack completo de gerenciamento de itens perdidos e encontrados, desenvolvido com FastAPI no backend e React no frontend, seguindo as melhores práticas de desenvolvimento.

## Sobre o Projeto

O sistema de Achados e Perdidos permite o registro, busca e devolução de itens perdidos, conectando pessoas que encontraram objetos com seus proprietários legítimos.

Este é um projeto fullstack desenvolvido pelo grupo **Ditko.br** para a disciplina de **Frameworks Full Stack**, ministrada pelo professor **Giovani Bontempo** na Faculdade Impacta. O projeto utiliza FastAPI para o backend e React para o frontend, demonstrando a integração completa entre as duas tecnologias.

## Modelo de Dados

O sistema é baseado no seguinte diagrama entidade-relacionamento:

![Diagrama ER - Achados e Perdidos](Diagrama-Achados-e-Perdidos.jpeg)

### Entidades Principais

#### Item

Representa os objetos perdidos/encontrados no sistema.

- **id**: Identificador único
- **nome**: Nome/descrição breve do item
- **categoria**: Classificação do item (eletrônicos, documentos, etc.)
- **data_encontro**: Data em que o item foi encontrado
- **descricao**: Descrição detalhada do item
- **status**: Status atual (disponível, devolvido, etc.)

#### Local

Representa os locais onde os itens foram encontrados.

- **id**: Identificador único
- **tipo**: Tipo do local (sala, corredor, etc.)
- **descricao**: Descrição específica do local
- **bairro**: Bairro onde o local está situado

#### Responsável

Pessoa responsável por registrar o item encontrado.

- **id**: Identificador único
- **nome**: Nome completo
- **cargo**: Cargo/função do responsável
- **telefone**: Telefone para contato
- **ativo**: Status de atividade no sistema

#### Reclamante

Pessoa que reivindica a devolução do item.

- **id**: Identificador único
- **nome**: Nome completo
- **documento**: Documento de identificação
- **telefone**: Telefone para contato

#### Devolução

Registro da devolução de um item ao reclamante.

- **id**: Identificador único
- **data_devolucao**: Data em que o item foi devolvido
- **observacao**: Observações sobre a devolução

### Relacionamentos

- **Item - Local**: Um item é encontrado em um local (N:1)
- **Item - Responsável**: Um item é registrado por um responsável (N:1)
- **Item - Devolução**: Um item pode ter uma devolução (1:0..1)
- **Devolução - Reclamante**: Uma devolução é retirada por um reclamante (N:1)

## Tecnologias Utilizadas

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=python&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white)

- **FastAPI**: Framework web moderno e rápido para construção de APIs REST
- **Python 3.x**: Linguagem de programação principal
- **Poetry**: Gerenciador de dependências e ambientes virtuais
- **SQLAlchemy**: ORM para interação com banco de dados
- **Pydantic**: Validação de dados e serialização

### Frontend

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

- **React**: Biblioteca JavaScript para construção de interfaces de usuário
- **JavaScript/TypeScript**: Linguagens de programação para o frontend
- **HTML5/CSS3**: Marcação e estilização das páginas

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Poetry

### Passos para instalação

Clone o repositório:
```bash
git clone https://github.com/impacta-gb/ap1-backend-fastapi-ditko-br.git
cd LostFoundFullstack
```

Instale as dependências usando Poetry:
```bash
poetry install
```

Ative o ambiente virtual:
```bash
poetry shell
```

Execute o servidor de desenvolvimento:
```bash
poetry run uvicorn fast_zero.app:app --reload
```

Acesse a documentação interativa da API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Autores

### Grupo Ditko.br

Projeto desenvolvido para a disciplina de Frameworks Full Stack:

**Professor:** Giovani Bontempo

**Instituição:** Faculdade Impacta

**Integrantes:**

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/Ryanditko">
        <img src="https://github.com/Ryanditko.png" width="100px;" alt="Ryan Rodrigues Cordeiro"/><br>
        <sub><b>Ryan Rodrigues Cordeiro</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Felipewv93">
        <img src="https://github.com/Felipewv93.png" width="100px;" alt="Felipe Wilson Viana"/><br>
        <sub><b>Felipe Wilson Viana</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Iago-RM">
        <img src="https://github.com/Iago-RM.png" width="100px;" alt="Iago Rozales"/><br>
        <sub><b>Iago Rozales</b></sub>
      </a>
    </td>
  </tr>
</table>

## Contato

Para mais informações sobre o projeto, entre em contato através do repositório no GitHub.

---

Projeto Acadêmico - Frameworks Full Stack | Prof. Giovani Bontempo | Faculdade Impacta
