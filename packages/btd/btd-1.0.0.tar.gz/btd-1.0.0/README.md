# BTD File Tools

BTD é uma biblioteca leve em Python para salvar e carregar arquivos com um formato binário personalizado usando a extensão `.btd`.

BTD is a lightweight Python library to save and load files using a custom binary format with the `.btd` extension.

---

## 📌 PT-BR — Ferramentas de Arquivo BTD

### Funções disponíveis

- save_btd(caminho: str, dados: str | bytes)
  Salva os dados fornecidos (texto ou bytes) em um arquivo `.btd`.

- load_btd(caminho: str) -> str | bytes
  Lê um arquivo `.btd` e retorna seu conteúdo original (texto ou bytes).

- is_btd(caminho: str) -> bool
  Verifica se o arquivo possui a extensão `.btd`.

---

## 📌 EN — BTD File Tools

### Available functions

- **save_btd(path: str, data: str | bytes)**  
  Saves the given data (text or bytes) to a `.btd` file.

- **load_btd(path: str) -> str | bytes**  
  Loads a `.btd` file and returns its original content (text or bytes).

- **is_btd(path: str) -> bool**  
  Checks if a file has the `.btd` extension.

---

## ✅ Requisitos / Requirements

- Python 3.7 ou superior / Python 3.7 or higher

---

## 📦 Instalação / Installation

Quando publicado no PyPI:

```bash
pip install btd

Ainda não está disponível no PyPI.
Not available on PyPI yet.